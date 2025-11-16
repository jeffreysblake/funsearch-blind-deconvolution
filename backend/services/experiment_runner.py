"""Experiment runner service that executes FunSearch experiments."""

import asyncio
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import UUID

# Add implementation directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "implementation"))

from implementation import code_manipulation, config as funsearch_config
from implementation import evaluator as fs_evaluator
from implementation import funsearch, programs_database, sampler

from backend.api import websocket
from backend.models import Experiment, ExperimentStatus, get_db


class MockLLM(sampler.LLM):
    """Mock LLM implementation for testing without LM Studio."""

    def __init__(self, samples_per_prompt: int, templates: Optional[list] = None):
        super().__init__(samples_per_prompt)
        self.templates = templates or self._default_templates()
        self.iteration = 0

    def _default_templates(self) -> list[str]:
        """Default code templates for evolution."""
        return [
            # Mathematical operations
            "    return value / weight if weight > 0 else 0.0",
            "    return value / (weight + 1e-6)",
            "    return (value ** 2) / weight if weight > 0 else 0.0",
            "    return value / (weight ** 0.5) if weight > 0 else 0.0",
            # Consider capacity
            "    return (value / weight) * (1.0 + capacity / 100.0) if weight > 0 else 0.0",
            "    ratio = value / weight if weight > 0 else 0.0\n"
            "    return ratio * (capacity / (weight + capacity))",
            # Absolute value considerations
            "    base = value / weight if weight > 0 else 0.0\n"
            "    return base + value * 0.01",
            # Complex heuristics
            "    if weight > capacity * 0.5:\n"
            "        return value * 0.5\n"
            "    return value / weight if weight > 0 else 0.0",
            # Fibonacci-like for number sequence
            "    if n <= 1:\n        return n\n"
            "    return int(1.618 ** n / 2.236)",  # Golden ratio approximation
            "    if n <= 2:\n        return 1\n"
            "    # Approximation\n    return int((n * n) * 0.2)",
        ]

    def _draw_sample(self, prompt: str) -> str:
        """Generate code sample from templates."""
        # Rotate through templates with some randomness
        import random

        self.iteration += 1

        # Mix templates to create variations
        if random.random() < 0.3:
            # Combine two templates occasionally
            t1 = random.choice(self.templates)
            return t1
        else:
            # Use single template
            return random.choice(self.templates)


class ExperimentRunner:
    """Runs FunSearch experiments and reports progress."""

    def __init__(self, experiment_id: UUID):
        self.experiment_id = str(experiment_id)
        self.experiment: Optional[Experiment] = None
        self.config: Optional[Dict[str, Any]] = None

    async def run(self):
        """Execute the experiment."""
        try:
            # Load experiment from database
            await self._load_experiment()

            # Update status to running
            await self._update_status(ExperimentStatus.RUNNING)
            await self._broadcast_log("info", "Experiment started")

            # Load specification
            spec_path = Path(self.experiment.specification_file)
            if not spec_path.exists():
                raise FileNotFoundError(f"Specification not found: {spec_path}")

            specification = spec_path.read_text()

            # Configure FunSearch
            fs_config = self._build_funsearch_config()

            # Run experiment
            await self._run_funsearch(specification, fs_config)

            # Mark as completed
            await self._update_status(ExperimentStatus.COMPLETED)
            await self._broadcast_log("info", "Experiment completed successfully")

        except Exception as e:
            await self._update_status(ExperimentStatus.FAILED, error=str(e))
            await self._broadcast_log("error", f"Experiment failed: {e}")
            raise

    def _build_funsearch_config(self) -> funsearch_config.Config:
        """Build FunSearch config from experiment settings."""
        exp_config = self.experiment.config

        # Extract funsearch-specific settings
        fs_settings = exp_config.get("funsearch", {})

        programs_db_config = funsearch_config.ProgramsDatabaseConfig(
            functions_per_prompt=fs_settings.get("functions_per_prompt", 2),
            num_islands=fs_settings.get("num_islands", 10),
            reset_period=fs_settings.get("reset_period", 4 * 60 * 60),
            cluster_sampling_temperature_init=fs_settings.get(
                "cluster_sampling_temperature_init", 0.1
            ),
            cluster_sampling_temperature_period=fs_settings.get(
                "cluster_sampling_temperature_period", 30000
            ),
        )

        return funsearch_config.Config(
            programs_database=programs_db_config,
            num_samplers=fs_settings.get("num_samplers", 1),  # Single-threaded for now
            num_evaluators=fs_settings.get("num_evaluators", 1),
            samples_per_prompt=fs_settings.get("samples_per_prompt", 4),
        )

    async def _run_funsearch(
        self, specification: str, config: funsearch_config.Config
    ):
        """Run the FunSearch algorithm."""
        # Extract function names
        function_to_evolve, function_to_run = funsearch._extract_function_names(
            specification
        )

        # Create template
        template = code_manipulation.text_to_program(specification)

        # Create programs database
        database = programs_database.ProgramsDatabase(
            config.programs_database, template, function_to_evolve
        )

        # Create evaluators
        evaluators = []
        inputs = []  # No inputs needed for our examples
        for _ in range(config.num_evaluators):
            evaluators.append(
                fs_evaluator.Evaluator(
                    database, template, function_to_evolve, function_to_run, inputs
                )
            )

        # Evaluate initial implementation
        initial = template.get_function(function_to_evolve).body
        evaluators[0].analyse(initial, island_id=None, version_generated=None)

        # Broadcast initial metrics
        await self._broadcast_metrics(
            iteration=0, best_score=database._best_score_per_island[0]
        )

        # Create samplers with mock LLM
        samplers_list = []
        for _ in range(config.num_samplers):
            s = sampler.Sampler(database, evaluators, config.samples_per_prompt)
            # Replace LLM with our mock
            s._llm = MockLLM(config.samples_per_prompt)
            samplers_list.append(s)

        # Run sampling iterations
        max_iterations = self.experiment.config.get("execution", {}).get(
            "max_iterations", 1000
        )

        for iteration in range(max_iterations):
            # Single iteration of sampling
            for s in samplers_list:
                prompt = database.get_prompt()
                samples = s._llm.draw_samples(prompt.code)

                for sample in samples:
                    # Pick an evaluator
                    chosen_evaluator = evaluators[0]
                    chosen_evaluator.analyse(
                        sample, prompt.island_id, prompt.version_generated
                    )

            # Broadcast progress every 10 iterations
            if iteration % 10 == 0:
                best_score = max(database._best_score_per_island)
                await self._broadcast_metrics(iteration=iteration, best_score=best_score)
                await self._broadcast_log(
                    "info", f"Iteration {iteration}/{max_iterations}, best score: {best_score:.2f}"
                )

            # Check for early stopping
            if iteration % 100 == 0:
                # Save checkpoint
                await self._save_checkpoint(iteration, database)

            # Yield control to event loop
            await asyncio.sleep(0.01)

    async def _load_experiment(self):
        """Load experiment from database."""
        db = next(get_db())
        self.experiment = (
            db.query(Experiment).filter(Experiment.id == self.experiment_id).first()
        )
        if not self.experiment:
            raise ValueError(f"Experiment {self.experiment_id} not found")

    async def _update_status(
        self, status: ExperimentStatus, error: Optional[str] = None
    ):
        """Update experiment status in database."""
        db = next(get_db())
        experiment = (
            db.query(Experiment).filter(Experiment.id == self.experiment_id).first()
        )
        if experiment:
            old_status = experiment.status
            experiment.status = status
            if error:
                experiment.error_message = error
            if status == ExperimentStatus.RUNNING:
                experiment.started_at = datetime.utcnow()
            elif status in [ExperimentStatus.COMPLETED, ExperimentStatus.FAILED]:
                experiment.completed_at = datetime.utcnow()
            db.commit()

            # Broadcast status change
            await websocket.broadcast_status_change(
                self.experiment_id, old_status.value, status.value
            )

    async def _broadcast_metrics(self, iteration: int, best_score: float):
        """Broadcast metrics update via WebSocket."""
        await websocket.broadcast_metric_update(
            self.experiment_id,
            {
                "iteration": iteration,
                "best_score": best_score,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    async def _broadcast_log(self, level: str, message: str):
        """Broadcast log message via WebSocket."""
        await websocket.broadcast_log(self.experiment_id, level, message)

    async def _save_checkpoint(self, iteration: int, database):
        """Save experiment checkpoint."""
        db = next(get_db())
        experiment = (
            db.query(Experiment).filter(Experiment.id == self.experiment_id).first()
        )
        if experiment:
            experiment.iterations_completed = iteration
            experiment.best_score = max(database._best_score_per_island)
            db.commit()


async def run_experiment(experiment_id: UUID):
    """Run an experiment asynchronously."""
    runner = ExperimentRunner(experiment_id)
    await runner.run()

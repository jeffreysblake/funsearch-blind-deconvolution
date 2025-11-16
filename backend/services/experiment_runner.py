"""Experiment runner service that executes FunSearch experiments."""

import asyncio
import logging
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
from backend.core.llm.lm_studio import LMStudioSampler
from backend.core.llm.prompts import get_template_for_problem
from backend.models import Experiment, ExperimentStatus, Project, get_db

logger = logging.getLogger(__name__)

# Optional MLflow integration
try:
    import mlflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False
    logger.info("MLflow not installed, experiment tracking disabled")


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


class LMStudioLLM(sampler.LLM):
    """LLM wrapper that adapts LMStudioSampler to implementation.sampler.LLM interface."""

    def __init__(
        self,
        samples_per_prompt: int,
        lm_studio_sampler: LMStudioSampler,
        prompt_template: Optional[Any] = None,
    ):
        super().__init__(samples_per_prompt)
        self.lm_studio = lm_studio_sampler
        self.prompt_template = prompt_template

    def _draw_sample(self, prompt: str) -> str:
        """Generate code sample using LM Studio."""
        # Apply prompt template if available
        if self.prompt_template:
            formatted_prompt = self.prompt_template.format_prompt(prompt)
        else:
            formatted_prompt = prompt

        # Generate single sample
        samples = self.lm_studio.sample(formatted_prompt, num_samples=1)
        return samples[0] if samples else ""


class ExperimentRunner:
    """Runs FunSearch experiments and reports progress."""

    def __init__(self, experiment_id: UUID):
        self.experiment_id = str(experiment_id)
        self.experiment: Optional[Experiment] = None
        self.project: Optional[Project] = None
        self.config: Optional[Dict[str, Any]] = None
        self.mlflow_run = None

    async def run(self):
        """Execute the experiment."""
        try:
            # Load experiment from database
            await self._load_experiment()

            # Initialize MLflow if available
            if MLFLOW_AVAILABLE:
                self._init_mlflow()

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

            # End MLflow run
            if self.mlflow_run:
                mlflow.end_run()

        except Exception as e:
            logger.exception(f"Experiment {self.experiment_id} failed")
            await self._update_status(ExperimentStatus.FAILED, error=str(e))
            await self._broadcast_log("error", f"Experiment failed: {e}")

            # End MLflow run with failed status
            if self.mlflow_run:
                mlflow.end_run(status="FAILED")

            raise

    def _init_mlflow(self):
        """Initialize MLflow tracking."""
        try:
            mlflow_config = self.experiment.config.get("mlflow", {})
            tracking_uri = mlflow_config.get("tracking_uri", "http://localhost:7352")

            mlflow.set_tracking_uri(tracking_uri)
            mlflow.set_experiment("funsearch")

            # Start MLflow run
            mlflow.start_run(run_name=self.experiment.name)
            self.mlflow_run = mlflow.active_run()

            # Log experiment configuration
            mlflow.log_params({
                "llm_provider": self.experiment.config.get("llm", {}).get("provider"),
                "llm_model": self.experiment.config.get("llm", {}).get("model"),
                "num_islands": self.experiment.config.get("funsearch", {}).get("num_islands"),
                "samples_per_prompt": self.experiment.config.get("funsearch", {}).get("samples_per_prompt"),
                "max_iterations": self.experiment.config.get("execution", {}).get("max_iterations"),
            })

            # Save run ID to database
            db = next(get_db())
            exp = db.query(Experiment).filter(Experiment.id == self.experiment_id).first()
            if exp:
                exp.mlflow_run_id = self.mlflow_run.info.run_id
                db.commit()

            logger.info(f"✓ MLflow tracking initialized: {self.mlflow_run.info.run_id}")

        except Exception as e:
            logger.warning(f"Failed to initialize MLflow: {e}")
            self.mlflow_run = None

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

    def _create_llm(self, samples_per_prompt: int) -> sampler.LLM:
        """Create appropriate LLM based on configuration.

        Args:
            samples_per_prompt: Number of samples per prompt

        Returns:
            LLM instance (either MockLLM or LMStudioLLM)
        """
        llm_config = self.experiment.config.get("llm", {})
        provider = llm_config.get("provider", "mock")

        if provider == "lm_studio":
            try:
                # Get problem type for prompt template
                problem_type = self.project.problem_type if self.project else "general"
                prompt_template = get_template_for_problem(problem_type)

                # Create LM Studio sampler
                lm_studio = LMStudioSampler(
                    base_url=llm_config.get("base_url", "http://localhost:1234/v1"),
                    model=llm_config.get("model"),
                    temperature=llm_config.get("temperature", 1.0),
                    max_tokens=llm_config.get("max_tokens", 512),
                    timeout=llm_config.get("timeout", 30),
                )

                logger.info(f"✓ Using LM Studio: {lm_studio.model}")

                return LMStudioLLM(samples_per_prompt, lm_studio, prompt_template)

            except Exception as e:
                logger.error(f"Failed to initialize LM Studio: {e}")
                logger.warning("Falling back to mock LLM")
                return MockLLM(samples_per_prompt)

        else:
            # Use mock LLM
            logger.info("Using Mock LLM")
            return MockLLM(samples_per_prompt)

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
        initial_score = max(database._best_score_per_island)
        await self._broadcast_metrics(iteration=0, best_score=initial_score)

        if self.mlflow_run:
            mlflow.log_metric("best_score", initial_score, step=0)

        # Create samplers with appropriate LLM
        samplers_list = []
        for _ in range(config.num_samplers):
            s = sampler.Sampler(database, evaluators, config.samples_per_prompt)
            # Replace LLM with our implementation (mock or real)
            s._llm = self._create_llm(config.samples_per_prompt)
            samplers_list.append(s)

        # Log which LLM we're using
        llm_type = "LM Studio" if isinstance(samplers_list[0]._llm, LMStudioLLM) else "Mock"
        await self._broadcast_log("info", f"Using {llm_type} for code generation")

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

                # Log to MLflow
                if self.mlflow_run:
                    mlflow.log_metric("best_score", best_score, step=iteration)
                    mlflow.log_metric("iteration", iteration, step=iteration)

            # Save checkpoint every 100 iterations
            if iteration % 100 == 0:
                await self._save_checkpoint(iteration, database)

            # Yield control to event loop
            await asyncio.sleep(0.01)

        # Log final best program to MLflow
        if self.mlflow_run:
            best_island_id = max(range(len(database._best_score_per_island)),
                                key=lambda i: database._best_score_per_island[i])
            best_program = database._best_program_per_island[best_island_id]
            if best_program:
                mlflow.log_text(str(best_program), "best_program.py")

    async def _load_experiment(self):
        """Load experiment from database."""
        db = next(get_db())
        self.experiment = (
            db.query(Experiment).filter(Experiment.id == self.experiment_id).first()
        )
        if not self.experiment:
            raise ValueError(f"Experiment {self.experiment_id} not found")

        # Load project for problem type
        self.project = (
            db.query(Project).filter(Project.id == self.experiment.project_id).first()
        )

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

            # Save best program
            best_island_id = max(
                range(len(database._best_score_per_island)),
                key=lambda i: database._best_score_per_island[i]
            )
            best_program = database._best_program_per_island[best_island_id]
            if best_program:
                experiment.best_program = str(best_program)

            db.commit()


async def run_experiment(experiment_id: UUID):
    """Run an experiment asynchronously."""
    runner = ExperimentRunner(experiment_id)
    await runner.run()

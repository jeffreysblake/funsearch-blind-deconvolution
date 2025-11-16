"""Mock LLM sampler implementations for testing and development."""

import random
import re
from pathlib import Path
from typing import List, Optional

from ..interfaces import Sampler


class MockSampler(Sampler):
    """
    Simple deterministic mock LLM for testing.

    Generates plausible code variations based on simple templates.
    """

    def __init__(self, model_name: str = "mock-gpt-4"):
        self.model_name = model_name
        self.call_count = 0
        self._cache: dict[str, List[str]] = {}

    def sample(self, prompt: str, num_samples: int = 1) -> List[str]:
        """Generate mock code samples."""
        # Check cache
        cache_key = f"{prompt}:{num_samples}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        self.call_count += 1

        # Extract function name from prompt
        match = re.search(r"def (\w+)\(", prompt)
        func_name = match.group(1) if match else "unknown"

        samples = []
        for i in range(num_samples):
            sample = self._generate_variation(func_name, i)
            samples.append(sample)

        # Cache result
        self._cache[cache_key] = samples
        return samples

    def _generate_variation(self, func_name: str, seed: int) -> str:
        """Generate a plausible code variation."""
        random.seed(self.call_count * 100 + seed)

        # Templates for different problem types
        if func_name == "priority":
            # Bin packing priority function
            templates = [
                f"return item * {random.uniform(0.5, 2.0):.2f} + {random.uniform(0, 100):.1f}",
                f"return item ** {random.uniform(1.0, 2.0):.2f} - {random.uniform(0, 50):.1f}",
                f"return max(item, {random.randint(10, 90)}) * {random.uniform(0.5, 1.5):.2f}",
                f"return min(item * {random.uniform(0.8, 1.2):.2f}, {random.randint(50, 150)})",
                f"return int(item > {random.randint(30, 70)}) * {random.randint(10, 100)} + item",
            ]
            return random.choice(templates)

        elif "stopping" in func_name or "criterion" in func_name:
            # Stopping criterion
            templates = [
                f"return iteration > {random.randint(10, 100)} and psnr_delta < {random.uniform(0.001, 0.1):.3f}",
                f"return iteration >= {random.randint(20, 80)} or psnr > {random.uniform(30, 40):.1f}",
                f"return psnr_delta < {random.uniform(0.01, 0.05):.3f} and iteration > {random.randint(5, 50)}",
                f"return iteration > {random.randint(15, 60)} * psnr_delta",
            ]
            return random.choice(templates)

        else:
            # Generic function
            return f"return {random.uniform(0, 100):.2f}"

    def get_stats(self) -> dict:
        """Return mock statistics."""
        return {
            "total_calls": self.call_count,
            "total_tokens": self.call_count * 250,  # Fake token count
            "model": self.model_name,
            "cache_size": len(self._cache),
        }


class TemplateMockSampler(Sampler):
    """
    More sophisticated mock using templates for realistic code.

    Uses Jinja2 templates to generate code variations that look
    more like real LLM outputs.
    """

    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = template_dir or Path(__file__).parent / "templates"
        self.call_count = 0
        self._cache: dict[str, List[str]] = {}

        # Simple template system (without Jinja2 dependency for now)
        self.templates = {
            "bin_packing": [
                """def priority(item: float, bins: np.ndarray, capacity: float) -> float:
    if item > {threshold}:
        return item * {multiplier}
    return item + {offset}""",
                """def priority(item: float, bins: np.ndarray, capacity: float) -> float:
    weight = {weight}
    return item ** weight + {bias}""",
                """def priority(item: float, bins: np.ndarray, capacity: float) -> float:
    return max(item, {min_val}) * {scale} - {offset}""",
            ],
            "stopping_criterion": [
                """def stopping_criterion(iteration: int, psnr: float, psnr_delta: float) -> bool:
    if iteration > {max_iter}:
        return True
    if psnr_delta < {threshold}:
        return True
    return False""",
                """def stopping_criterion(iteration: int, psnr: float, psnr_delta: float) -> bool:
    return iteration > {min_iter} and psnr_delta < {delta_threshold}""",
                """def stopping_criterion(iteration: int, psnr: float, psnr_delta: float) -> bool:
    return psnr > {psnr_target} or (iteration > {iter_min} and psnr_delta < {delta_max})""",
            ],
        }

    def sample(self, prompt: str, num_samples: int = 1) -> List[str]:
        """Generate samples from templates."""
        # Check cache
        cache_key = f"{prompt}:{num_samples}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        self.call_count += 1

        # Detect problem type from prompt
        problem_type = self._detect_problem_type(prompt)

        # Get templates
        templates = self.templates.get(problem_type, [self.templates["stopping_criterion"][0]])

        # Generate variations
        samples = []
        for i in range(num_samples):
            template = random.choice(templates)
            params = self._random_params(problem_type, i)
            code = template.format(**params)
            samples.append(code)

        # Cache result
        self._cache[cache_key] = samples
        return samples

    def _detect_problem_type(self, prompt: str) -> str:
        """Detect problem type from prompt."""
        prompt_lower = prompt.lower()
        if "bin" in prompt_lower or "priority" in prompt_lower:
            return "bin_packing"
        elif "deconvolution" in prompt_lower or "stopping" in prompt_lower:
            return "stopping_criterion"
        else:
            return "stopping_criterion"  # Default

    def _random_params(self, problem_type: str, seed: int) -> dict:
        """Generate random parameters for templates."""
        random.seed(seed * 1000 + self.call_count)

        if problem_type == "bin_packing":
            return {
                "threshold": random.randint(10, 90),
                "multiplier": round(random.uniform(0.5, 2.0), 2),
                "offset": random.randint(0, 50),
                "weight": round(random.uniform(0.8, 1.5), 2),
                "bias": round(random.uniform(0, 20), 1),
                "min_val": random.randint(5, 30),
                "scale": round(random.uniform(0.8, 1.2), 2),
            }
        elif problem_type == "stopping_criterion":
            return {
                "max_iter": random.randint(50, 200),
                "threshold": round(random.uniform(0.001, 0.05), 4),
                "min_iter": random.randint(10, 50),
                "delta_threshold": round(random.uniform(0.005, 0.02), 4),
                "psnr_target": round(random.uniform(30, 40), 1),
                "iter_min": random.randint(20, 80),
                "delta_max": round(random.uniform(0.01, 0.03), 4),
            }
        else:
            return {}

    def get_stats(self) -> dict:
        """Return mock statistics."""
        return {
            "total_calls": self.call_count,
            "total_tokens": self.call_count * 300,  # Slightly more than simple mock
            "model": "template-mock",
            "cache_size": len(self._cache),
            "templates_available": sum(len(v) for v in self.templates.values()),
        }

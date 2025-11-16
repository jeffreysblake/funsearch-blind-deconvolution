# Mock Implementations for Development & Testing

## Overview

This document describes the mock implementations of external dependencies (LM Studio, Docker) to enable development and testing in environments where these services aren't available (web instances, CI/CD, etc.).

## Design Pattern: Dependency Injection

We'll use **interface-based design** with dependency injection to make implementations swappable:

```python
# Abstract interfaces (already exist in funsearch codebase)
class Sampler(ABC):
    """LLM code generation interface"""
    @abstractmethod
    def sample(self, prompt: str) -> list[str]:
        pass

class Evaluator(ABC):
    """Code evaluation interface"""
    @abstractmethod
    def evaluate(self, program: str) -> float:
        pass

# Concrete implementations
class LMStudioSampler(Sampler):
    """Real LM Studio integration"""
    pass

class MockSampler(Sampler):
    """Fake LLM for testing"""
    pass

class DockerEvaluator(Evaluator):
    """Real Docker sandboxing"""
    pass

class MockEvaluator(Evaluator):
    """In-process evaluation for testing"""
    pass
```

## Configuration-Based Switching

```yaml
# .funsearch/config.yaml

# For local development with real services
mode: "production"
llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "qwen/qwen3-vl-8b"

sandbox:
  provider: "docker"
  max_workers: 8

---

# For web instance / CI testing
mode: "mock"
llm:
  provider: "mock"
  model: "mock-gpt-4"

sandbox:
  provider: "mock"
```

## Mock LLM Implementation

### Simple Mock (Deterministic)

```python
# backend/core/mock_llm.py

import random
from typing import List
from .sampler import Sampler

class MockSampler(Sampler):
    """
    Mock LLM that generates plausible but fake code completions.
    Useful for testing the evolutionary algorithm without real LLM.
    """

    def __init__(self, model_name: str = "mock-gpt-4"):
        self.model_name = model_name
        self.call_count = 0

    def sample(self, prompt: str, num_samples: int = 1) -> List[str]:
        """
        Generate mock code samples based on patterns.
        """
        self.call_count += 1

        # Extract function name from prompt
        import re
        match = re.search(r'def (\w+)\(', prompt)
        func_name = match.group(1) if match else "priority"

        samples = []
        for i in range(num_samples):
            # Generate variations with random parameters
            sample = self._generate_variation(func_name, i)
            samples.append(sample)

        return samples

    def _generate_variation(self, func_name: str, seed: int) -> str:
        """Generate a plausible code variation"""
        random.seed(self.call_count * 100 + seed)

        # Templates for different problem types
        if func_name == "priority":
            # Bin packing priority function
            templates = [
                "return item * {a} + {b}",
                "return item ** {a} - {b}",
                "return max(item, {a}) * {b}",
                "return min(item * {a}, {b})",
                "return int(item > {a}) * {b} + item",
            ]
            template = random.choice(templates)
            return template.format(
                a=round(random.uniform(0.5, 2.0), 2),
                b=round(random.uniform(0, 100), 1)
            )

        elif func_name == "stopping_criterion":
            # Lucy-Richardson stopping criterion
            templates = [
                "return iteration > {a} and psnr_delta < {b}",
                "return iteration >= {a} or psnr > {b}",
                "return psnr_delta < {a} and iteration > {b}",
                "return iteration > {a} * psnr",
            ]
            template = random.choice(templates)
            return template.format(
                a=random.randint(5, 50),
                b=round(random.uniform(0.01, 0.5), 3)
            )

        else:
            # Generic function
            return f"return {random.randint(0, 100)}"

    def get_stats(self) -> dict:
        """Return mock statistics"""
        return {
            "total_calls": self.call_count,
            "total_tokens": self.call_count * 250,  # Fake token count
            "model": self.model_name,
        }
```

### Template-Based Mock (More Realistic)

```python
# backend/core/mock_llm_advanced.py

import jinja2
from pathlib import Path

class TemplateMockSampler(Sampler):
    """
    More sophisticated mock that uses templates to generate
    realistic-looking code variations.
    """

    def __init__(self, template_dir: Path = Path("templates/mock_code")):
        self.template_dir = template_dir
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(template_dir)
        )
        self.call_count = 0

    def sample(self, prompt: str, num_samples: int = 1) -> List[str]:
        """Generate samples from templates"""
        import random

        # Detect problem type from prompt
        problem_type = self._detect_problem_type(prompt)

        # Load template
        template = self.env.get_template(f"{problem_type}.py.jinja")

        # Generate variations
        samples = []
        for i in range(num_samples):
            # Random parameters for template
            params = self._random_params(problem_type, i)
            code = template.render(**params)
            samples.append(code)

        self.call_count += 1
        return samples

    def _detect_problem_type(self, prompt: str) -> str:
        """Detect what kind of problem this is"""
        if "bin" in prompt.lower() or "priority" in prompt.lower():
            return "bin_packing"
        elif "deconvolution" in prompt.lower() or "stopping" in prompt.lower():
            return "lucy_richardson"
        elif "cap set" in prompt.lower():
            return "cap_set"
        else:
            return "generic"

    def _random_params(self, problem_type: str, seed: int) -> dict:
        """Generate random parameters for templates"""
        import random
        random.seed(seed)

        if problem_type == "bin_packing":
            return {
                "threshold": random.randint(10, 90),
                "multiplier": round(random.uniform(0.5, 2.0), 2),
                "offset": random.randint(0, 50),
            }
        elif problem_type == "lucy_richardson":
            return {
                "max_iterations": random.randint(20, 100),
                "psnr_threshold": round(random.uniform(0.01, 0.1), 3),
                "delta_weight": round(random.uniform(0.5, 2.0), 2),
            }
        else:
            return {}
```

### Template Examples

```python
# templates/mock_code/bin_packing.py.jinja
"""Generated bin packing priority function"""

def priority(item: float, bins: np.ndarray, capacity: float) -> float:
    """
    Assign priority to item for bin selection.
    Higher priority = more likely to be selected.
    """
    {% if threshold %}
    if item > {{ threshold }}:
        return item * {{ multiplier }}
    {% endif %}
    return item + {{ offset }}
```

```python
# templates/mock_code/lucy_richardson.py.jinja
"""Generated stopping criterion for Lucy-Richardson"""

def stopping_criterion(iteration: int, psnr: float, psnr_delta: float) -> bool:
    """
    Determine when to stop deconvolution.
    Returns True to stop, False to continue.
    """
    if iteration > {{ max_iterations }}:
        return True

    if psnr_delta < {{ psnr_threshold }}:
        return True

    return False
```

## Mock Sandbox Implementation

### In-Process Evaluation (Simple)

```python
# backend/core/mock_sandbox.py

import ast
import multiprocessing
from typing import Any, Dict
from .evaluator import Evaluator

class MockEvaluator(Evaluator):
    """
    Evaluates code in-process (or subprocess) without Docker.
    WARNING: Not secure! Only use for testing with trusted code.
    """

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def evaluate(self, program: str, test_input: Any) -> float:
        """
        Execute program and return fitness score.
        Uses multiprocessing for timeout support.
        """
        try:
            # Parse code to check syntax
            ast.parse(program)

            # Run in separate process with timeout
            with multiprocessing.Pool(1) as pool:
                result = pool.apply_async(
                    self._run_code,
                    args=(program, test_input)
                )
                score = result.get(timeout=self.timeout)
                return score

        except SyntaxError:
            return float('-inf')  # Invalid code
        except multiprocessing.TimeoutError:
            return float('-inf')  # Timeout
        except Exception as e:
            print(f"Evaluation error: {e}")
            return float('-inf')

    @staticmethod
    def _run_code(program: str, test_input: Any) -> float:
        """Execute code in subprocess"""
        # Create namespace
        namespace = {
            'np': __import__('numpy'),
            '__builtins__': __builtins__,
        }

        # Execute program
        exec(program, namespace)

        # Call evaluate function
        if 'evaluate' in namespace:
            return float(namespace['evaluate'](test_input))
        else:
            raise ValueError("No 'evaluate' function found")
```

### Subprocess Evaluation (Safer)

```python
# backend/core/subprocess_sandbox.py

import subprocess
import json
import tempfile
from pathlib import Path

class SubprocessEvaluator(Evaluator):
    """
    Evaluates code in separate Python subprocess.
    Safer than in-process but not as secure as Docker.
    """

    def __init__(self, timeout: int = 30):
        self.timeout = timeout

    def evaluate(self, program: str, test_input: dict) -> float:
        """Run code in subprocess"""

        # Create temporary script
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.py',
            delete=False
        ) as f:
            # Write program + test harness
            f.write(program)
            f.write("\n\n")
            f.write(f"import json\n")
            f.write(f"test_input = {json.dumps(test_input)}\n")
            f.write(f"result = evaluate(test_input)\n")
            f.write(f"print(json.dumps({{'score': result}}))\n")
            script_path = f.name

        try:
            # Run subprocess
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                timeout=self.timeout,
                text=True,
            )

            if result.returncode == 0:
                # Parse output
                output = json.loads(result.stdout.strip())
                return float(output['score'])
            else:
                print(f"Script error: {result.stderr}")
                return float('-inf')

        except subprocess.TimeoutExpired:
            return float('-inf')
        except Exception as e:
            print(f"Evaluation error: {e}")
            return float('-inf')
        finally:
            # Cleanup
            Path(script_path).unlink(missing_ok=True)
```

## Factory Pattern for Implementation Selection

```python
# backend/core/factory.py

from typing import Literal
from .sampler import Sampler
from .evaluator import Evaluator
from .config import Config

class FunSearchFactory:
    """
    Factory for creating FunSearch components based on configuration.
    Automatically selects mock vs. real implementations.
    """

    @staticmethod
    def create_sampler(config: Config) -> Sampler:
        """Create LLM sampler based on config"""

        if config.llm.provider == "lm_studio":
            from .lm_studio_sampler import LMStudioSampler
            return LMStudioSampler(
                base_url=config.llm.base_url,
                model=config.llm.model,
                temperature=config.llm.temperature,
            )

        elif config.llm.provider == "mock":
            from .mock_llm import MockSampler
            return MockSampler(model_name=config.llm.model)

        elif config.llm.provider == "template_mock":
            from .mock_llm_advanced import TemplateMockSampler
            return TemplateMockSampler()

        else:
            raise ValueError(f"Unknown LLM provider: {config.llm.provider}")

    @staticmethod
    def create_evaluator(config: Config) -> Evaluator:
        """Create evaluator based on config"""

        if config.sandbox.provider == "docker":
            from .docker_evaluator import DockerEvaluator
            return DockerEvaluator(
                max_workers=config.sandbox.max_workers,
                timeout=config.sandbox.timeout,
            )

        elif config.sandbox.provider == "subprocess":
            from .subprocess_sandbox import SubprocessEvaluator
            return SubprocessEvaluator(timeout=config.sandbox.timeout)

        elif config.sandbox.provider == "mock":
            from .mock_sandbox import MockEvaluator
            return MockEvaluator(timeout=config.sandbox.timeout)

        else:
            raise ValueError(f"Unknown sandbox provider: {config.sandbox.provider}")

    @staticmethod
    def create_funsearch(config: Config):
        """Create complete FunSearch instance"""
        from .funsearch import FunSearch

        sampler = FunSearchFactory.create_sampler(config)
        evaluator = FunSearchFactory.create_evaluator(config)

        return FunSearch(
            sampler=sampler,
            evaluator=evaluator,
            config=config.funsearch,
        )
```

## Usage Examples

### In Tests

```python
# tests/test_funsearch.py

import pytest
from backend.core.factory import FunSearchFactory
from backend.core.config import Config

def test_funsearch_with_mocks():
    """Test FunSearch evolution with mock components"""

    config = Config.from_dict({
        "llm": {"provider": "mock", "model": "mock-gpt-4"},
        "sandbox": {"provider": "mock", "timeout": 5},
        "funsearch": {
            "samples_per_prompt": 4,
            "num_islands": 3,  # Smaller for tests
        }
    })

    funsearch = FunSearchFactory.create_funsearch(config)

    # Run for a few iterations
    results = funsearch.run(max_iterations=100)

    assert results.best_score > 0
    assert len(results.programs) > 0
```

### In Development (Web Instance)

```yaml
# .funsearch/config.dev.yaml
mode: "development"

llm:
  provider: "template_mock"  # Use template-based mock

sandbox:
  provider: "subprocess"  # Subprocess is safe enough for dev
  timeout: 10

funsearch:
  samples_per_prompt: 2  # Faster iteration
  num_islands: 3
```

```bash
# Run with dev config
python -m backend.cli run --config=.funsearch/config.dev.yaml
```

### In Production (Local Machine)

```yaml
# .funsearch/config.prod.yaml
mode: "production"

llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "qwen/qwen3-vl-8b"
  temperature: 1.0

sandbox:
  provider: "docker"
  max_workers: 16
  timeout: 30
  image: "funsearch-sandbox:latest"

funsearch:
  samples_per_prompt: 4
  num_islands: 10
```

```bash
# Run with production config
python -m backend.cli run --config=.funsearch/config.prod.yaml
```

## Environment Detection

```python
# backend/core/config.py

import os
from pathlib import Path

class Config:
    @classmethod
    def auto_detect(cls) -> 'Config':
        """
        Auto-detect environment and load appropriate config.
        """
        # Check if LM Studio is available
        lm_studio_available = cls._check_lm_studio()

        # Check if Docker is available
        docker_available = cls._check_docker()

        # Select config based on availability
        if lm_studio_available and docker_available:
            config_file = ".funsearch/config.prod.yaml"
        elif docker_available:
            config_file = ".funsearch/config.docker.yaml"
        else:
            config_file = ".funsearch/config.dev.yaml"

        print(f"Auto-detected environment: {config_file}")
        return cls.from_file(config_file)

    @staticmethod
    def _check_lm_studio() -> bool:
        """Check if LM Studio is running"""
        try:
            import requests
            response = requests.get(
                "http://localhost:1234/v1/models",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False

    @staticmethod
    def _check_docker() -> bool:
        """Check if Docker is available"""
        try:
            import docker
            client = docker.from_env()
            client.ping()
            return True
        except:
            return False
```

## Mock Data for Experiments

```python
# backend/core/mock_data.py

class MockExperimentData:
    """
    Generate fake but realistic experiment data for UI development.
    """

    @staticmethod
    def generate_experiment_history(num_iterations: int = 1000):
        """Generate fake metrics over time"""
        import numpy as np

        # Simulate improving fitness scores
        iterations = np.arange(num_iterations)
        best_score = 100 + 50 * (1 - np.exp(-iterations / 200))
        best_score += np.random.normal(0, 5, num_iterations).cumsum() * 0.1

        # Simulate diversity decreasing
        diversity = 0.8 * np.exp(-iterations / 500) + 0.2

        return {
            "iterations": iterations.tolist(),
            "best_score": best_score.tolist(),
            "diversity": diversity.tolist(),
        }

    @staticmethod
    def generate_island_states(num_islands: int = 10):
        """Generate fake island population states"""
        import random

        islands = []
        for i in range(num_islands):
            islands.append({
                "island_id": i,
                "population_size": random.randint(20, 50),
                "best_score": random.uniform(100, 200),
                "avg_score": random.uniform(50, 150),
                "diversity": random.uniform(0.3, 0.8),
            })

        return islands
```

## Testing Strategy

```python
# tests/conftest.py

import pytest
from backend.core.config import Config
from backend.core.factory import FunSearchFactory

@pytest.fixture
def mock_config():
    """Config using all mocks for fast tests"""
    return Config.from_dict({
        "llm": {"provider": "mock"},
        "sandbox": {"provider": "mock"},
        "funsearch": {"samples_per_prompt": 2, "num_islands": 3}
    })

@pytest.fixture
def funsearch_instance(mock_config):
    """FunSearch instance with mocks"""
    return FunSearchFactory.create_funsearch(mock_config)

# Use in tests
def test_evolution(funsearch_instance):
    results = funsearch_instance.run(max_iterations=50)
    assert results is not None
```

## Summary

| Component | Mock Implementation | Use Case |
|-----------|-------------------|----------|
| **LLM Sampler** | `MockSampler` | Fast unit tests |
| | `TemplateMockSampler` | Realistic dev testing |
| | `LMStudioSampler` | Production (local) |
| **Evaluator** | `MockEvaluator` | Fast unit tests |
| | `SubprocessEvaluator` | Dev/testing (web) |
| | `DockerEvaluator` | Production (secure) |
| **Config** | Auto-detection | Seamless dev→prod |

## Next Steps

1. **Phase 1A**: Implement mock components for web development
2. **Phase 1B**: Implement factory pattern and config system
3. **Phase 2**: Implement real LM Studio and Docker components
4. **Phase 3**: Add auto-detection for seamless switching

This design allows you to:
- ✅ Develop and test in web instance (mocks)
- ✅ Run locally with full features (LM Studio + Docker)
- ✅ CI/CD testing without external dependencies
- ✅ Easy switching via configuration

---

**Last Updated**: 2025-11-16
**Status**: Technical Specification

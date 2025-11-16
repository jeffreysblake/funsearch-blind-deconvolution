"""Evaluator interface for code evaluation in sandboxed environment."""

from abc import ABC, abstractmethod
from typing import Any, List


class Evaluator(ABC):
    """
    Abstract interface for code evaluation in sandboxed environment.

    Implementations:
    - DockerEvaluator: Secure Docker containers
    - SubprocessEvaluator: Subprocess execution
    - MockEvaluator: In-memory evaluation for testing

    Contract:
    - MUST enforce timeout (default 30s)
    - MUST isolate executions (no cross-contamination)
    - MUST return -inf for syntax errors, timeouts, exceptions
    - MUST be thread-safe for parallel execution
    - SHOULD limit resources (CPU, memory, network)
    - MUST clean up all resources on close()
    """

    @abstractmethod
    def evaluate(self, program: str, test_input: Any) -> float:
        """
        Execute program and return fitness score.

        Args:
            program: Python code to execute
            test_input: Input data for evaluation

        Returns:
            Fitness score (higher is better)
            Returns -inf for failed evaluations

        Raises:
            EvaluatorError: If evaluation infrastructure fails
        """
        pass

    @abstractmethod
    def evaluate_batch(self, programs: List[str], test_inputs: List[Any]) -> List[float]:
        """
        Evaluate multiple programs in parallel.

        Args:
            programs: List of Python code strings
            test_inputs: List of test inputs (one per program)

        Returns:
            List of fitness scores (same length as programs)
        """
        pass

    @abstractmethod
    def close(self):
        """Cleanup resources (containers, processes, etc.)."""
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


class EvaluatorError(Exception):
    """Base exception for evaluator errors."""

    pass

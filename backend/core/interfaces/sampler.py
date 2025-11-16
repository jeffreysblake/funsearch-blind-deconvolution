"""Sampler interface for LLM code generation."""

from abc import ABC, abstractmethod
from typing import List


class Sampler(ABC):
    """
    Abstract interface for LLM code generation.

    Implementations:
    - LMStudioSampler: Real LM Studio integration
    - MockSampler: Simple deterministic mock for testing
    - TemplateMockSampler: Template-based mock for development

    Contract:
    - MUST return valid Python code strings
    - MUST handle timeout gracefully
    - MUST be thread-safe for parallel calls
    - SHOULD cache responses for identical prompts
    - MAY raise SamplerError for retryable errors
    """

    @abstractmethod
    def sample(self, prompt: str, num_samples: int = 1) -> List[str]:
        """
        Generate code samples from a prompt.

        Args:
            prompt: The code prompt (partial function to complete)
            num_samples: Number of samples to generate

        Returns:
            List of generated code strings

        Raises:
            SamplerError: If generation fails
            TimeoutError: If generation times out
        """
        pass

    @abstractmethod
    def get_stats(self) -> dict:
        """
        Get sampler statistics (tokens used, calls made, etc.).

        Returns:
            Dictionary with statistics
        """
        pass

    def __enter__(self):
        """Context manager support."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup resources."""
        pass


class SamplerError(Exception):
    """Base exception for sampler errors."""

    pass

"""Factory for creating FunSearch components based on configuration."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from config.models import Config

from .interfaces import Evaluator, Sampler


class ComponentFactory:
    """
    Factory for creating FunSearch components.

    Automatically selects implementation based on configuration:
    - LLM Provider: lm_studio, mock, template_mock
    - Sandbox Provider: docker, subprocess, mock
    """

    @staticmethod
    def create_sampler(config: "Config") -> Sampler:
        """
        Create LLM sampler based on configuration.

        Args:
            config: Application configuration

        Returns:
            Sampler implementation

        Raises:
            ValueError: If provider is unknown
        """
        provider = config.llm.provider

        if provider == "lm_studio":
            # Import only when needed (might not be available in all environments)
            try:
                from .lm_studio_sampler import LMStudioSampler

                return LMStudioSampler(
                    base_url=config.llm.base_url,
                    model=config.llm.model,
                    temperature=config.llm.temperature,
                    max_tokens=config.llm.max_tokens,
                    timeout=config.llm.timeout,
                )
            except ImportError as e:
                raise ImportError(
                    f"LM Studio sampler not available. Install with: pip install openai\n{e}"
                )

        elif provider == "mock":
            from .mocks import MockSampler

            return MockSampler(model_name=config.llm.model)

        elif provider == "template_mock":
            from .mocks import TemplateMockSampler

            return TemplateMockSampler()

        else:
            raise ValueError(
                f"Unknown LLM provider: {provider}. "
                f"Valid options: lm_studio, mock, template_mock"
            )

    @staticmethod
    def create_evaluator(config: "Config") -> Evaluator:
        """
        Create code evaluator based on configuration.

        Args:
            config: Application configuration

        Returns:
            Evaluator implementation

        Raises:
            ValueError: If provider is unknown
        """
        provider = config.sandbox.provider

        if provider == "docker":
            # Import only when needed
            try:
                from .docker_evaluator import DockerEvaluator

                return DockerEvaluator(
                    max_workers=config.sandbox.max_workers,
                    timeout=config.sandbox.timeout,
                    image=config.sandbox.image,
                    limits=config.sandbox.limits,
                )
            except ImportError as e:
                raise ImportError(
                    f"Docker evaluator not available. Install with: pip install docker\n{e}"
                )

        elif provider == "subprocess":
            from .mocks import SubprocessEvaluator

            return SubprocessEvaluator(
                timeout=config.sandbox.timeout, max_workers=config.sandbox.max_workers
            )

        elif provider == "mock":
            from .mocks import MockEvaluator

            return MockEvaluator(timeout=config.sandbox.timeout)

        else:
            raise ValueError(
                f"Unknown sandbox provider: {provider}. "
                f"Valid options: docker, subprocess, mock"
            )

    @staticmethod
    def create_components(config: "Config") -> tuple[Sampler, Evaluator]:
        """
        Create all core components.

        Args:
            config: Application configuration

        Returns:
            Tuple of (sampler, evaluator)
        """
        sampler = ComponentFactory.create_sampler(config)
        evaluator = ComponentFactory.create_evaluator(config)

        return sampler, evaluator

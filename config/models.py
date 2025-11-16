"""Configuration models using Pydantic."""

import os
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class LLMConfig(BaseModel):
    """LLM configuration."""

    provider: Literal["lm_studio", "mock", "template_mock"] = "mock"
    model: str = Field(..., min_length=1)
    base_url: str = "http://localhost:1234/v1"
    temperature: float = Field(1.0, ge=0.0, le=2.0)
    max_tokens: int = Field(512, ge=50, le=4096)
    timeout: int = Field(30, ge=5, le=300)


class SandboxConfig(BaseModel):
    """Sandbox configuration."""

    provider: Literal["docker", "subprocess", "mock"] = "mock"
    max_workers: int = Field(8, ge=1, le=64)
    timeout: int = Field(30, ge=5, le=300)
    image: str = "funsearch-sandbox:latest"
    limits: dict = Field(
        default_factory=lambda: {"memory": "256m", "cpu_cores": 1}
    )


class FunSearchConfig(BaseModel):
    """FunSearch algorithm configuration."""

    samples_per_prompt: int = Field(4, ge=1, le=16)
    num_islands: int = Field(10, ge=1, le=20)
    reset_period: int = Field(80000, ge=1000)
    cluster_sampling_temperature_init: float = Field(0.1, ge=0.01, le=1.0)
    cluster_sampling_temperature_period: int = Field(20000, ge=1000)


class ExecutionConfig(BaseModel):
    """Execution configuration."""

    max_iterations: int = Field(100000, ge=100)
    checkpoint_interval: int = Field(1000, ge=100)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: str = "sqlite:///funsearch.db"
    echo: bool = False  # SQL logging
    pool_size: int = Field(20, ge=1, le=100)
    max_overflow: int = Field(0, ge=0, le=50)


class MLflowConfig(BaseModel):
    """MLflow configuration."""

    tracking_uri: str = "http://localhost:7352"
    experiment_name: str = "funsearch"


class Config(BaseModel):
    """Complete application configuration."""

    mode: Literal["development", "production", "test"] = "development"
    llm: LLMConfig
    sandbox: SandboxConfig
    funsearch: FunSearchConfig
    execution: ExecutionConfig
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    mlflow: MLflowConfig = Field(default_factory=MLflowConfig)

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """Validate and normalize mode."""
        return v.lower()

    @classmethod
    def from_file(cls, config_file: Path | str) -> "Config":
        """Load configuration from YAML file."""
        config_file = Path(config_file)

        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_file) as f:
            data = yaml.safe_load(f)

        return cls(**data)

    @classmethod
    def auto_detect(cls) -> "Config":
        """Auto-detect environment and load appropriate config."""
        # Check for config file in standard locations
        config_paths = [
            Path(".funsearch/config.yaml"),
            Path(".funsearch/config.dev.yaml"),
            Path("config.yaml"),
        ]

        for path in config_paths:
            if path.exists():
                print(f"Loading config from: {path}")
                return cls.from_file(path)

        # No config file found, use defaults with auto-detection
        print("No config file found, using defaults with auto-detection")

        llm_provider = "lm_studio" if _check_lm_studio() else "mock"
        sandbox_provider = "docker" if _check_docker() else "subprocess"

        return cls(
            mode="development",
            llm=LLMConfig(
                provider=llm_provider,
                model="mock-gpt-4" if llm_provider == "mock" else "qwen/qwen3-vl-8b",
            ),
            sandbox=SandboxConfig(provider=sandbox_provider),
            funsearch=FunSearchConfig(),
            execution=ExecutionConfig(),
        )

    def to_file(self, config_file: Path | str) -> None:
        """Save configuration to YAML file."""
        config_file = Path(config_file)
        config_file.parent.mkdir(parents=True, exist_ok=True)

        with open(config_file, "w") as f:
            yaml.dump(self.model_dump(), f, default_flow_style=False, sort_keys=False)


def _check_lm_studio() -> bool:
    """Check if LM Studio is available."""
    try:
        import httpx

        response = httpx.get("http://localhost:1234/v1/models", timeout=2)
        return response.status_code == 200
    except Exception:
        return False


def _check_docker() -> bool:
    """Check if Docker is available."""
    try:
        import docker

        client = docker.from_env()
        client.ping()
        return True
    except Exception:
        return False


def load_config(config_file: Optional[Path | str] = None) -> Config:
    """
    Load configuration from file or auto-detect.

    Args:
        config_file: Path to config file, or None to auto-detect

    Returns:
        Loaded configuration
    """
    if config_file:
        return Config.from_file(config_file)
    return Config.auto_detect()

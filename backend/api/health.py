"""Health check endpoint."""

from datetime import datetime
from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from config.detection import detect_lm_studio, check_mlflow

router = APIRouter()


class ServiceStatus(BaseModel):
    """Service status model."""

    database: str = "connected"
    redis: str = "not_configured"
    mlflow: str = "not_configured"
    mlflow_uri: Optional[str] = None
    lm_studio: str = "disconnected"
    lm_studio_model: Optional[str] = None
    lm_studio_models: list[str] = []
    docker: str = "unavailable"


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    timestamp: datetime
    services: ServiceStatus
    config_mode: str = "development"
    errors: list[str] = []


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check system health and service connectivity.

    Returns status of all services and configuration mode.
    """
    services = ServiceStatus()
    errors = []

    # Check LM Studio using detection utility
    lm_studio_status = detect_lm_studio()
    if lm_studio_status["available"]:
        services.lm_studio = "connected"
        services.lm_studio_model = lm_studio_status["current_model"]
        services.lm_studio_models = lm_studio_status["models"]
    else:
        services.lm_studio = "disconnected"
        if lm_studio_status["error"]:
            errors.append(f"LM Studio: {lm_studio_status['error']}")

    # Check MLflow using detection utility
    mlflow_status = check_mlflow()
    if mlflow_status["available"]:
        services.mlflow = "connected"
        services.mlflow_uri = mlflow_status["tracking_uri"]
    else:
        services.mlflow = "disconnected"
        # Don't add to errors since MLflow is optional

    # Check Docker
    try:
        import docker

        client = docker.from_env()
        client.ping()
        services.docker = "available"
    except Exception:
        services.docker = "unavailable"
        # Don't add to errors since Docker is optional for development

    # Determine overall status
    # System is healthy even if optional services (LM Studio, Docker, MLflow) are down
    status = "healthy"

    return HealthResponse(
        status=status,
        version="0.1.0",
        timestamp=datetime.utcnow(),
        services=services,
        config_mode="development",
        errors=errors,
    )

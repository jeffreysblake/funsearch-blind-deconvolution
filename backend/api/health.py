"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ServiceStatus(BaseModel):
    """Service status model."""

    database: str = "connected"
    redis: str = "not_configured"
    mlflow: str = "not_configured"
    lm_studio: str = "disconnected"
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

    # Check LM Studio
    try:
        import httpx

        response = httpx.get("http://localhost:1234/v1/models", timeout=2)
        if response.status_code == 200:
            services.lm_studio = "connected"
    except Exception as e:
        services.lm_studio = "disconnected"
        errors.append(f"LM Studio not responding: {str(e)}")

    # Check Docker
    try:
        import docker

        client = docker.from_env()
        client.ping()
        services.docker = "available"
    except Exception as e:
        services.docker = "unavailable"
        errors.append(f"Docker not available: {str(e)}")

    # Determine overall status
    status = "healthy" if not errors else "degraded"

    return HealthResponse(
        status=status,
        version="0.1.0",
        timestamp=datetime.utcnow(),
        services=services,
        config_mode="development",
        errors=errors,
    )

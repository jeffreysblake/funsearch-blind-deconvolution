"""Tests for backend API health endpoint."""

import pytest
from fastapi.testclient import TestClient

from backend.main import app

client = TestClient(app)


def test_health_endpoint_returns_200():
    """Test that health endpoint returns 200 OK."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_structure():
    """Test that health endpoint returns expected structure."""
    response = client.get("/health")
    data = response.json()

    assert "status" in data
    assert "version" in data
    assert "timestamp" in data
    assert "services" in data
    assert "config_mode" in data


def test_health_services_structure():
    """Test that services section has expected fields."""
    response = client.get("/health")
    data = response.json()
    services = data["services"]

    assert "database" in services
    assert "lm_studio" in services
    assert "mlflow" in services
    assert "docker" in services


def test_health_status_is_healthy():
    """Test that status is healthy when core services are up."""
    response = client.get("/health")
    data = response.json()

    # Should be healthy even if optional services (LM Studio, MLflow) are down
    assert data["status"] == "healthy"


def test_health_version():
    """Test that version is returned."""
    response = client.get("/health")
    data = response.json()

    assert data["version"] == "0.1.0"

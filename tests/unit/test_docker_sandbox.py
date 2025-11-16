"""Tests for Docker sandbox."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from docker.errors import ContainerError, ImageNotFound

from backend.core.sandbox.docker_sandbox import DockerSandbox


@pytest.fixture
def mock_docker_client():
    """Mock Docker client."""
    mock_client = MagicMock()
    mock_client.ping.return_value = True

    # Mock image exists
    mock_image = Mock()
    mock_client.images.get.return_value = mock_image

    return mock_client


@patch("docker.from_env")
def test_docker_sandbox_init(mock_docker_from_env, mock_docker_client):
    """Test DockerSandbox initialization."""
    mock_docker_from_env.return_value = mock_docker_client

    sandbox = DockerSandbox()

    assert sandbox.image == "funsearch-sandbox:latest"
    assert sandbox.memory_limit == "256m"
    assert sandbox.timeout == 30


@patch("docker.from_env")
def test_docker_sandbox_execute_success(mock_docker_from_env, mock_docker_client):
    """Test successful code execution."""
    mock_docker_from_env.return_value = mock_docker_client
    mock_docker_client.containers.run.return_value = b"Hello, World!"

    sandbox = DockerSandbox()
    result = sandbox.execute("print('Hello, World!')")

    assert result["success"] is True
    assert "Hello, World!" in result["stdout"]
    assert result["exit_code"] == 0


@patch("docker.from_env")
def test_docker_sandbox_execute_error(mock_docker_from_env, mock_docker_client):
    """Test execution with error."""
    mock_docker_from_env.return_value = mock_docker_client

    error = ContainerError(
        container="test",
        exit_status=1,
        command="python",
        image="test-image",
        stderr=b"SyntaxError: invalid syntax",
    )
    mock_docker_client.containers.run.side_effect = error

    sandbox = DockerSandbox()
    result = sandbox.execute("invalid python code")

    assert result["success"] is False
    assert result["exit_code"] == 1
    assert "SyntaxError" in result["stderr"]


@patch("docker.from_env")
def test_docker_sandbox_health_check(mock_docker_from_env, mock_docker_client):
    """Test health check."""
    mock_docker_from_env.return_value = mock_docker_client
    mock_docker_client.version.return_value = {"Version": "20.10.0"}
    mock_docker_client.containers.run.return_value = b"ok"

    sandbox = DockerSandbox()
    health = sandbox.health_check()

    assert health["status"] == "healthy"
    assert "docker_version" in health


@patch("docker.from_env")
def test_docker_sandbox_connection_error(mock_docker_from_env):
    """Test handling of Docker connection error."""
    mock_docker_from_env.side_effect = Exception("Cannot connect to Docker daemon")

    with pytest.raises(Exception):
        DockerSandbox()

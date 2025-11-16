"""Tests for LM Studio sampler."""

import pytest
from unittest.mock import Mock, patch, MagicMock
import requests

from backend.core.llm.lm_studio import LMStudioSampler


@pytest.fixture
def mock_successful_response():
    """Mock successful LM Studio API response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"text": "    return value / weight"}],
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 20,
            "total_tokens": 120,
        },
    }
    return mock_response


@pytest.fixture
def mock_models_response():
    """Mock models list response."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"id": "test-model"}]
    }
    return mock_response


@patch("requests.Session")
def test_lm_studio_sampler_init(mock_session_class, mock_models_response):
    """Test LMStudioSampler initialization."""
    mock_session = MagicMock()
    mock_session.get.return_value = mock_models_response
    mock_session_class.return_value = mock_session

    sampler = LMStudioSampler(model="test-model")

    assert sampler.model == "test-model"
    assert sampler.temperature == 1.0
    assert sampler.max_tokens == 512


@patch("requests.Session")
def test_lm_studio_sampler_sample(mock_session_class, mock_models_response, mock_successful_response):
    """Test generating samples."""
    mock_session = MagicMock()
    mock_session.get.return_value = mock_models_response
    mock_session.post.return_value = mock_successful_response
    mock_session_class.return_value = mock_session

    sampler = LMStudioSampler(model="test-model")
    samples = sampler.sample("def priority(value, weight):", num_samples=2)

    assert len(samples) == 2
    assert all(isinstance(s, str) for s in samples)


@patch("requests.Session")
def test_lm_studio_sampler_connection_error(mock_session_class):
    """Test handling of connection errors."""
    mock_session = MagicMock()
    mock_session.get.side_effect = requests.exceptions.ConnectionError("Cannot connect")
    mock_session_class.return_value = mock_session

    with pytest.raises(ConnectionError):
        LMStudioSampler()


@patch("requests.Session")
def test_lm_studio_sampler_timeout(mock_session_class, mock_models_response):
    """Test handling of timeout."""
    mock_session = MagicMock()
    mock_session.get.return_value = mock_models_response
    mock_session.post.side_effect = requests.exceptions.Timeout("Timed out")
    mock_session_class.return_value = mock_session

    sampler = LMStudioSampler(model="test-model")

    with pytest.raises(TimeoutError):
        sampler.sample("test prompt")


@patch("requests.Session")
def test_lm_studio_health_check(mock_session_class, mock_models_response):
    """Test health check."""
    mock_session = MagicMock()
    mock_session.get.return_value = mock_models_response
    mock_session_class.return_value = mock_session

    sampler = LMStudioSampler(model="test-model")
    health = sampler.health_check()

    assert health["status"] == "healthy"
    assert "model" in health
    assert "available_models" in health

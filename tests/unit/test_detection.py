"""Tests for service detection utilities."""

import pytest
from unittest.mock import Mock, patch

from config.detection import detect_lm_studio, check_mlflow, auto_configure_llm


@patch("requests.get")
def test_detect_lm_studio_available(mock_get):
    """Test LM Studio detection when available."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": [{"id": "test-model"}]
    }
    mock_get.return_value = mock_response

    result = detect_lm_studio()

    assert result["available"] is True
    assert result["current_model"] == "test-model"
    assert "test-model" in result["models"]


@patch("requests.get")
def test_detect_lm_studio_unavailable(mock_get):
    """Test LM Studio detection when unavailable."""
    mock_get.side_effect = Exception("Connection refused")

    result = detect_lm_studio()

    assert result["available"] is False
    assert result["error"] is not None


@patch("requests.get")
def test_detect_lm_studio_no_models(mock_get):
    """Test LM Studio detection when no models loaded."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"data": []}
    mock_get.return_value = mock_response

    result = detect_lm_studio()

    assert result["available"] is False
    assert "no models" in result["error"].lower()


@patch("requests.get")
def test_check_mlflow_available(mock_get):
    """Test MLflow detection when available."""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_get.return_value = mock_response

    result = check_mlflow()

    assert result["available"] is True


@patch("requests.get")
def test_check_mlflow_unavailable(mock_get):
    """Test MLflow detection when unavailable."""
    mock_get.side_effect = Exception("Connection refused")

    result = check_mlflow()

    assert result["available"] is False
    assert result["error"] is not None


@patch("config.detection.detect_lm_studio")
def test_auto_configure_llm_with_lm_studio(mock_detect):
    """Test auto-configuration when LM Studio is available."""
    mock_detect.return_value = {
        "available": True,
        "current_model": "test-model",
        "base_url": "http://localhost:1234/v1",
    }

    config = auto_configure_llm()

    assert config["provider"] == "lm_studio"
    assert config["model"] == "test-model"


@patch("config.detection.detect_lm_studio")
def test_auto_configure_llm_without_lm_studio(mock_detect):
    """Test auto-configuration when LM Studio is unavailable."""
    mock_detect.return_value = {
        "available": False,
        "error": "Not running",
    }

    config = auto_configure_llm()

    assert config["provider"] == "template_mock"
    assert config["model"] == "mock"

"""Auto-detection utilities for LM Studio and Docker."""

import logging
from typing import Optional

import requests

logger = logging.getLogger(__name__)


def detect_lm_studio(base_url: str = "http://localhost:1234/v1", timeout: int = 2) -> dict:
    """Detect if LM Studio is running and get available models.

    Args:
        base_url: LM Studio API base URL
        timeout: Connection timeout in seconds

    Returns:
        Dict with detection results:
        {
            "available": bool,
            "base_url": str,
            "models": list[str],
            "current_model": Optional[str],
            "error": Optional[str]
        }
    """
    result = {
        "available": False,
        "base_url": base_url,
        "models": [],
        "current_model": None,
        "error": None,
    }

    try:
        response = requests.get(
            f"{base_url}/models",
            timeout=timeout,
        )
        response.raise_for_status()

        data = response.json()

        if "data" in data and len(data["data"]) > 0:
            result["available"] = True
            result["models"] = [model["id"] for model in data["data"]]
            result["current_model"] = data["data"][0]["id"]  # First model is current
            logger.info(f"✓ LM Studio detected at {base_url}")
            logger.info(f"  Current model: {result['current_model']}")
        else:
            result["error"] = "LM Studio is running but no models are loaded"
            logger.warning(result["error"])

    except requests.exceptions.ConnectionError:
        result["error"] = f"LM Studio not reachable at {base_url}"
        logger.debug(result["error"])

    except requests.exceptions.Timeout:
        result["error"] = f"Connection to LM Studio timed out ({timeout}s)"
        logger.debug(result["error"])

    except Exception as e:
        result["error"] = f"Error detecting LM Studio: {e}"
        logger.warning(result["error"])

    return result


def get_recommended_model() -> Optional[str]:
    """Get recommended model based on what's available in LM Studio.

    Returns:
        Model name if LM Studio is available, None otherwise
    """
    detection = detect_lm_studio()

    if detection["available"]:
        return detection["current_model"]

    return None


def check_mlflow(tracking_uri: str = "http://localhost:7352", timeout: int = 2) -> dict:
    """Check if MLflow tracking server is running.

    Args:
        tracking_uri: MLflow tracking URI
        timeout: Connection timeout

    Returns:
        Dict with detection results
    """
    result = {
        "available": False,
        "tracking_uri": tracking_uri,
        "error": None,
    }

    try:
        # MLflow health check endpoint
        health_url = tracking_uri.replace("/api", "").rstrip("/") + "/health"

        response = requests.get(health_url, timeout=timeout)
        response.raise_for_status()

        result["available"] = True
        logger.info(f"✓ MLflow detected at {tracking_uri}")

    except requests.exceptions.ConnectionError:
        result["error"] = f"MLflow not reachable at {tracking_uri}"
        logger.debug(result["error"])

    except Exception as e:
        result["error"] = f"Error detecting MLflow: {e}"
        logger.debug(result["error"])

    return result


def auto_configure_llm(preferred_provider: Optional[str] = None) -> dict:
    """Auto-configure LLM based on what's available.

    Args:
        preferred_provider: Preferred provider if available

    Returns:
        Dict with LLM configuration
    """
    # Check if LM Studio is available
    lm_studio = detect_lm_studio()

    # If user prefers LM Studio and it's available, use it
    if preferred_provider == "lm_studio" and lm_studio["available"]:
        return {
            "provider": "lm_studio",
            "model": lm_studio["current_model"],
            "base_url": lm_studio["base_url"],
        }

    # If LM Studio is available and no preference, use it
    if lm_studio["available"]:
        logger.info("Auto-configuring to use LM Studio")
        return {
            "provider": "lm_studio",
            "model": lm_studio["current_model"],
            "base_url": lm_studio["base_url"],
        }

    # Fall back to mock
    logger.info("LM Studio not available, using mock LLM")
    return {
        "provider": "template_mock",
        "model": "mock",
        "base_url": "http://localhost:1234/v1",  # For consistency
    }


def get_system_info() -> dict:
    """Get complete system information for diagnostics.

    Returns:
        Dict with system capabilities
    """
    lm_studio = detect_lm_studio()
    mlflow = check_mlflow()

    return {
        "lm_studio": lm_studio,
        "mlflow": mlflow,
        "recommended_config": auto_configure_llm(),
    }

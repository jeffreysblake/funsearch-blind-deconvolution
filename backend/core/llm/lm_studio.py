"""LM Studio integration for FunSearch."""

import logging
import time
from typing import List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from backend.core.interfaces.sampler import Sampler

logger = logging.getLogger(__name__)


class LMStudioSampler(Sampler):
    """Sampler that uses LM Studio API for code generation.

    LM Studio provides an OpenAI-compatible API running locally.
    Default endpoint: http://localhost:1234/v1
    """

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: int = 512,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0,
    ):
        """Initialize LM Studio sampler.

        Args:
            base_url: LM Studio API base URL
            model: Model name (if None, uses currently loaded model)
            temperature: Sampling temperature (higher = more creative)
            max_tokens: Maximum tokens to generate
            timeout: Request timeout in seconds
            max_retries: Number of retries on failure
            retry_delay: Delay between retries in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        # Create session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=retry_delay,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        # Verify connection and get model info
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify LM Studio is running and get model info."""
        try:
            response = self.session.get(
                f"{self.base_url}/models", timeout=5
            )
            response.raise_for_status()
            models_data = response.json()

            if "data" in models_data and len(models_data["data"]) > 0:
                if self.model is None:
                    # Use first available model
                    self.model = models_data["data"][0]["id"]
                logger.info(f"✓ Connected to LM Studio, using model: {self.model}")
            else:
                raise ValueError("No models loaded in LM Studio")

        except requests.exceptions.RequestException as e:
            logger.error(f"✗ Failed to connect to LM Studio at {self.base_url}")
            raise ConnectionError(
                f"Cannot connect to LM Studio at {self.base_url}. "
                f"Make sure LM Studio is running and a model is loaded. Error: {e}"
            )

    def sample(self, prompt: str, num_samples: int = 1) -> List[str]:
        """Generate code samples from prompt.

        Args:
            prompt: Code prompt to complete
            num_samples: Number of samples to generate

        Returns:
            List of generated code samples
        """
        samples = []

        for i in range(num_samples):
            try:
                sample = self._generate_single_sample(prompt)
                samples.append(sample)
                logger.debug(f"Generated sample {i+1}/{num_samples}")

            except Exception as e:
                logger.error(f"Failed to generate sample {i+1}/{num_samples}: {e}")
                # Return what we have so far
                if samples:
                    logger.warning(f"Returning {len(samples)}/{num_samples} samples due to error")
                    return samples
                else:
                    raise

        return samples

    def _generate_single_sample(self, prompt: str) -> str:
        """Generate a single code sample.

        Args:
            prompt: Code prompt to complete

        Returns:
            Generated code sample
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "stop": ["\n\n\n", "def ", "class "],  # Stop at function boundaries
        }

        start_time = time.time()

        try:
            response = self.session.post(
                f"{self.base_url}/completions",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            elapsed = time.time() - start_time
            logger.debug(f"LLM call completed in {elapsed:.2f}s")

            data = response.json()

            if "choices" not in data or len(data["choices"]) == 0:
                raise ValueError("LM Studio returned no choices")

            completion = data["choices"][0]["text"]

            # Log token usage if available
            if "usage" in data:
                usage = data["usage"]
                logger.debug(
                    f"Tokens: {usage.get('prompt_tokens', 0)} prompt + "
                    f"{usage.get('completion_tokens', 0)} completion = "
                    f"{usage.get('total_tokens', 0)} total"
                )

            return completion

        except requests.exceptions.Timeout:
            raise TimeoutError(f"LM Studio request timed out after {self.timeout}s")

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"LM Studio API error: {e}")

    def health_check(self) -> dict:
        """Check LM Studio health and return status.

        Returns:
            Dict with status information
        """
        try:
            response = self.session.get(
                f"{self.base_url}/models", timeout=5
            )
            response.raise_for_status()
            models = response.json()

            return {
                "status": "healthy",
                "base_url": self.base_url,
                "model": self.model,
                "available_models": [m["id"] for m in models.get("data", [])],
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "base_url": self.base_url,
                "error": str(e),
            }


class LMStudioChatSampler(Sampler):
    """Sampler using LM Studio's chat completion API.

    Some models work better with chat format than raw completions.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        model: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: int = 512,
        timeout: int = 30,
        system_prompt: Optional[str] = None,
    ):
        """Initialize chat-based sampler.

        Args:
            base_url: LM Studio API base URL
            model: Model name
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            timeout: Request timeout
            system_prompt: Optional system prompt for chat models
        """
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout = timeout
        self.system_prompt = system_prompt or (
            "You are an expert programmer. Complete the given code accurately and concisely."
        )

        self.session = requests.Session()
        self._verify_connection()

    def _verify_connection(self) -> None:
        """Verify LM Studio is running."""
        try:
            response = self.session.get(
                f"{self.base_url}/models", timeout=5
            )
            response.raise_for_status()
            models_data = response.json()

            if self.model is None and "data" in models_data:
                self.model = models_data["data"][0]["id"]

            logger.info(f"✓ Connected to LM Studio (chat mode), model: {self.model}")

        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Cannot connect to LM Studio: {e}")

    def sample(self, prompt: str, num_samples: int = 1) -> List[str]:
        """Generate code samples using chat API.

        Args:
            prompt: Code prompt to complete
            num_samples: Number of samples to generate

        Returns:
            List of generated code samples
        """
        samples = []

        for i in range(num_samples):
            try:
                sample = self._generate_single_sample(prompt)
                samples.append(sample)
            except Exception as e:
                logger.error(f"Failed to generate sample {i+1}: {e}")
                if samples:
                    return samples
                raise

        return samples

    def _generate_single_sample(self, prompt: str) -> str:
        """Generate single sample via chat API."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Complete this code:\n\n{prompt}"},
        ]

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            response = self.session.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()

            data = response.json()

            if "choices" not in data or len(data["choices"]) == 0:
                raise ValueError("No response from LM Studio")

            return data["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"LM Studio chat API error: {e}")

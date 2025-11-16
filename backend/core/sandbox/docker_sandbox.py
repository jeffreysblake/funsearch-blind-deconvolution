"""Docker-based sandbox for secure code execution."""

import logging
import tempfile
from pathlib import Path
from typing import Any, Optional

import docker
from docker.errors import ContainerError, ImageNotFound

logger = logging.getLogger(__name__)


class DockerSandbox:
    """Execute code in isolated Docker containers.

    Security features:
    - No network access
    - Read-only filesystem (except /tmp)
    - Memory limits
    - CPU limits
    - Execution timeout
    - Non-root user inside container
    """

    def __init__(
        self,
        image: str = "funsearch-sandbox:latest",
        memory_limit: str = "256m",
        cpu_limit: float = 1.0,
        timeout: int = 30,
    ):
        """Initialize Docker sandbox.

        Args:
            image: Docker image to use
            memory_limit: Memory limit (e.g., "256m", "1g")
            cpu_limit: CPU limit in cores (e.g., 1.0, 0.5)
            timeout: Execution timeout in seconds
        """
        self.image = image
        self.memory_limit = memory_limit
        self.cpu_limit = cpu_limit
        self.timeout = timeout

        # Initialize Docker client
        try:
            self.client = docker.from_env()
            self.client.ping()
            logger.info("✓ Docker client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Docker client: {e}")
            raise

        # Verify sandbox image exists
        self._verify_image()

    def _verify_image(self):
        """Verify sandbox image exists, build if necessary."""
        try:
            self.client.images.get(self.image)
            logger.debug(f"Sandbox image found: {self.image}")
        except ImageNotFound:
            logger.warning(f"Sandbox image not found: {self.image}")
            logger.info("Building sandbox image...")
            self._build_image()

    def _build_image(self):
        """Build sandbox image from Dockerfile."""
        try:
            # Build from Dockerfile.sandbox
            dockerfile_path = Path(__file__).parent.parent.parent.parent / "Dockerfile.sandbox"
            if not dockerfile_path.exists():
                raise FileNotFoundError(f"Dockerfile not found: {dockerfile_path}")

            self.client.images.build(
                path=str(dockerfile_path.parent),
                dockerfile="Dockerfile.sandbox",
                tag=self.image,
                rm=True,
            )
            logger.info(f"✓ Built sandbox image: {self.image}")

        except Exception as e:
            logger.error(f"Failed to build sandbox image: {e}")
            raise

    def execute(
        self,
        code: str,
        test_input: Optional[Any] = None,
    ) -> dict:
        """Execute code in sandbox and return results.

        Args:
            code: Python code to execute
            test_input: Optional test input (not used in current implementation)

        Returns:
            Dict with execution results:
            {
                "success": bool,
                "stdout": str,
                "stderr": str,
                "exit_code": int,
                "error": Optional[str]
            }
        """
        # Create temporary file for code
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
        ) as f:
            f.write(code)
            code_file = Path(f.name)

        try:
            # Run container
            result = self.client.containers.run(
                image=self.image,
                command=["python", "/sandbox/code.py"],
                volumes={
                    str(code_file): {
                        "bind": "/sandbox/code.py",
                        "mode": "ro",
                    }
                },
                mem_limit=self.memory_limit,
                nano_cpus=int(self.cpu_limit * 1e9),
                network_disabled=True,
                read_only=True,
                tmpfs={"/tmp": "size=10m"},
                remove=True,
                stdout=True,
                stderr=True,
                timeout=self.timeout,
            )

            # Decode output
            stdout = result.decode("utf-8") if isinstance(result, bytes) else result

            return {
                "success": True,
                "stdout": stdout,
                "stderr": "",
                "exit_code": 0,
                "error": None,
            }

        except ContainerError as e:
            logger.warning(f"Container execution failed: {e}")
            return {
                "success": False,
                "stdout": e.stdout.decode("utf-8") if e.stdout else "",
                "stderr": e.stderr.decode("utf-8") if e.stderr else str(e),
                "exit_code": e.exit_status,
                "error": str(e),
            }

        except Exception as e:
            logger.error(f"Sandbox execution error: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "error": str(e),
            }

        finally:
            # Clean up temporary file
            try:
                code_file.unlink()
            except Exception as e:
                logger.warning(f"Failed to clean up temp file: {e}")

    def health_check(self) -> dict:
        """Check if Docker sandbox is available.

        Returns:
            Dict with health status
        """
        try:
            # Ping Docker daemon
            self.client.ping()

            # Check image exists
            self.client.images.get(self.image)

            # Try running a simple container
            result = self.client.containers.run(
                image=self.image,
                command=["python", "-c", "print('ok')"],
                remove=True,
                timeout=5,
            )

            return {
                "status": "healthy",
                "image": self.image,
                "docker_version": self.client.version()["Version"],
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

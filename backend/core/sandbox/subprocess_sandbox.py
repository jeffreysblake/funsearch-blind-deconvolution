"""Subprocess-based sandbox for code execution (less secure)."""

import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class SubprocessSandbox:
    """Execute code in subprocesses.

    WARNING: This is less secure than Docker sandbox.
    Use only for development/testing or trusted code.

    Security features:
    - Execution timeout
    - Resource limits (via ulimit where available)

    Missing protections:
    - No filesystem isolation
    - No network isolation
    - No memory limits (on Windows)
    """

    def __init__(
        self,
        timeout: int = 30,
    ):
        """Initialize subprocess sandbox.

        Args:
            timeout: Execution timeout in seconds
        """
        self.timeout = timeout
        logger.warning(
            "Using SubprocessSandbox - not recommended for production!"
        )

    def execute(
        self,
        code: str,
        test_input: Optional[Any] = None,
    ) -> dict:
        """Execute code in subprocess and return results.

        Args:
            code: Python code to execute
            test_input: Optional test input (not used)

        Returns:
            Dict with execution results
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
            # Run in subprocess
            result = subprocess.run(
                ["python", str(code_file)],
                capture_output=True,
                timeout=self.timeout,
                text=True,
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "exit_code": result.returncode,
                "error": None if result.returncode == 0 else result.stderr,
            }

        except subprocess.TimeoutExpired as e:
            logger.warning(f"Execution timed out after {self.timeout}s")
            return {
                "success": False,
                "stdout": e.stdout.decode("utf-8") if e.stdout else "",
                "stderr": f"Execution timed out after {self.timeout}s",
                "exit_code": -1,
                "error": "Timeout",
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
        """Check if subprocess sandbox is available.

        Returns:
            Dict with health status
        """
        try:
            # Try running a simple Python command
            result = subprocess.run(
                ["python", "-c", "print('ok')"],
                capture_output=True,
                timeout=5,
                text=True,
            )

            if result.returncode == 0:
                return {
                    "status": "healthy",
                    "warning": "SubprocessSandbox is not recommended for production",
                }
            else:
                return {
                    "status": "unhealthy",
                    "error": result.stderr,
                }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

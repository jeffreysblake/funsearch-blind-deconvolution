"""Mock evaluator implementations for testing and development."""

import ast
import json
import multiprocessing
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from pathlib import Path
from typing import Any, List

from ..interfaces import Evaluator, EvaluatorError


class MockEvaluator(Evaluator):
    """
    Simple in-process evaluator for testing.

    WARNING: Not secure! Only use for testing with trusted code.
    Uses multiprocessing for timeout support.
    """

    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        self._pool: multiprocessing.Pool | None = None

    def evaluate(self, program: str, test_input: Any) -> float:
        """Execute program and return fitness score."""
        try:
            # Parse code to check syntax
            ast.parse(program)

            # Run in separate process with timeout
            if self._pool is None:
                self._pool = multiprocessing.Pool(1)

            result = self._pool.apply_async(self._run_code, args=(program, test_input))
            try:
                score = result.get(timeout=self.timeout)
                return score
            except multiprocessing.TimeoutError:
                return float("-inf")  # Timeout

        except SyntaxError:
            return float("-inf")  # Invalid code
        except Exception as e:
            print(f"Evaluation error: {e}")
            return float("-inf")

    def evaluate_batch(self, programs: List[str], test_inputs: List[Any]) -> List[float]:
        """Evaluate multiple programs (sequentially in this simple version)."""
        return [self.evaluate(prog, inp) for prog, inp in zip(programs, test_inputs)]

    @staticmethod
    def _run_code(program: str, test_input: Any) -> float:
        """Execute code in subprocess."""
        # Create namespace
        namespace: dict[str, Any] = {
            "np": __import__("numpy"),
            "__builtins__": __builtins__,
        }

        # Execute program
        exec(program, namespace)

        # Call evaluate function
        if "evaluate" in namespace:
            return float(namespace["evaluate"](test_input))
        else:
            raise ValueError("No 'evaluate' function found")

    def close(self):
        """Cleanup resources."""
        if self._pool is not None:
            self._pool.close()
            self._pool.join()
            self._pool = None


class SubprocessEvaluator(Evaluator):
    """
    Evaluator using subprocess for safer execution.

    Safer than in-process but not as secure as Docker.
    Good for development on web instances.
    """

    def __init__(self, timeout: int = 30, max_workers: int = 4):
        self.timeout = timeout
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)

    def evaluate(self, program: str, test_input: Any) -> float:
        """Run code in subprocess."""
        try:
            # Check syntax first
            ast.parse(program)
        except SyntaxError:
            return float("-inf")

        # Create temporary script
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            # Write program + test harness
            f.write(program)
            f.write("\n\n")
            f.write("import json\n")
            f.write("import sys\n")
            f.write(f"test_input = {json.dumps(test_input)}\n")
            f.write("try:\n")
            f.write("    result = evaluate(test_input)\n")
            f.write("    print(json.dumps({'score': result}))\n")
            f.write("except Exception as e:\n")
            f.write("    print(json.dumps({'error': str(e)}), file=sys.stderr)\n")
            f.write("    sys.exit(1)\n")
            script_path = f.name

        try:
            # Run subprocess
            result = subprocess.run(
                ["python", script_path],
                capture_output=True,
                timeout=self.timeout,
                text=True,
            )

            if result.returncode == 0:
                # Parse output
                output = json.loads(result.stdout.strip())
                return float(output["score"])
            else:
                # Script error
                return float("-inf")

        except subprocess.TimeoutExpired:
            return float("-inf")
        except Exception:
            return float("-inf")
        finally:
            # Cleanup
            Path(script_path).unlink(missing_ok=True)

    def evaluate_batch(self, programs: List[str], test_inputs: List[Any]) -> List[float]:
        """Evaluate multiple programs in parallel using thread pool."""
        futures = [
            self.executor.submit(self.evaluate, prog, inp)
            for prog, inp in zip(programs, test_inputs)
        ]

        results = []
        for future in futures:
            try:
                score = future.result(timeout=self.timeout + 5)
                results.append(score)
            except (FuturesTimeoutError, Exception):
                results.append(float("-inf"))

        return results

    def close(self):
        """Cleanup resources."""
        self.executor.shutdown(wait=True)

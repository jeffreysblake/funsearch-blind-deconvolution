"""Simple number sequence optimization problem.

This is a minimal FunSearch example that should converge in 5-10 minutes.
Goal: Find a function that generates numbers close to the Fibonacci sequence.
"""

import funsearch
import numpy as np


def fibonacci(n: int) -> int:
    """Returns the nth Fibonacci number (ground truth for testing)."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(n - 1):
        a, b = b, a + b
    return b


@funsearch.run
def evaluate(generate_number) -> float:
    """Evaluate how well the function approximates Fibonacci numbers.

    Returns negative mean squared error (higher is better).
    """
    errors = []
    for n in range(1, 15):  # Test first 15 Fibonacci numbers
        predicted = generate_number(n)
        actual = fibonacci(n)
        error = abs(predicted - actual)
        errors.append(error)

    # Return negative MSE (we want to maximize, so higher is better)
    mse = np.mean(np.array(errors) ** 2)
    return -mse


@funsearch.evolve
def generate_number(n: int) -> int:
    """Generate the nth number in a sequence.

    Args:
        n: Position in sequence (1-indexed)

    Returns:
        The nth number
    """
    # Baseline: just return n
    # FunSearch should evolve this to approximate Fibonacci
    return n

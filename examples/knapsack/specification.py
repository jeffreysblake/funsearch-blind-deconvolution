"""Knapsack problem with heuristic optimization.

This example evolves a priority function for the 0/1 knapsack problem.
Expected convergence: 15-30 minutes with TemplateMockSampler.
"""

import funsearch
import numpy as np
from typing import List, Tuple


def generate_test_instances() -> List[Tuple[np.ndarray, np.ndarray, float]]:
    """Generate random knapsack test instances.

    Returns:
        List of (values, weights, capacity) tuples
    """
    np.random.seed(42)  # Reproducible test cases
    instances = []

    # Small instances for fast evaluation
    for _ in range(10):
        n = np.random.randint(10, 20)  # 10-20 items
        values = np.random.randint(1, 100, size=n)
        weights = np.random.randint(1, 50, size=n)
        capacity = np.sum(weights) * 0.5  # Half of total weight
        instances.append((values, weights, capacity))

    return instances


def greedy_knapsack(
    values: np.ndarray,
    weights: np.ndarray,
    capacity: float,
    priority_fn,
) -> float:
    """Solve knapsack using greedy algorithm with priority function.

    Args:
        values: Item values
        weights: Item weights
        capacity: Knapsack capacity
        priority_fn: Function that assigns priority to each item

    Returns:
        Total value of selected items
    """
    n = len(values)

    # Calculate priorities for all items
    priorities = np.array([
        priority_fn(values[i], weights[i], capacity) for i in range(n)
    ])

    # Sort items by priority (descending)
    indices = np.argsort(-priorities)

    total_value = 0.0
    total_weight = 0.0

    # Greedily add items in priority order
    for idx in indices:
        if total_weight + weights[idx] <= capacity:
            total_value += values[idx]
            total_weight += weights[idx]

    return total_value


# Pre-generate test instances
TEST_INSTANCES = generate_test_instances()


@funsearch.run
def evaluate(priority) -> float:
    """Evaluate priority function on knapsack test instances.

    Args:
        priority: Function that takes (value, weight, capacity) and returns priority

    Returns:
        Average total value across all test instances (higher is better)
    """
    total_score = 0.0

    try:
        for values, weights, capacity in TEST_INSTANCES:
            score = greedy_knapsack(values, weights, capacity, priority)
            total_score += score
    except Exception:
        # If the priority function fails, return very low score
        return -1e9

    # Return average value
    return total_score / len(TEST_INSTANCES)


@funsearch.evolve
def priority(value: float, weight: float, capacity: float) -> float:
    """Compute priority for a knapsack item.

    Args:
        value: Value of the item
        weight: Weight of the item
        capacity: Total knapsack capacity

    Returns:
        Priority score (higher = more likely to be selected)
    """
    # Baseline: value-to-weight ratio (classic greedy heuristic)
    # FunSearch should evolve better heuristics
    if weight <= 0:
        return 0.0
    return value / weight

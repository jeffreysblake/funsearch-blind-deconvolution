# Knapsack Heuristic Optimization

A realistic FunSearch example that evolves heuristics for the 0/1 knapsack problem.

## Problem

The 0/1 knapsack problem: Given items with values and weights, select a subset that:
- Maximizes total value
- Stays within weight capacity

We use a **greedy algorithm** with a **priority function**. FunSearch evolves the priority function.

## Baseline Heuristic

```python
def priority(value: float, weight: float, capacity: float) -> float:
    """Classic value-to-weight ratio."""
    return value / weight
```

**Expected Baseline Score**: ~450-500 (average value across 10 test instances)

## What FunSearch Should Discover

Better heuristics might consider:
- **Efficiency**: `value / weight`
- **Absolute value**: Sometimes high-value items are worth it even if heavy
- **Capacity utilization**: Prefer items that fit well in remaining space
- **Combinations**: `value / sqrt(weight)` or other transformations

## Expected Convergence

- **Time**: 15-30 minutes
- **Iterations**: 500-1000
- **Target Score**: > 550 (10-20% improvement over baseline)

## Test Instances

- 10 random instances
- 10-20 items each
- Capacity = 50% of total weight
- Seeded for reproducibility

## Why This Example Is Good

1. **Fast evaluation**: Each test takes milliseconds
2. **Clear metric**: Easy to see if we're improving
3. **Known heuristics**: We can verify if FunSearch discovers classic techniques
4. **Bounded search**: Priority functions are simple enough for mocks to explore

## Running

```bash
# Via CLI
python -m cli.main init knapsack-test --spec examples/knapsack/specification.py

# Via API
curl -X POST http://localhost:7351/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Knapsack Heuristic Evolution",
    "description": "Evolve priority functions for greedy knapsack",
    "problem_type": "optimization",
    "specification": {
      "file_path": "examples/knapsack/specification.py",
      "evolve_function": "priority",
      "evaluate_function": "evaluate"
    }
  }'

# Start experiment
curl -X POST http://localhost:7351/api/v1/projects/{project_id}/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "30-Minute Convergence Test",
    "config": {
      "llm": {
        "provider": "template_mock",
        "temperature": 1.0
      },
      "funsearch": {
        "samples_per_prompt": 4,
        "num_islands": 10,
        "reset_period": 1800
      },
      "execution": {
        "max_iterations": 1000,
        "checkpoint_interval": 100
      }
    }
  }'
```

## Monitoring Progress

Watch the score improve in real-time:

```bash
# WebSocket connection
websocat ws://localhost:7351/ws/experiments/{experiment_id}

# Subscribe to metrics
{"type": "subscribe", "channels": ["metrics", "best_program"]}
```

You should see:
1. Initial score: ~450-500 (baseline)
2. Gradual improvement as better heuristics evolve
3. Periodic island resets (diversity mechanism)
4. Best program updates when new heuristics are discovered

## Success Criteria

Test passes if:
1. ✅ Experiment runs without errors
2. ✅ Score improves by at least 5% over baseline
3. ✅ Completes within 30 minutes
4. ✅ Generates syntactically valid priority functions
5. ✅ Islands maintain diversity (different heuristics)

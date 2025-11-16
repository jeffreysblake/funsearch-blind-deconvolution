# Number Sequence Optimization Example

A minimal FunSearch example for testing the framework.

## Problem

Evolve a function `generate_number(n)` that approximates the Fibonacci sequence without explicitly computing it.

## Baseline

```python
def generate_number(n: int) -> int:
    return n  # Just return the position
```

**Baseline Score**: ~-15000 (high error)

## Goal

Find a function that produces numbers closer to the Fibonacci sequence.

## Expected Convergence

- **Time**: 5-10 minutes
- **Iterations**: 100-500
- **Target Score**: > -1000 (much better than baseline)

## Why This Works

The TemplateMockSampler has templates for generating mathematical expressions like:
- `n * 2`
- `n ** 2`
- Recursive patterns
- Fibonacci-like recurrence relations

The evolutionary algorithm should discover progressively better approximations.

## Running

```bash
# Create project from this specification
python -m cli.main init number-sequence --spec examples/number_sequence/specification.py

# Start experiment via API
curl -X POST http://localhost:7351/api/v1/projects/{project_id}/experiments \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Quick Convergence Test",
    "config": {
      "llm": {"provider": "template_mock"},
      "funsearch": {
        "samples_per_prompt": 4,
        "num_islands": 5,
        "max_iterations": 500
      }
    }
  }'
```

## Success Criteria

The test passes if:
1. Experiment completes without errors
2. Score improves significantly from baseline
3. Converges within 10 minutes

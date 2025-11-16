"""Templates API endpoints."""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class TemplateInfo(BaseModel):
    """Project template information."""

    id: str
    name: str
    description: str
    example_problems: list[str] = []


class TemplateDetail(TemplateInfo):
    """Detailed template with code."""

    specification_template: str
    default_config: dict
    example: dict = {}


# Template data
TEMPLATES = {
    "algorithm_synthesis": TemplateInfo(
        id="algorithm_synthesis",
        name="Algorithm Synthesis",
        description="Generate and optimize algorithms (e.g., bin packing, scheduling)",
        example_problems=["bin_packing", "online_scheduling", "load_balancing"],
    ),
    "mathematical_optimization": TemplateInfo(
        id="mathematical_optimization",
        name="Mathematical Optimization",
        description="Optimize mathematical functions and combinatorial problems",
        example_problems=["cap_set", "admissible_set", "graph_coloring"],
    ),
    "signal_processing": TemplateInfo(
        id="signal_processing",
        name="Signal Processing",
        description="Optimize signal processing algorithms",
        example_problems=["lucy_richardson", "wiener_filter", "edge_detection"],
    ),
}


@router.get("/templates", response_model=list[TemplateInfo])
async def list_templates():
    """
    List available project templates.
    """
    return list(TEMPLATES.values())


@router.get("/templates/{template_id}", response_model=TemplateDetail)
async def get_template(template_id: str):
    """
    Get template details with example code.
    """
    if template_id not in TEMPLATES:
        raise HTTPException(status_code=404, detail="Template not found")

    template = TEMPLATES[template_id]

    # Generate specification template
    if template_id == "algorithm_synthesis":
        spec_template = '''"""Algorithm synthesis problem."""

import funsearch
import numpy as np


@funsearch.run
def evaluate(priority_fn) -> float:
    """Evaluate the priority function on test cases."""
    # TODO: Implement evaluation logic
    score = 0.0

    # Test on multiple instances
    for test_case in generate_test_cases():
        result = run_algorithm(priority_fn, test_case)
        score += result

    return score / len(test_cases)


@funsearch.evolve
def priority(item: float, bins: np.ndarray, capacity: float) -> float:
    """
    Assign priority to item for bin selection.

    Higher priority = more likely to be selected.
    """
    return item  # Simple baseline - evolve this!
'''
    elif template_id == "signal_processing":
        spec_template = '''"""Signal processing optimization."""

import funsearch
import numpy as np


@funsearch.run
def evaluate(stopping_criterion_fn) -> float:
    """Evaluate the stopping criterion on test images."""
    # TODO: Implement evaluation logic
    total_score = 0.0

    for test_image in load_test_images():
        iterations, quality = run_deconvolution(stopping_criterion_fn, test_image)
        # Balance quality vs computational cost
        score = quality / np.sqrt(iterations)
        total_score += score

    return total_score / len(test_images)


@funsearch.evolve
def stopping_criterion(iteration: int, psnr: float, psnr_delta: float) -> bool:
    """
    Determine when to stop iterative algorithm.

    Returns True to stop, False to continue.
    """
    # Simple baseline - evolve this!
    return iteration > 100 or psnr_delta < 0.01
'''
    else:
        spec_template = '''"""Mathematical optimization problem."""

import funsearch
import numpy as np


@funsearch.run
def evaluate(construction_fn) -> float:
    """Evaluate the construction function."""
    # TODO: Implement evaluation logic
    result = construction_fn()
    return len(result)  # Or other metric


@funsearch.evolve
def construct() -> np.ndarray:
    """
    Construct solution to the problem.
    """
    # Simple baseline - evolve this!
    return np.array([])
'''

    # Default config
    default_config = {
        "llm": {
            "provider": "template_mock",
            "model": "mock-gpt-4",
            "temperature": 1.0,
            "max_tokens": 512,
        },
        "sandbox": {"provider": "subprocess", "max_workers": 4, "timeout": 30},
        "funsearch": {
            "samples_per_prompt": 4,
            "num_islands": 10,
            "reset_period": 80000,
        },
        "execution": {"max_iterations": 100000, "checkpoint_interval": 1000},
    }

    return TemplateDetail(
        id=template.id,
        name=template.name,
        description=template.description,
        example_problems=template.example_problems,
        specification_template=spec_template,
        default_config=default_config,
        example={
            "problem": template.example_problems[0] if template.example_problems else "example"
        },
    )

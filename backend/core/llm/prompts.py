"""Prompt templates for different problem types."""

from typing import Optional


class PromptTemplate:
    """Template for generating prompts for different problem domains."""

    def __init__(
        self,
        name: str,
        description: str,
        instruction: str,
        examples: Optional[list[str]] = None,
    ):
        """Initialize prompt template.

        Args:
            name: Template name
            description: What this template is for
            instruction: Instruction to prepend to code
            examples: Optional example completions
        """
        self.name = name
        self.description = description
        self.instruction = instruction
        self.examples = examples or []

    def format_prompt(self, code: str) -> str:
        """Format code prompt with instruction.

        Args:
            code: Code to complete

        Returns:
            Formatted prompt with instruction
        """
        parts = []

        # Add instruction
        if self.instruction:
            parts.append(f"# {self.instruction}\n")

        # Add examples if available
        if self.examples:
            parts.append("# Examples of good implementations:\n")
            for example in self.examples[:2]:  # Limit to 2 examples
                parts.append(f"# {example}\n")
            parts.append("\n")

        # Add the actual code
        parts.append(code)

        return "".join(parts)


# Predefined templates for different problem types

ALGORITHM_SYNTHESIS_TEMPLATE = PromptTemplate(
    name="algorithm_synthesis",
    description="For synthesizing algorithms (e.g., bin packing, cap set)",
    instruction="Complete this function to implement an efficient algorithm. Focus on correctness and performance.",
    examples=[
        "Use greedy heuristics when appropriate",
        "Consider edge cases and boundary conditions",
        "Optimize for the given constraints",
    ],
)

MATHEMATICAL_OPTIMIZATION_TEMPLATE = PromptTemplate(
    name="mathematical_optimization",
    description="For mathematical optimization problems",
    instruction="Complete this function to maximize/minimize the objective. Use mathematical insights.",
    examples=[
        "Consider mathematical properties of the problem",
        "Use closed-form solutions when possible",
        "Balance exploration and exploitation",
    ],
)

HEURISTIC_DESIGN_TEMPLATE = PromptTemplate(
    name="heuristic_design",
    description="For designing priority/scoring heuristics",
    instruction="Complete this heuristic function. Return a score where higher values indicate better priority.",
    examples=[
        "Combine multiple factors (value, weight, capacity, etc.)",
        "Use mathematical transformations (sqrt, log, exp, etc.)",
        "Consider edge cases (division by zero, negative values)",
    ],
)

SEQUENCE_GENERATION_TEMPLATE = PromptTemplate(
    name="sequence_generation",
    description="For generating sequences or patterns",
    instruction="Complete this function to generate the nth element in a sequence.",
    examples=[
        "Look for mathematical patterns (arithmetic, geometric, recursive)",
        "Consider using closed-form formulas when possible",
        "Handle base cases explicitly",
    ],
)

SIGNAL_PROCESSING_TEMPLATE = PromptTemplate(
    name="signal_processing",
    description="For signal processing and deconvolution",
    instruction="Complete this function for signal processing. Focus on numerical stability.",
    examples=[
        "Use numerical methods appropriate for the problem",
        "Consider convergence criteria",
        "Handle boundary conditions carefully",
    ],
)

GENERAL_TEMPLATE = PromptTemplate(
    name="general",
    description="General-purpose template",
    instruction="Complete this function. Write clear, correct, and efficient code.",
    examples=[],
)


# Template registry
TEMPLATES = {
    "algorithm_synthesis": ALGORITHM_SYNTHESIS_TEMPLATE,
    "mathematical_optimization": MATHEMATICAL_OPTIMIZATION_TEMPLATE,
    "heuristic_design": HEURISTIC_DESIGN_TEMPLATE,
    "sequence_generation": SEQUENCE_GENERATION_TEMPLATE,
    "signal_processing": SIGNAL_PROCESSING_TEMPLATE,
    "general": GENERAL_TEMPLATE,
}


def get_template_for_problem(problem_type: str) -> PromptTemplate:
    """Get appropriate prompt template for problem type.

    Args:
        problem_type: Type of problem (matches project.problem_type)

    Returns:
        Appropriate PromptTemplate
    """
    # Map problem types to templates
    type_mapping = {
        "optimization": "mathematical_optimization",
        "synthesis": "algorithm_synthesis",
        "search": "heuristic_design",
        "signal_processing": "signal_processing",
        "sequence": "sequence_generation",
    }

    template_name = type_mapping.get(problem_type, "general")
    return TEMPLATES.get(template_name, GENERAL_TEMPLATE)


def create_custom_template(
    instruction: str,
    examples: Optional[list[str]] = None,
) -> PromptTemplate:
    """Create a custom prompt template.

    Args:
        instruction: Custom instruction
        examples: Optional examples

    Returns:
        Custom PromptTemplate
    """
    return PromptTemplate(
        name="custom",
        description="Custom template",
        instruction=instruction,
        examples=examples or [],
    )

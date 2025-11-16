"""LLM implementations for FunSearch."""

from .lm_studio import LMStudioSampler
from .prompts import PromptTemplate, get_template_for_problem

__all__ = ["LMStudioSampler", "PromptTemplate", "get_template_for_problem"]

"""
Typed contracts for the email classifier feature.

PromptConfig is loaded from a versioned YAML file (see /prompts).
ClassificationOutput is the structured, validated output of the LLM call.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Category(str, Enum):
    BILLING = "billing"
    TECHNICAL = "technical"
    ACCOUNT = "account"
    GENERAL = "general"


class FewShotExample(BaseModel):
    input: str
    output: "ClassificationOutput"


class ModelParameters(BaseModel):
    temperature: float = 0.0
    max_tokens: int = 200


class PromptConfig(BaseModel):
    """The full, versioned configuration for one prompt variant."""

    version_id: str
    timestamp: datetime
    model: str
    description: Optional[str] = None
    system_prompt: str
    few_shot_examples: list[FewShotExample] = Field(default_factory=list)
    model_parameters: ModelParameters = Field(default_factory=ModelParameters)


class ClassificationOutput(BaseModel):
    """The structured output the LLM must produce for every email."""

    category: Category
    summary: str = Field(..., min_length=1, max_length=300)


# Needed because FewShotExample references ClassificationOutput before it's defined
FewShotExample.model_rebuild()
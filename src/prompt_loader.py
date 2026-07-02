"""Loads a versioned prompt YAML file into a validated PromptConfig."""

from pathlib import Path

import yaml

from src.schemas import PromptConfig


def load_prompt_config(path: str | Path) -> PromptConfig:
    """
    Read a prompt YAML file (see /prompts/email_classifier_v1.yaml) and
    validate it into a PromptConfig object.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    # few_shot_examples in YAML are {input, output: {category, summary}}
    # PromptConfig expects the same shape, Pydantic will validate nested models.
    return PromptConfig(**raw)
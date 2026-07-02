"""
The LLM feature under test: a customer support email classifier.

This wraps a single Groq API call behind a clean function. The prompt itself
is NOT hardcoded here -- it's injected via a PromptConfig, loaded from a
versioned YAML file. This is what lets the eval pipeline swap prompt
versions without touching this code.
"""

import json
import os

from groq import Groq

from src.schemas import ClassificationOutput, PromptConfig

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY environment variable is not set. "
                "Run: set GROQ_API_KEY=your-key-here"
            )
        _client = Groq(api_key=api_key)
    return _client


def _build_messages(config: PromptConfig, email_text: str) -> list[dict]:
    messages = [{"role": "system", "content": config.system_prompt}]

    for example in config.few_shot_examples:
        messages.append({"role": "user", "content": example.input})
        messages.append(
            {
                "role": "assistant",
                "content": json.dumps(
                    {
                        "category": example.output.category.value,
                        "summary": example.output.summary,
                    }
                ),
            }
        )

    messages.append({"role": "user", "content": email_text})
    return messages


def classify_email(email_text: str, config: PromptConfig) -> ClassificationOutput:
    """
    Classify a single customer support email using the given prompt config.

    Returns a validated ClassificationOutput (category + summary).
    """
    client = _get_client()
    messages = _build_messages(config, email_text)

    response = client.chat.completions.create(
        model=config.model,
        messages=messages,
        temperature=config.model_parameters.temperature,
        max_tokens=config.model_parameters.max_tokens,
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content

    try:
        parsed = json.loads(raw_content)
        return ClassificationOutput(**parsed)
    except (json.JSONDecodeError, TypeError) as e:
        raise ValueError(
            f"Model did not return valid JSON matching ClassificationOutput.\n"
            f"Raw response: {raw_content}\nError: {e}"
        )
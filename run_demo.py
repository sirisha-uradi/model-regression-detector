"""
Quick manual smoke test for Phase 1.

Usage:
    set GROQ_API_KEY=your-key-here
    python run_demo.py
"""

from src.classifier import classify_email
from src.prompt_loader import load_prompt_config

if __name__ == "__main__":
    config = load_prompt_config("prompts/email_classifier_v1.yaml")

    test_email = (
        "Hey, I've been trying to log in for 2 days and it keeps saying "
        "'invalid password' even though I just reset it. Super frustrating."
    )

    result = classify_email(test_email, config)

    print(f"Prompt version: {config.version_id}")
    print(f"Category: {result.category.value}")
    print(f"Summary: {result.summary}")
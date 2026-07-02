"""
Phase 3: The evaluation engine.

Runs every test case in the golden dataset through the classifier,
scores each one against the expected category, and prints a summary report.
"""

import json
from pathlib import Path

from src.classifier import classify_email
from src.prompt_loader import load_prompt_config


def load_golden_dataset(path: str = "data/golden_dataset.json") -> list[dict]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_evaluation(prompt_config_path: str = "prompts/email_classifier_v1.yaml"):
    config = load_prompt_config(prompt_config_path)
    dataset = load_golden_dataset()

    results = []
    passed = 0
    failed = 0

    print(f"Running evaluation with prompt version: {config.version_id}")
    print(f"Testing {len(dataset)} cases...\n")

    for case in dataset:
        try:
            output = classify_email(case["email"], config)
            actual_category = output.category.value
            expected_category = case["expected_category"]
            is_correct = actual_category == expected_category

            if is_correct:
                passed += 1
                status = "PASS"
            else:
                failed += 1
                status = "FAIL"

            results.append(
                {
                    "id": case["id"],
                    "status": status,
                    "expected_category": expected_category,
                    "actual_category": actual_category,
                    "actual_summary": output.summary,
                    "difficulty": case["difficulty"],
                }
            )

            print(f"[{status}] {case['id']} (difficulty: {case['difficulty']})")
            if not is_correct:
                print(f"       Expected: {expected_category} | Got: {actual_category}")

        except Exception as e:
            failed += 1
            results.append(
                {
                    "id": case["id"],
                    "status": "ERROR",
                    "error": str(e),
                }
            )
            print(f"[ERROR] {case['id']}: {e}")

    total = len(dataset)
    pass_rate = (passed / total) * 100 if total else 0

    print("\n" + "=" * 50)
    print(f"RESULTS: {passed}/{total} passed ({pass_rate:.1f}%)")
    print("=" * 50)

    # Save full results to a file so we can compare against future runs
    output_path = Path("data/last_run_results.json")
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(
            {
                "prompt_version": config.version_id,
                "passed": passed,
                "failed": failed,
                "total": total,
                "pass_rate": pass_rate,
                "results": results,
            },
            f,
            indent=2,
        )
    print(f"\nFull results saved to {output_path}")

    return results


if __name__ == "__main__":
    run_evaluation()
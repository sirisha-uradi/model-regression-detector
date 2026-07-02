"""
Phase 3 (continued): The comparison / diffing engine.

Compares a baseline run against a new run and reports:
- overall pass rate delta
- specific cases that flipped from PASS -> FAIL (regressions)
- specific cases that flipped from FAIL -> PASS (improvements)
"""

import json


def load_results(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def compare_runs(baseline_path: str, new_path: str):
    baseline = load_results(baseline_path)
    new = load_results(new_path)

    baseline_by_id = {r["id"]: r for r in baseline["results"]}
    new_by_id = {r["id"]: r for r in new["results"]}

    regressions = []
    improvements = []
    unchanged_pass = []
    unchanged_fail = []

    all_ids = set(baseline_by_id.keys()) | set(new_by_id.keys())

    for case_id in sorted(all_ids):
        old = baseline_by_id.get(case_id)
        curr = new_by_id.get(case_id)

        if old is None or curr is None:
            continue

        old_pass = old["status"] == "PASS"
        new_pass = curr["status"] == "PASS"

        if old_pass and not new_pass:
            regressions.append((case_id, old, curr))
        elif not old_pass and new_pass:
            improvements.append((case_id, old, curr))
        elif old_pass and new_pass:
            unchanged_pass.append(case_id)
        else:
            unchanged_fail.append(case_id)

    print("=" * 60)
    print(f"COMPARING: {baseline['prompt_version']} (baseline) -> {new['prompt_version']} (new)")
    print("=" * 60)
    print(f"Baseline pass rate: {baseline['pass_rate']:.1f}% ({baseline['passed']}/{baseline['total']})")
    print(f"New pass rate:      {new['pass_rate']:.1f}% ({new['passed']}/{new['total']})")

    delta = new["pass_rate"] - baseline["pass_rate"]
    sign = "+" if delta >= 0 else ""
    print(f"Delta:              {sign}{delta:.1f} percentage points")
    print()

    if regressions:
        print(f"REGRESSIONS ({len(regressions)}) - used to pass, now fail:")
        for case_id, old, curr in regressions:
            print(f"   - {case_id}: expected '{curr['expected_category']}', now got '{curr['actual_category']}'")
    else:
        print("No regressions detected.")

    print()

    if improvements:
        print(f"IMPROVEMENTS ({len(improvements)}) - used to fail, now pass:")
        for case_id, old, curr in improvements:
            print(f"   - {case_id}: now correctly classified as '{curr['actual_category']}'")
    else:
        print("No new improvements.")

    print()
    print(f"Unchanged (still passing): {len(unchanged_pass)}")
    print(f"Unchanged (still failing): {len(unchanged_fail)}")
    print("=" * 60)

    if abs(delta) >= 8:
        print("STATUS: CRITICAL - pass rate changed by 8+ points")
    elif abs(delta) >= 3:
        print("STATUS: WARNING - pass rate changed by 3+ points")
    else:
        print("STATUS: OK - change within normal noise threshold")

    return {
        "regressions": regressions,
        "improvements": improvements,
        "delta": delta,
    }


if __name__ == "__main__":
    compare_runs(
        baseline_path="data/baseline_v1_results.json",
        new_path="data/last_run_results.json",
    )
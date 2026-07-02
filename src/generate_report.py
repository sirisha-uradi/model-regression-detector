"""
Phase 4: Generates an HTML diff report comparing a baseline run to a new run.

Produces a self-contained HTML file you can open in any browser -- shows
a scorecard, and a table of every test case with old vs new status.
"""

import json
from pathlib import Path


def load_results(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def generate_report(
    baseline_path: str = "data/baseline_v1_results.json",
    new_path: str = "data/last_run_results.json",
    output_path: str = "data/report.html",
):
    baseline = load_results(baseline_path)
    new = load_results(new_path)

    baseline_by_id = {r["id"]: r for r in baseline["results"]}
    new_by_id = {r["id"]: r for r in new["results"]}

    all_ids = sorted(set(baseline_by_id.keys()) | set(new_by_id.keys()))

    delta = new["pass_rate"] - baseline["pass_rate"]
    delta_sign = "+" if delta >= 0 else ""

    if abs(delta) >= 8:
        status_label = "CRITICAL"
        status_color = "#dc2626"
    elif abs(delta) >= 3:
        status_label = "WARNING"
        status_color = "#d97706"
    else:
        status_label = "OK"
        status_color = "#16a34a"

    rows_html = ""
    for case_id in all_ids:
        old = baseline_by_id.get(case_id)
        curr = new_by_id.get(case_id)

        old_status = old["status"] if old else "N/A"
        new_status = curr["status"] if curr else "N/A"

        if old_status == "PASS" and new_status == "FAIL":
            row_class = "regression"
            flag = "REGRESSION"
        elif old_status == "FAIL" and new_status == "PASS":
            row_class = "improvement"
            flag = "IMPROVED"
        else:
            row_class = ""
            flag = ""

        expected = curr.get("expected_category", "-") if curr else "-"
        old_actual = old.get("actual_category", "-") if old else "-"
        new_actual = curr.get("actual_category", "-") if curr else "-"

        rows_html += f"""
        <tr class="{row_class}">
            <td>{case_id}</td>
            <td>{expected}</td>
            <td>{old_actual} ({old_status})</td>
            <td>{new_actual} ({new_status})</td>
            <td>{flag}</td>
        </tr>
        """

    html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Model Regression Report</title>
<style>
    body {{ font-family: Arial, sans-serif; margin: 40px; background: #f8fafc; color: #1e293b; }}
    h1 {{ margin-bottom: 4px; }}
    .subtitle {{ color: #64748b; margin-bottom: 24px; }}
    .scorecard {{ display: flex; gap: 16px; margin-bottom: 24px; }}
    .card {{ background: white; border-radius: 8px; padding: 16px 24px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    .card .label {{ font-size: 12px; color: #64748b; text-transform: uppercase; }}
    .card .value {{ font-size: 24px; font-weight: bold; }}
    .status-badge {{ display: inline-block; padding: 4px 12px; border-radius: 999px; color: white; font-weight: bold; background: {status_color}; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
    th, td {{ text-align: left; padding: 10px 14px; border-bottom: 1px solid #e2e8f0; font-size: 14px; }}
    th {{ background: #f1f5f9; }}
    tr.regression {{ background: #fef2f2; }}
    tr.improvement {{ background: #f0fdf4; }}
</style>
</head>
<body>
    <h1>Model Regression Report</h1>
    <div class="subtitle">Comparing prompt <b>{baseline['prompt_version']}</b> (baseline) vs <b>{new['prompt_version']}</b> (new)</div>

    <div class="scorecard">
        <div class="card"><div class="label">Baseline Pass Rate</div><div class="value">{baseline['pass_rate']:.1f}%</div></div>
        <div class="card"><div class="label">New Pass Rate</div><div class="value">{new['pass_rate']:.1f}%</div></div>
        <div class="card"><div class="label">Delta</div><div class="value">{delta_sign}{delta:.1f} pts</div></div>
        <div class="card"><div class="label">Status</div><div class="value"><span class="status-badge">{status_label}</span></div></div>
    </div>

    <table>
        <tr>
            <th>Test Case</th>
            <th>Expected</th>
            <th>Baseline Result</th>
            <th>New Result</th>
            <th>Change</th>
        </tr>
        {rows_html}
    </table>
</body>
</html>
"""

    Path(output_path).write_text(html, encoding="utf-8")
    print(f"Report generated: {output_path}")
    print(f"Open it by double-clicking the file in File Explorer.")


if __name__ == "__main__":
    generate_report()
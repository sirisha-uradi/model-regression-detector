# Model Regression Detector

A CI/CD pipeline for LLM prompts. Every time a prompt changes, this system automatically re-tests it against a hand-labeled golden dataset, flags any regressions (cases that used to pass and now fail), and generates a visual diff report -- all before the change reaches production.

## The problem this solves

Most teams change LLM prompts the same way: edit the string, deploy, hope nothing broke. There's no automated way to know if a "small fix" to handle one edge case just silently broke five other cases. This project brings the same discipline software engineers already apply to code -- automated regression testing -- to prompt engineering.

## How it works

1. **The feature under test**: a customer support email classifier (Groq + Llama 3.3) that categorizes emails into billing/technical/account/general and writes a one-line summary.
2. **The golden dataset**: 10 hand-labeled test emails with known-correct answers, including deliberately tricky cases (sarcasm, typos, mixed intent, ambiguous wording).
3. **The eval engine**: runs every test case through the classifier, scores pass/fail against expected output, and saves results.
4. **The regression detector**: diffs any two eval runs and reports exactly which cases flipped from pass to fail (regression) or fail to pass (improvement), plus an overall pass-rate delta with warning/critical thresholds.
5. **The reporting layer**: generates a standalone HTML report with a scorecard and full case-by-case diff table.
6. **CI/CD**: a GitHub Actions workflow automatically re-runs the full eval suite whenever a prompt file changes, using a securely stored API key.

## Real example from this repo

Prompt v1 scored 80% (8/10) on the golden dataset, failing on a sarcastic complaint and a mixed billing/technical email -- both misclassified as "technical" when the customer's real intent was billing. After adding an explicit tie-breaking rule and two new few-shot examples, v2 scored 100% (10/10) with zero regressions. The full before/after diff is in data/report.html.

## Project structure

model-regression-detector/
├── .github/workflows/eval.yml   # CI/CD pipeline definition
├── prompts/                     # Versioned prompt configs (v1, v2, ...)
├── data/
│   ├── golden_dataset.json      # Hand-labeled ground truth test cases
│   ├── baseline_v1_results.json # Saved baseline for comparison
│   ├── last_run_results.json    # Most recent eval run
│   └── report.html              # Generated visual diff report
├── src/
│   ├── schemas.py                # Pydantic contracts (PromptConfig, ClassificationOutput)
│   ├── prompt_loader.py          # Loads YAML prompt configs
│   ├── classifier.py             # The LLM feature under test
│   ├── eval_runner.py            # Runs golden dataset through classifier, scores results
│   ├── compare_runs.py           # Diffs two eval runs, flags regressions
│   └── generate_report.py        # Builds the HTML report
├── requirements.txt
└── run_demo.py                   # Quick single-email smoke test

## Running it locally

pip install -r requirements.txt
set GROQ_API_KEY=your-key-here          # Windows
export GROQ_API_KEY=your-key-here       # Mac/Linux
python -m src.eval_runner
python -c "from src.eval_runner import run_evaluation; run_evaluation('prompts/email_classifier_v2.yaml')"
python -m src.compare_runs
python -m src.generate_report

## Adding a new test case

Add an entry to data/golden_dataset.json with a unique id, the email text, expected_category, expected_summary, a difficulty tag, and a notes field explaining why the case matters. Prioritize edge cases -- that's where regressions hide.

## Adding a new prompt version

Create a new file in prompts/ (e.g. email_classifier_v3.yaml), following the same schema as v1/v2. Bump version_id. Run the eval engine against it and compare against the current baseline before promoting it.

## CI/CD

.github/workflows/eval.yml runs automatically on any push that touches /prompts, and can also be triggered manually from the Actions tab. It installs dependencies, runs the eval against the golden dataset, compares against baseline, and uploads results as a downloadable artifact -- using a GROQ_API_KEY stored as a GitHub repository secret.

## Design decisions

- **Why a golden dataset instead of just spot-checking?** Manual spot-checks don't scale and don't catch regressions in cases you didn't think to re-check. A fixed dataset means every prompt change gets tested against the exact same bar.
- **Why track pass/fail thresholds (warning at 3%, critical at 8%) instead of just reporting the delta?** Small fluctuations can be noise. Explicit thresholds force a decision: is this change worth a second look before merging?
- **Why flag large positive deltas as critical too?** A prompt that suddenly jumps from 80% to 100% deserves scrutiny, not just celebration -- it could mean the change overfit to the visible test cases rather than generalizing.
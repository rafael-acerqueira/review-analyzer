from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any

from app.utils.prompts import suggestion_prompt_template


VALID_STATUSES = {"Accepted", "Rejected"}
VALID_SENTIMENTS = {"POSITIVE", "NEGATIVE", "NEUTRAL"}
REQUIRED_GROUPS = {
    "short_generic",
    "specific_positive",
    "negative_well_written",
    "prompt_injection",
    "ambiguous_mixed",
}
REQUIRED_FIELDS = {
    "id": str,
    "group": str,
    "review": str,
    "expected_status": str,
    "expected_sentiment": str,
    "suggestion_required": bool,
    "notes": str,
}
REQUIRED_PROMPT_PHRASES = [
    "Do NOT invent facts",
    "guidance for improving the review",
    "not a finished review written for the user",
    "if this matches your experience",
    "UNTRUSTED_REVIEW_TEXT",
    "examples_used",
]
REQUIRED_BASELINE_CORE_METRICS = {
    "status_accuracy",
    "suggestion_presence_accuracy",
    "feedback_length_accuracy",
    "output_contract_accuracy",
    "error_rate",
}
REQUIRED_BASELINE_SECONDARY_METRICS = {
    "sentiment_accuracy",
    "suggestion_guidance_safety",
}


def _evals_dir() -> Path:
    return Path(__file__).resolve().parent


def _load_dataset(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} is not valid JSON: {exc}") from exc

    if not isinstance(data, list):
        raise ValueError("review eval dataset must be a JSON list")
    if not data:
        raise ValueError("review eval dataset must not be empty")

    return data


def _validate_dataset(data: list[dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    groups: set[str] = set()

    for index, item in enumerate(data):
        prefix = f"case[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{prefix}: must be an object")
            continue

        for field, expected_type in REQUIRED_FIELDS.items():
            if field not in item:
                errors.append(f"{prefix}: missing field {field!r}")
                continue
            if not isinstance(item[field], expected_type):
                errors.append(f"{prefix}: field {field!r} must be {expected_type.__name__}")

        case_id = item.get("id")
        if isinstance(case_id, str):
            if case_id in seen_ids:
                errors.append(f"{prefix}: duplicate id {case_id!r}")
            seen_ids.add(case_id)

        group = item.get("group")
        if isinstance(group, str):
            groups.add(group)

        status = item.get("expected_status")
        if status not in VALID_STATUSES:
            errors.append(f"{prefix}: expected_status must be one of {sorted(VALID_STATUSES)}")

        sentiment = item.get("expected_sentiment")
        if sentiment not in VALID_SENTIMENTS:
            errors.append(f"{prefix}: expected_sentiment must be one of {sorted(VALID_SENTIMENTS)}")

        review = item.get("review")
        if isinstance(review, str) and not review.strip():
            errors.append(f"{prefix}: review must not be blank")

    missing_groups = REQUIRED_GROUPS - groups
    if missing_groups:
        errors.append(f"dataset is missing required groups: {sorted(missing_groups)}")

    return errors


def _validate_python_syntax(paths: list[Path]) -> list[str]:
    errors = []
    for path in paths:
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            errors.append(f"{path}: invalid Python syntax: {exc}")
    return errors


def _validate_prompt_contract() -> list[str]:
    prompt = suggestion_prompt_template(
        review_text="Good product.",
        examples_block="NO_EXAMPLES_FOUND",
    )
    return [
        f"prompt is missing required phrase: {phrase!r}"
        for phrase in REQUIRED_PROMPT_PHRASES
        if phrase not in prompt
    ]


def _validate_baseline(path: Path, *, dataset_size: int) -> list[str]:
    try:
        baseline = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{path} is not valid JSON: {exc}"]

    errors = []
    if not isinstance(baseline, dict):
        return ["baseline must be a JSON object"]

    if baseline.get("dataset_cases") != dataset_size:
        errors.append(
            f"baseline dataset_cases must be {dataset_size}, got {baseline.get('dataset_cases')!r}"
        )

    core_metrics = baseline.get("core_metrics")
    if not isinstance(core_metrics, dict):
        errors.append("baseline core_metrics must be an object")
    else:
        missing = REQUIRED_BASELINE_CORE_METRICS - set(core_metrics)
        if missing:
            errors.append(f"baseline is missing core metrics: {sorted(missing)}")

    secondary_metrics = baseline.get("secondary_metrics")
    if not isinstance(secondary_metrics, dict):
        errors.append("baseline secondary_metrics must be an object")
    else:
        missing = REQUIRED_BASELINE_SECONDARY_METRICS - set(secondary_metrics)
        if missing:
            errors.append(f"baseline is missing secondary metrics: {sorted(missing)}")

    return errors


def main() -> int:
    evals_dir = _evals_dir()
    dataset_path = evals_dir / "review_eval_dataset.json"
    baseline_path = evals_dir / "baselines" / "current.json"
    data = _load_dataset(dataset_path)

    errors = []
    errors.extend(_validate_dataset(data))
    errors.extend(
        _validate_python_syntax(
            [
                evals_dir / "run_review_eval.py",
                evals_dir / "run_sentiment_model_eval.py",
            ]
        )
    )
    errors.extend(_validate_prompt_contract())
    errors.extend(_validate_baseline(baseline_path, dataset_size=len(data)))

    if errors:
        print("Eval smoke check failed")
        print()
        for error in errors:
            print(f"- {error}")
        return 1

    print("Eval smoke check passed")
    print(f"Dataset cases: {len(data)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

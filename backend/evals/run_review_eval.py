from __future__ import annotations

import argparse
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALID_STATUSES = {"Accepted", "Rejected"}
CORE_THRESHOLDS = {
    "status_accuracy": 95.0,
    "suggestion_presence_accuracy": 95.0,
    "feedback_length_accuracy": 100.0,
    "output_contract_accuracy": 100.0,
    "error_rate": 0.0,
}
SECONDARY_THRESHOLDS = {
    "sentiment_accuracy": 90.0,
    "suggestion_guidance_safety": 90.0,
}
GUIDANCE_TERMS = {
    "add",
    "mention",
    "describe",
    "include",
    "explain",
    "consider",
    "try",
    "focus",
    "clarify",
    "provide",
}
CONDITIONAL_TERMS = {
    "if",
    "such as",
    "for example",
    "consider",
    "could",
    "try",
    "when",
}


@dataclass(frozen=True)
class EvalCase:
    id: str
    group: str
    review: str
    expected_status: str
    expected_sentiment: str
    suggestion_required: bool
    notes: str = ""


def _default_dataset_path() -> Path:
    return Path(__file__).with_name("review_eval_dataset.json")


def _default_results_dir() -> Path:
    return Path(__file__).with_name("results")


def _load_dataset(path: Path) -> list[EvalCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [EvalCase(**item) for item in data]


def _suggestion_presence_passed(actual_status: str | None, suggestion: str, expected_required: bool) -> bool:
    has_suggestion = bool((suggestion or "").strip())

    if expected_required:
        return has_suggestion

    if actual_status == "Accepted":
        return not has_suggestion

    return True


def _suggestion_guidance_safe(actual_status: str | None, suggestion: str, expected_required: bool) -> bool:
    text = (suggestion or "").strip()
    if actual_status == "Accepted" or not expected_required:
        return True
    if not text:
        return False

    lowered = text.lower()
    has_guidance = any(term in lowered for term in GUIDANCE_TERMS)
    has_conditional = any(term in lowered for term in CONDITIONAL_TERMS)
    looks_like_finished_review = lowered.startswith(("the ", "this ", "i ", "my "))

    return has_guidance and (has_conditional or not looks_like_finished_review)


def _pct(passed: int, total: int) -> float:
    return round((passed / total) * 100, 2) if total else 0.0


def _summarize(items: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(items)
    summary = {
        "total": total,
        "status_accuracy": _pct(sum(1 for item in items if item["checks"]["status_passed"]), total),
        "sentiment_accuracy": _pct(sum(1 for item in items if item["checks"]["sentiment_passed"]), total),
        "suggestion_presence_accuracy": _pct(
            sum(1 for item in items if item["checks"]["suggestion_presence_passed"]),
            total,
        ),
        "feedback_length_accuracy": _pct(
            sum(1 for item in items if item["checks"]["feedback_length_passed"]),
            total,
        ),
        "output_contract_accuracy": _pct(
            sum(1 for item in items if item["checks"]["output_contract_passed"]),
            total,
        ),
        "suggestion_guidance_safety": _pct(
            sum(1 for item in items if item["checks"]["suggestion_guidance_safe"]),
            total,
        ),
        "error_rate": round(
            (sum(1 for item in items if item["error"] is not None) / total) * 100,
            2,
        ) if total else 0.0,
        "avg_latency_ms": round(
            sum(item["latency_ms"] for item in items) / total,
            2,
        ) if total else 0.0,
    }

    groups: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        groups.setdefault(item["group"], []).append(item)

    summary["by_group"] = {
        group: {
            "total": len(group_items),
            "status_accuracy": _pct(
                sum(1 for item in group_items if item["checks"]["status_passed"]),
                len(group_items),
            ),
            "sentiment_accuracy": _pct(
                sum(1 for item in group_items if item["checks"]["sentiment_passed"]),
                len(group_items),
            ),
            "suggestion_presence_accuracy": _pct(
                sum(1 for item in group_items if item["checks"]["suggestion_presence_passed"]),
                len(group_items),
            ),
            "suggestion_guidance_safety": _pct(
                sum(1 for item in group_items if item["checks"]["suggestion_guidance_safe"]),
                len(group_items),
            ),
        }
        for group, group_items in sorted(groups.items())
    }

    return summary


def _evaluate_case(use_case: Any, invalid_review_error: type[Exception], case: EvalCase) -> dict[str, Any]:
    started = time.perf_counter()
    error: str | None = None
    actual: dict[str, Any]

    try:
        result = use_case.execute(text=case.review)
        actual = {
            "status": result.status,
            "sentiment": result.sentiment,
            "polarity": result.polarity,
            "feedback": result.feedback,
            "suggestion": result.suggestion,
        }
    except invalid_review_error as exc:
        error = str(exc)
        actual = {
            "status": None,
            "sentiment": None,
            "polarity": None,
            "feedback": "",
            "suggestion": "",
        }
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"
        actual = {
            "status": None,
            "sentiment": None,
            "polarity": None,
            "feedback": "",
            "suggestion": "",
        }

    latency_ms = round((time.perf_counter() - started) * 1000, 2)
    feedback = actual["feedback"] or ""
    suggestion = actual["suggestion"] or ""

    return {
        "id": case.id,
        "group": case.group,
        "review": case.review,
        "expected": {
            "status": case.expected_status,
            "sentiment": case.expected_sentiment,
            "suggestion_required": case.suggestion_required,
        },
        "actual": actual,
        "checks": {
            "status_passed": actual["status"] == case.expected_status,
            "sentiment_passed": actual["sentiment"] == case.expected_sentiment,
            "suggestion_presence_passed": _suggestion_presence_passed(
                actual["status"],
                suggestion,
                case.suggestion_required,
            ),
            "suggestion_guidance_safe": _suggestion_guidance_safe(
                actual["status"],
                suggestion,
                case.suggestion_required,
            ),
            "feedback_length_passed": len(feedback) <= 200,
            "output_contract_passed": actual["status"] in VALID_STATUSES and isinstance(feedback, str),
        },
        "latency_ms": latency_ms,
        "error": error,
        "notes": case.notes,
    }


def _build_report(
    dataset_path: Path,
    items: list[dict[str, Any]],
    *,
    hf_model: str | None,
    hf_provider: str | None,
    sentiment_model_name: str | None,
) -> dict[str, Any]:
    run_id = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return {
        "run_id": run_id,
        "dataset": str(dataset_path),
        "environment": {
            "hf_model": hf_model,
            "hf_provider": hf_provider,
            "sentiment_model": sentiment_model_name,
            "rag_enabled": False,
            "llm_cache_enabled": os.getenv("LLM_CACHE_ENABLED", "false"),
        },
        "summary": _summarize(items),
        "items": items,
    }


def _write_report(report: dict[str, Any], results_dir: Path) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    filename = report["run_id"].replace(":", "-").replace("+00:00", "Z")
    output_path = results_dir / f"{filename}-review-eval.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def _threshold_failures(summary: dict[str, Any], thresholds: dict[str, float]) -> list[str]:
    failures = []

    for metric, threshold in thresholds.items():
        actual = float(summary[metric])
        if metric == "error_rate":
            if actual > threshold:
                failures.append(f"{metric}: expected <= {threshold}%, got {actual}%")
            continue

        if actual < threshold:
            failures.append(f"{metric}: expected >= {threshold}%, got {actual}%")

    return failures


def _metric_passed(metric: str, actual: float, threshold: float) -> bool:
    if metric == "error_rate":
        return actual <= threshold

    return actual >= threshold


def _format_metric_status(metric: str, actual: float, threshold: float, *, warning: bool = False) -> str:
    passed = _metric_passed(metric, actual, threshold)
    if passed:
        return "PASS"

    return "WARN" if warning else "FAIL"


def _print_metric_group(title: str, summary: dict[str, Any], thresholds: dict[str, float], *, warning: bool = False) -> None:
    print(title)
    for metric, threshold in thresholds.items():
        actual = float(summary[metric])
        status = _format_metric_status(metric, actual, threshold, warning=warning)
        comparator = "<=" if metric == "error_rate" else ">="
        print(f"  {metric}: {actual}% {status} ({comparator} {threshold}%)")


def _print_failures(items: list[dict[str, Any]]) -> None:
    failed_items = [
        item
        for item in items
        if item["error"] is not None or not all(item["checks"].values())
    ]

    if not failed_items:
        return

    print()
    print("Failed cases:")
    for item in failed_items:
        failed_checks = [
            name for name, passed in item["checks"].items() if not passed
        ]
        if item["error"] is not None:
            failed_checks.append("error")

        print(f"- {item['id']} ({', '.join(failed_checks)})")
        print(f"  expected: {item['expected']}")
        print(f"  actual: {item['actual']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run offline LLMOps evaluations for review analysis.")
    parser.add_argument("--dataset", type=Path, default=_default_dataset_path())
    parser.add_argument("--results-dir", type=Path, default=_default_results_dir())
    parser.add_argument(
        "--no-thresholds",
        action="store_true",
        help="Run the eval without failing or warning when metrics are below thresholds.",
    )
    parser.add_argument("--min-status-accuracy", type=float, default=CORE_THRESHOLDS["status_accuracy"])
    parser.add_argument("--min-sentiment-accuracy", type=float, default=SECONDARY_THRESHOLDS["sentiment_accuracy"])
    parser.add_argument(
        "--min-suggestion-guidance-safety",
        type=float,
        default=SECONDARY_THRESHOLDS["suggestion_guidance_safety"],
    )
    parser.add_argument(
        "--min-suggestion-presence-accuracy",
        type=float,
        default=CORE_THRESHOLDS["suggestion_presence_accuracy"],
    )
    parser.add_argument(
        "--min-feedback-length-accuracy",
        type=float,
        default=CORE_THRESHOLDS["feedback_length_accuracy"],
    )
    parser.add_argument(
        "--min-output-contract-accuracy",
        type=float,
        default=CORE_THRESHOLDS["output_contract_accuracy"],
    )
    parser.add_argument("--max-error-rate", type=float, default=CORE_THRESHOLDS["error_rate"])
    args = parser.parse_args()

    try:
        from app.core.clients import HF_MODEL, HF_PROVIDER, SENTIMENT_MODEL_NAME
        from app.domain.reviews.exceptions import InvalidReview
        from app.domain.reviews.use_cases import EvaluateText
        from app.services.sentiment_analysis_service import SentimentAnalysisService
        from app.services.suggestion_service import SuggestionService
    except ModuleNotFoundError as exc:
        print(f"Missing dependency: {exc.name}")
        print()
        print("Run this command from the backend directory using the project virtualenv:")
        print(".venv/bin/python -m evals.run_review_eval")
        print()
        print("If dependencies are not installed yet, install them with:")
        print("uv sync --extra dev")
        return 1

    cases = _load_dataset(args.dataset)
    use_case = EvaluateText(
        sentiment=SentimentAnalysisService(),
        sugg=SuggestionService(),
        min_length=1,
    )

    items = [_evaluate_case(use_case, InvalidReview, case) for case in cases]
    report = _build_report(
        args.dataset,
        items,
        hf_model=HF_MODEL,
        hf_provider=HF_PROVIDER,
        sentiment_model_name=SENTIMENT_MODEL_NAME,
    )
    output_path = _write_report(report, args.results_dir)
    summary = report["summary"]

    print("Review eval completed")
    print()
    print(f"Total: {summary['total']}")
    core_thresholds = {
        "status_accuracy": args.min_status_accuracy,
        "suggestion_presence_accuracy": args.min_suggestion_presence_accuracy,
        "feedback_length_accuracy": args.min_feedback_length_accuracy,
        "output_contract_accuracy": args.min_output_contract_accuracy,
        "error_rate": args.max_error_rate,
    }
    secondary_thresholds = {
        "sentiment_accuracy": args.min_sentiment_accuracy,
        "suggestion_guidance_safety": args.min_suggestion_guidance_safety,
    }

    _print_metric_group("Core metrics", summary, core_thresholds)
    print()
    _print_metric_group("Secondary metrics", summary, secondary_thresholds, warning=True)
    print(f"  avg_latency_ms: {summary['avg_latency_ms']} INFO")
    print()
    print(f"Results saved to {output_path}")

    if args.no_thresholds:
        return 0

    core_failures = _threshold_failures(summary, core_thresholds)
    secondary_warnings = _threshold_failures(summary, secondary_thresholds)

    if secondary_warnings:
        print()
        print("Secondary metric warnings:")
        for warning in secondary_warnings:
            print(f"- {warning}")

    if not core_failures:
        print()
        print("Core thresholds passed")
        return 0

    print()
    print("Core thresholds failed:")
    for failure in core_failures:
        print(f"- {failure}")
    _print_failures(report["items"])

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

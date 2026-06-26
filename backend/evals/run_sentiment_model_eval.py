from __future__ import annotations

import argparse
import json
import time
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class SentimentEvalCase:
    id: str
    group: str
    review: str
    expected_sentiment: str


def _default_dataset_path() -> Path:
    return Path(__file__).with_name("review_eval_dataset.json")


def _default_results_dir() -> Path:
    return Path(__file__).with_name("results")


def _load_dataset(path: Path) -> list[SentimentEvalCase]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return [
        SentimentEvalCase(
            id=item["id"],
            group=item["group"],
            review=item["review"],
            expected_sentiment=item["expected_sentiment"],
        )
        for item in data
    ]


def _normalize_label(label: str) -> str:
    value = (label or "").strip().upper()

    if value in {"POSITIVE", "POS", "LABEL_1", "1"}:
        return "POSITIVE"
    if value in {"NEGATIVE", "NEG", "LABEL_0", "0"}:
        return "NEGATIVE"
    if value in {"NEUTRAL", "LABEL_2", "2"}:
        return "NEUTRAL"

    return value


def _pct(passed: int, total: int) -> float:
    return round((passed / total) * 100, 2) if total else 0.0


def _evaluate_model(model_name: str, cases: list[SentimentEvalCase]) -> dict[str, Any]:
    from transformers import pipeline

    started_model = time.perf_counter()
    sentiment_pipeline = pipeline("sentiment-analysis", model=model_name)
    load_time_ms = round((time.perf_counter() - started_model) * 1000, 2)

    items = []
    for case in cases:
        started_item = time.perf_counter()
        error: str | None = None

        try:
            raw = sentiment_pipeline(case.review)[0]
            actual_label = _normalize_label(raw.get("label", ""))
            score = raw.get("score")
        except Exception as exc:
            actual_label = None
            score = None
            error = f"{type(exc).__name__}: {exc}"

        latency_ms = round((time.perf_counter() - started_item) * 1000, 2)
        passed = actual_label == case.expected_sentiment
        items.append(
            {
                "id": case.id,
                "group": case.group,
                "review": case.review,
                "expected_sentiment": case.expected_sentiment,
                "actual_sentiment": actual_label,
                "score": score,
                "passed": passed,
                "latency_ms": latency_ms,
                "error": error,
            }
        )

    total = len(items)
    passed_count = sum(1 for item in items if item["passed"])
    error_count = sum(1 for item in items if item["error"] is not None)

    groups: dict[str, list[dict[str, Any]]] = {}
    for item in items:
        groups.setdefault(item["group"], []).append(item)

    confusion = Counter(
        (item["expected_sentiment"], item["actual_sentiment"])
        for item in items
        if item["actual_sentiment"] is not None
    )

    return {
        "model": model_name,
        "summary": {
            "total": total,
            "accuracy": _pct(passed_count, total),
            "error_rate": _pct(error_count, total),
            "load_time_ms": load_time_ms,
            "avg_latency_ms": round(
                sum(item["latency_ms"] for item in items) / total,
                2,
            ) if total else 0.0,
            "by_group": {
                group: {
                    "total": len(group_items),
                    "accuracy": _pct(
                        sum(1 for item in group_items if item["passed"]),
                        len(group_items),
                    ),
                }
                for group, group_items in sorted(groups.items())
            },
            "confusion": [
                {
                    "expected": expected,
                    "actual": actual,
                    "count": count,
                }
                for (expected, actual), count in sorted(confusion.items())
            ],
        },
        "failures": [
            item for item in items if not item["passed"] or item["error"] is not None
        ],
        "items": items,
    }


def _build_report(
    *,
    dataset_path: Path,
    model_results: list[dict[str, Any]],
) -> dict[str, Any]:
    run_id = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ranked_models = sorted(
        model_results,
        key=lambda result: (
            result["summary"]["accuracy"],
            -result["summary"]["error_rate"],
            -result["summary"]["avg_latency_ms"],
        ),
        reverse=True,
    )

    return {
        "run_id": run_id,
        "dataset": str(dataset_path),
        "best_model": ranked_models[0]["model"] if ranked_models else None,
        "models": model_results,
    }


def _write_report(report: dict[str, Any], results_dir: Path) -> Path:
    results_dir.mkdir(parents=True, exist_ok=True)
    filename = report["run_id"].replace(":", "-").replace("+00:00", "Z")
    output_path = results_dir / f"{filename}-sentiment-model-eval.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output_path


def _print_summary(report: dict[str, Any], output_path: Path) -> None:
    print("Sentiment model eval completed")
    print()
    print(f"Best model: {report['best_model']}")
    print()

    for result in report["models"]:
        summary = result["summary"]
        print(result["model"])
        print(f"  Accuracy: {summary['accuracy']}%")
        print(f"  Error rate: {summary['error_rate']}%")
        print(f"  Load time: {summary['load_time_ms']}ms")
        print(f"  Avg latency: {summary['avg_latency_ms']}ms")
        print(f"  Failures: {len(result['failures'])}")
        print()

    print(f"Results saved to {output_path}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Compare sentiment models against the review eval dataset.")
    parser.add_argument("--dataset", type=Path, default=_default_dataset_path())
    parser.add_argument("--results-dir", type=Path, default=_default_results_dir())
    parser.add_argument(
        "--model",
        action="append",
        dest="models",
        help="Model name to evaluate. Can be passed multiple times.",
    )
    args = parser.parse_args()

    try:
        from app.core.clients import SENTIMENT_MODEL_NAME
        import transformers  # noqa: F401
    except ModuleNotFoundError as exc:
        print(f"Missing dependency: {exc.name}")
        print()
        print("Run this command from the backend directory using the project virtualenv:")
        print(".venv/bin/python -m evals.run_sentiment_model_eval")
        print()
        print("If dependencies are not installed yet, install them with:")
        print("uv sync --extra dev")
        return 1

    model_names = args.models or [SENTIMENT_MODEL_NAME]
    cases = _load_dataset(args.dataset)
    model_results = [_evaluate_model(model_name, cases) for model_name in model_names]
    report = _build_report(dataset_path=args.dataset, model_results=model_results)
    output_path = _write_report(report, args.results_dir)
    _print_summary(report, output_path)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

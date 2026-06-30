# Review Evaluation

Offline LLMOps evaluation for the review quality analyzer.

Run from the backend directory with the project virtualenv:

```bash
.venv/bin/python -m evals.run_review_eval
```

The runner reads `review_eval_dataset.json`, evaluates each review with the backend
`EvaluateText` use case, and writes a timestamped JSON report to `evals/results/`.

This first evaluation is intentionally offline and does not use the application
database or RAG context. It measures the review quality contract:

- status accuracy
- sentiment accuracy
- suggestion presence
- suggestion guidance safety
- feedback length
- output contract validity
- latency and error rate

The runner sets `EvaluateText(min_length=1)` so short reviews are evaluated by
the LLM as rejection cases instead of being counted as technical input errors.

By default, the runner fails with exit code `1` only when core metrics regress
below these thresholds:

- status accuracy >= 95%
- suggestion presence accuracy >= 95%
- feedback length accuracy = 100%
- output contract accuracy = 100%
- error rate = 0%

Secondary metrics are reported as warnings, but do not fail the command:

- sentiment accuracy >= 90%
- suggestion guidance safety >= 90%
- average latency

For exploratory runs without threshold failure or warnings:

```bash
.venv/bin/python -m evals.run_review_eval --no-thresholds
```

Thresholds can also be overridden, for example:

```bash
.venv/bin/python -m evals.run_review_eval --min-status-accuracy 90
```

The runner also compares results against the versioned baseline at
`evals/baselines/current.json`. This comparison is informational; thresholds are
still what decide whether the command fails. To skip the baseline output:

```bash
.venv/bin/python -m evals.run_review_eval --no-baseline
```

The command may call the configured Hugging Face LLM and sentiment model.

If the dependencies are not installed yet, run:

```bash
uv sync --extra dev
```

## Smoke Check

For CI or quick local validation without calling the LLM, run:

```bash
.venv/bin/python -m evals.validate_review_eval
```

This checks that the dataset is valid, case IDs are unique, required groups are
present, eval runners have valid Python syntax, and the prompt still contains
the core safety contract. It also verifies that the versioned baseline matches
the dataset size and includes required metrics.

## Sentiment Model Comparison

To evaluate the current sentiment model against the same dataset:

```bash
.venv/bin/python -m evals.run_sentiment_model_eval
```

To compare candidate models, pass `--model` multiple times:

```bash
.venv/bin/python -m evals.run_sentiment_model_eval \
  --model distilbert-base-uncased-finetuned-sst-2-english \
  --model siebert/sentiment-roberta-large-english
```

The report includes accuracy, failures, latency, group-level metrics, and a
confusion summary for each model. Candidate models may be downloaded by
Transformers on first use.

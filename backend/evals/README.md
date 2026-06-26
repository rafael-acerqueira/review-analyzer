# Review Evaluation

Offline LLMOps evaluation for the review quality analyzer.

Run from the backend directory with the project virtualenv:

```bash
.venv/bin/python -m evals.run_review_eval
```

The runner reads `review_eval_dataset.json`, evaluates each review with the backend
`EvaluateText` use case, and writes a timestamped JSON report to `evals/results/`.

This first evaluation is intentionally offline and does not use the application
database or RAG context. It measures the core review quality contract:

- status accuracy
- sentiment accuracy
- suggestion presence
- feedback length
- output contract validity
- latency and error rate

The runner sets `EvaluateText(min_length=1)` so short reviews are evaluated by
the LLM as rejection cases instead of being counted as technical input errors.

The command may call the configured Hugging Face LLM and sentiment model.

If the dependencies are not installed yet, run:

```bash
uv sync --extra dev
```

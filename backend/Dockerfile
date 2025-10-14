# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
 && install -m 0755 /root/.local/bin/uv /usr/local/bin/uv \
 && install -m 0755 /root/.local/bin/uvx /usr/local/bin/uvx

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-editable

COPY . .

ENV HF_HOME=/app/.cache/huggingface \
    HUGGINGFACE_HUB_CACHE=/app/.cache/huggingface \
    TRANSFORMERS_CACHE=/app/.cache/huggingface \
    SENTENCE_TRANSFORMERS_HOME=/app/.cache/sentencetransformers \
    TORCH_HOME=/app/.cache/torch
RUN mkdir -p $HF_HOME $SENTENCE_TRANSFORMERS_HOME $TORCH_HOME

RUN /app/.venv/bin/python - <<'PY'
from sentence_transformers import SentenceTransformer
SentenceTransformer("intfloat/multilingual-e5-small")
PY

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -f "http://localhost:${PORT:-7860}/docs" || exit 1

CMD sh -c '/app/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}'

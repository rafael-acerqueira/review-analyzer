# syntax=docker/dockerfile:1

FROM python:3.12-slim

ENV UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev --no-editable

COPY . .

EXPOSE 7860

HEALTHCHECK --interval=30s --timeout=3s --retries=3 CMD curl -f http://localhost:${PORT:-7860}/docs || exit 1

CMD sh -c 'uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-7860}'
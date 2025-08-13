FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl git ca-certificates \
  && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements-app.txt /app/requirements-app.txt

RUN pip install --upgrade pip && \
    pip install -r /app/requirements-app.txt

RUN pip install --index-url https://download.pytorch.org/whl/cpu torch==2.7.0

COPY . /app

ENV PORT=7860

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

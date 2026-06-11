from dotenv import load_dotenv
from transformers import pipeline
from huggingface_hub import InferenceClient
from functools import lru_cache
import logging
import os
import time

load_dotenv()

logger = logging.getLogger(__name__)
LLM_ERROR_RESPONSE = '{"status": "Rejected", "feedback": "AI error", "suggestion": ""}'

sentiment_pipeline = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

HF_TOKEN = os.getenv("HF_TOKEN")
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
HF_PROVIDER = os.getenv("HF_PROVIDER", "together")
LLM_CACHE_ENABLED = os.getenv("LLM_CACHE_ENABLED", "false").lower() in ("1", "true", "yes")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.3"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "150"))
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "30"))
LLM_RETRY_ATTEMPTS = max(1, int(os.getenv("LLM_RETRY_ATTEMPTS", "2")))
LLM_RETRY_BACKOFF_SECONDS = float(os.getenv("LLM_RETRY_BACKOFF_SECONDS", "0.5"))



client = InferenceClient(
    provider=HF_PROVIDER,
    api_key=HF_TOKEN,
    timeout=LLM_TIMEOUT_SECONDS,
)

def _validate_llm_config() -> bool:
    missing = []
    if not HF_TOKEN:
        missing.append("HF_TOKEN")
    if not HF_MODEL:
        missing.append("HF_MODEL")
    if not HF_PROVIDER:
        missing.append("HF_PROVIDER")

    if missing:
        logger.error("LLM is not configured; missing %s", ", ".join(missing))
        return False
    return True

def _call_llm_uncached(user_prompt: str) -> str:
    if not _validate_llm_config():
        return LLM_ERROR_RESPONSE

    for attempt in range(1, LLM_RETRY_ATTEMPTS + 1):
        try:
            completion = client.chat.completions.create(
                model=HF_MODEL,
                messages=[{"role": "user", "content": user_prompt}],
                temperature=LLM_TEMPERATURE,
                max_tokens=LLM_MAX_TOKENS,
            )
            return completion.choices[0].message.content
        except Exception:
            if attempt >= LLM_RETRY_ATTEMPTS:
                logger.exception("LLM request failed after %s attempt(s)", attempt)
                return LLM_ERROR_RESPONSE

            logger.warning(
                "LLM request failed on attempt %s/%s; retrying",
                attempt,
                LLM_RETRY_ATTEMPTS,
                exc_info=True,
            )
            time.sleep(LLM_RETRY_BACKOFF_SECONDS)


@lru_cache(maxsize=128)
def _call_llm_cached(user_prompt: str) -> str:
    return _call_llm_uncached(user_prompt)


def call_llm(user_prompt: str) -> str:
    if LLM_CACHE_ENABLED:
        return _call_llm_cached(user_prompt)
    return _call_llm_uncached(user_prompt)

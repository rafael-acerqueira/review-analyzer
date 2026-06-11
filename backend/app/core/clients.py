from dotenv import load_dotenv
from transformers import pipeline
from huggingface_hub import InferenceClient
from functools import lru_cache
import logging
import os
import time
from typing import Any

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



class HuggingFaceLLMClient:
    def __init__(
        self,
        *,
        client: Any,
        token: str | None,
        model: str | None,
        provider: str | None,
        temperature: float,
        max_tokens: int,
        retry_attempts: int,
        retry_backoff_seconds: float,
        error_response: str = LLM_ERROR_RESPONSE,
    ) -> None:
        self.client = client
        self.token = token
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.retry_attempts = max(1, retry_attempts)
        self.retry_backoff_seconds = retry_backoff_seconds
        self.error_response = error_response

    def _validate_config(self) -> bool:
        missing = []
        if not self.token:
            missing.append("HF_TOKEN")
        if not self.model:
            missing.append("HF_MODEL")
        if not self.provider:
            missing.append("HF_PROVIDER")

        if missing:
            logger.error("LLM is not configured; missing %s", ", ".join(missing))
            return False
        return True

    def complete(self, user_prompt: str) -> str:
        if not self._validate_config():
            return self.error_response

        for attempt in range(1, self.retry_attempts + 1):
            try:
                completion = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": user_prompt}],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                return completion.choices[0].message.content
            except Exception:
                if attempt >= self.retry_attempts:
                    logger.exception("LLM request failed after %s attempt(s)", attempt)
                    return self.error_response

                logger.warning(
                    "LLM request failed on attempt %s/%s; retrying",
                    attempt,
                    self.retry_attempts,
                    exc_info=True,
                )
                time.sleep(self.retry_backoff_seconds)


client = InferenceClient(
    provider=HF_PROVIDER,
    api_key=HF_TOKEN,
    timeout=LLM_TIMEOUT_SECONDS,
)

llm_client = HuggingFaceLLMClient(
    client=client,
    token=HF_TOKEN,
    model=HF_MODEL,
    provider=HF_PROVIDER,
    temperature=LLM_TEMPERATURE,
    max_tokens=LLM_MAX_TOKENS,
    retry_attempts=LLM_RETRY_ATTEMPTS,
    retry_backoff_seconds=LLM_RETRY_BACKOFF_SECONDS,
)

def _call_llm_uncached(user_prompt: str) -> str:
    return llm_client.complete(user_prompt)


@lru_cache(maxsize=128)
def _call_llm_cached(user_prompt: str) -> str:
    return _call_llm_uncached(user_prompt)


def call_llm(user_prompt: str) -> str:
    if LLM_CACHE_ENABLED:
        return _call_llm_cached(user_prompt)
    return _call_llm_uncached(user_prompt)

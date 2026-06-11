import json

from app.core import clients


class _Message:
    content = '{"status": "Accepted", "feedback": "ok", "suggestion": ""}'


class _Choice:
    message = _Message()


class _Completion:
    choices = [_Choice()]


class _FakeCompletions:
    def __init__(self, failures_before_success: int):
        self.failures_before_success = failures_before_success
        self.calls = 0

    def create(self, **kwargs):
        self.calls += 1
        if self.calls <= self.failures_before_success:
            raise RuntimeError("temporary LLM failure")
        return _Completion()


class _FakeChat:
    def __init__(self, completions: _FakeCompletions):
        self.completions = completions


class _FakeClient:
    def __init__(self, completions: _FakeCompletions):
        self.chat = _FakeChat(completions)


def test_call_llm_retries_transient_failure(monkeypatch):
    completions = _FakeCompletions(failures_before_success=1)
    llm_client = clients.HuggingFaceLLMClient(
        client=_FakeClient(completions),
        token="test-token",
        model="test-model",
        provider="test-provider",
        temperature=0.3,
        max_tokens=150,
        retry_attempts=2,
        retry_backoff_seconds=0,
    )
    monkeypatch.setattr(clients.time, "sleep", lambda _: None)

    result = llm_client.complete("prompt")

    assert completions.calls == 2
    assert json.loads(result)["status"] == "Accepted"


def test_call_llm_returns_fallback_after_retry_exhaustion(monkeypatch):
    completions = _FakeCompletions(failures_before_success=99)
    llm_client = clients.HuggingFaceLLMClient(
        client=_FakeClient(completions),
        token="test-token",
        model="test-model",
        provider="test-provider",
        temperature=0.3,
        max_tokens=150,
        retry_attempts=2,
        retry_backoff_seconds=0,
    )
    monkeypatch.setattr(clients.time, "sleep", lambda _: None)

    result = llm_client.complete("prompt")

    assert completions.calls == 2
    assert json.loads(result) == {
        "status": "Rejected",
        "feedback": "AI error",
        "suggestion": "",
    }


def test_call_llm_returns_fallback_when_token_is_missing(monkeypatch):
    completions = _FakeCompletions(failures_before_success=0)
    llm_client = clients.HuggingFaceLLMClient(
        client=_FakeClient(completions),
        token="",
        model="test-model",
        provider="test-provider",
        temperature=0.3,
        max_tokens=150,
        retry_attempts=2,
        retry_backoff_seconds=0,
    )

    result = llm_client.complete("prompt")

    assert completions.calls == 0
    assert json.loads(result) == {
        "status": "Rejected",
        "feedback": "AI error",
        "suggestion": "",
    }

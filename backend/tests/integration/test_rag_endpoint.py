# tests/integration/test_rag_endpoint.py
from dataclasses import dataclass
from typing import List, Optional

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.domain.rag.use_cases import SearchRag
from app.domain.rag.entities import RagHit
from app.api.v1.deps import get_rag_uc


BASE = "/api/v1/rag"  # ajuste se seu prefixo for diferente


@dataclass
class _FakeEmbedder:
    def embed(self, text: str) -> List[float]:
        return [0.1, 0.2, 0.3]


@dataclass
class _FakeRepo:
    items: List[RagHit]

    def search_by_embedding(self, *, embedding: List[float], k: int = 5, min_score: Optional[float] = None) -> List[RagHit]:
        out = self.items[:]
        if min_score is not None:
            out = [h for h in out if h.score >= min_score]
        out.sort(key=lambda h: h.score, reverse=True)
        return out[:k]


@pytest.fixture
def client():
    # cria UC fake e faz override do provider
    items = [
        RagHit(id=10, text="doc corrected or original", score=0.88),
        RagHit(id=11, text="another doc", score=0.72),
        RagHit(id=12, text="low score doc", score=0.41),
    ]
    fake_uc = SearchRag(embedder=_FakeEmbedder(), repo=_FakeRepo(items))
    app.dependency_overrides[get_rag_uc] = lambda: fake_uc
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


def test_rag_search_ok(client):
    payload = {"text": "my query", "k": 2, "min_score": 0.5}
    r = client.post(f"{BASE}/search", json=payload)
    assert r.status_code == 200, r.text
    data = r.json()
    assert "results" in data
    assert len(data["results"]) == 2
    assert [hit["id"] for hit in data["results"]] == [10, 11]
    assert all(0 <= hit["score"] <= 1 for hit in data["results"])


def test_rag_search_min_score_filters(client):
    payload = {"text": "q", "k": 5, "min_score": 0.75}
    r = client.post(f"{BASE}/search", json=payload)
    assert r.status_code == 200
    data = r.json()
    # só o 0.88 passa
    assert [hit["id"] for hit in data["results"]] == [10]


def test_rag_search_empty_text_returns_empty(client):
    r = client.post(f"{BASE}/search", json={"text": "   "})
    assert r.status_code == 200
    assert r.json()["results"] == []

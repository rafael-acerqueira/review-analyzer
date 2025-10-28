from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Optional, List

from .entities import RagHit, RagSearchResult
from .interfaces import Embedder, RagRepository


__all__ = ["SearchRag"]


@dataclass(frozen=True)
class SearchRag:
    embedder: Embedder
    repo: RagRepository
    max_k: int = 50

    def execute(self, *, text: str, k: int = 5, min_score: Optional[float] = None) -> RagSearchResult:
        t0 = time.perf_counter()

        q = (text or "").strip()
        if not q:
            return RagSearchResult(query=q, hits=[], took_ms=0)

        k = max(1, min(self.max_k, int(k or 5)))

        emb: List[float] = self.embedder.embed(q)

        hits: List[RagHit] = self.repo.search_by_embedding(
            embedding=emb, k=k, min_score=min_score
        )

        hits_sorted = sorted(hits, key=lambda h: h.score, reverse=True)

        took_ms = int((time.perf_counter() - t0) * 1000)
        return RagSearchResult(query=q, hits=hits_sorted, took_ms=took_ms)

from __future__ import annotations
from typing import Protocol, List, Optional
from .entities import RagHit


__all__ = ["RagRepository", "Embedder"]


class RagRepository(Protocol):
    def search_by_embedding(
        self,
        *,
        embedding: List[float],
        k: int = 5,
        min_score: Optional[float] = None,
    ) -> List[RagHit]:
        ...


class Embedder(Protocol):
    def embed(self, text: str) -> List[float]:
        ...

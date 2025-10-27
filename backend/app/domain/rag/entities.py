from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


__all__ = ["RagHit", "RagSearchResult"]


@dataclass(frozen=True)
class RagHit:
    id: int
    text: str
    score: float


@dataclass(frozen=True)
class RagSearchResult:
    query: str
    hits: List[RagHit]
    took_ms: Optional[int] = None

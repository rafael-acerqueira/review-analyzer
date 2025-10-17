from __future__ import annotations

from typing import Protocol, Optional, List, Tuple, Iterable
from datetime import datetime
from app.domain.reviews.entities import ReviewEntity


class ReviewRepository(Protocol):

    def create_approved(
        self,
        *,
        user_id: int,
        text: str,
        corrected_text: str,
        sentiment: Optional[str],
        polarity: Optional[float],
        suggestion: Optional[str],
        feedback: Optional[str] = None,
    ) -> ReviewEntity: ...
    def delete(self, review_id: int) -> bool: ...
    def get(self, review_id: int) -> Optional[ReviewEntity]: ...
    def list_by_user(self, *, user_id: int) -> List[ReviewEntity]: ...

    def list_filtered(
        self,
        *,
        sentiment: Optional[str] = None,
        status: Optional[str] = None,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        user_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[ReviewEntity]: ...

    def stats(
        self,
        *,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        user_id: Optional[int] = None,
    ) -> dict: ...


class SentimentAnalyzer(Protocol):
    def analyze(self, text: str) -> Tuple[str, float]: ...


class SuggestionEngine(Protocol):
    def evaluate(self, *, text: str) -> dict: ...


class DraftProvider(Protocol):

    def create(self, *, user_id: int, text: str, group_id: str) -> str: ...
    def decode(self, token: str) -> dict: ...  # {"user_id","text","group_id","ts"}

__all__ = ["ReviewRepository", "SentimentAnalyzer", "SuggestionEngine", "DraftProvider"]

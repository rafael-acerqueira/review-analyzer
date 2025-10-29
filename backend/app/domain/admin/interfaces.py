from __future__ import annotations
from datetime import datetime, date
from typing import Iterable, Optional, Protocol

from app.models.review import Review
from app.domain.admin.entities import AdminStats


class AdminReviewsRepository(Protocol):
    def list_reviews(
        self,
        *,
        sentiment: Optional[str],
        status: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[Review]:
        ...

    def delete_review(self, review_id: int) -> bool:
        ...

    def aggregate_stats(
        self,
        *,
        from_date: date,
        to_date: date,
        user_id: Optional[int] = None,
    ) -> AdminStats:
        ...

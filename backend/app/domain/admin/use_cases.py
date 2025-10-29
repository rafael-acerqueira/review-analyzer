from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone, date
from typing import Iterable, Optional

from app.domain.admin.interfaces import AdminReviewsRepository
from app.domain.admin.entities import AdminStats
from app.models.review import Review


@dataclass
class ListReviews:
    repo: AdminReviewsRepository

    def execute(
        self,
        *,
        sentiment: Optional[str],
        status: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[Review]:
        return self.repo.list_reviews(
            sentiment=sentiment,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )


@dataclass
class DeleteReview:
    repo: AdminReviewsRepository

    def execute(self, review_id: int) -> bool:
        return self.repo.delete_review(review_id)


@dataclass
class GetStats:
    repo: AdminReviewsRepository

    def execute(
        self,
        *,
        from_date: Optional[date],
        to_date: Optional[date],
        user_id: Optional[int],
    ) -> AdminStats:
        to_d = to_date or datetime.now(timezone.utc).date()
        from_d = from_date or (to_d - timedelta(days=30))
        return self.repo.aggregate_stats(from_date=from_d, to_date=to_d, user_id=user_id)

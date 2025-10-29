from __future__ import annotations
from typing import Iterable, Optional
from datetime import datetime, date, time

from sqlmodel import Session, select, func
from app.models.review import Review
from app.domain.admin.interfaces import AdminReviewsRepository
from app.domain.admin.entities import AdminStats, Period, RejectionReason


class SqlModelAdminRepository(AdminReviewsRepository):
    def __init__(self, db: Session):
        self.db = db

    def list_reviews(
        self,
        *,
        sentiment: Optional[str],
        status: Optional[str],
        date_from: Optional[datetime],
        date_to: Optional[datetime],
    ) -> Iterable[Review]:
        stmt = select(Review)
        if sentiment:
            stmt = stmt.where(Review.sentiment == sentiment)
        if status:
            stmt = stmt.where(Review.status == status)
        if date_from:
            stmt = stmt.where(Review.created_at >= date_from)
        if date_to:
            stmt = stmt.where(Review.created_at <= date_to)

        return self.db.exec(stmt).all()

    def delete_review(self, review_id: int) -> bool:
        row = self.db.get(Review, review_id)
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True

    def aggregate_stats(
        self,
        *,
        from_date: date,
        to_date: date,
        user_id: Optional[int] = None,
    ) -> AdminStats:
        from_dt = datetime.combine(from_date, time.min)
        to_dt = datetime.combine(to_date, time.max)

        base = select(Review).where(
            Review.created_at >= from_dt,
            Review.created_at <= to_dt,
        )
        if user_id:
            base = base.where(Review.user_id == user_id)

        rows = self.db.exec(base).all()
        total = len(rows)

        # Aggregations
        sent_stmt = (
            select(Review.sentiment, func.count())
            .where(
                Review.created_at >= from_dt,
                Review.created_at <= to_dt,
                *( [Review.user_id == user_id] if user_id else [] )
            )
            .group_by(Review.sentiment)
        )
        status_stmt = (
            select(Review.status, func.count())
            .where(
                Review.created_at >= from_dt,
                Review.created_at <= to_dt,
                *( [Review.user_id == user_id] if user_id else [] )
            )
            .group_by(Review.status)
        )
        rej_stmt = (
            select(Review.feedback, func.count())
            .where(
                Review.status == "Rejected",
                Review.created_at >= from_dt,
                Review.created_at <= to_dt,
                *( [Review.user_id == user_id] if user_id else [] )
            )
            .group_by(Review.feedback)
            .order_by(func.count().desc())
            .limit(5)
        )

        sent_rows = self.db.exec(sent_stmt).all()
        status_rows = self.db.exec(status_stmt).all()
        rej_rows = self.db.exec(rej_stmt).all()

        by_sentiment = {k: int(v) for k, v in sent_rows}
        by_status = {k: int(v) for k, v in status_rows}
        top_rejection_reasons = [
            RejectionReason(reason=r, count=int(c)) for (r, c) in rej_rows if r
        ]

        pct_accepted = (by_status.get("Accepted", 0) / total * 100.0) if total else 0.0
        pct_rejected = (by_status.get("Rejected", 0) / total * 100.0) if total else 0.0

        return AdminStats(
            period=Period(from_date=from_date, to_date=to_date),
            total_reviews=total,
            by_sentiment=by_sentiment,
            by_status=by_status,
            percent_accepted=pct_accepted,
            percent_rejected=pct_rejected,
            top_rejection_reasons=top_rejection_reasons,
            user_id=user_id,
        )

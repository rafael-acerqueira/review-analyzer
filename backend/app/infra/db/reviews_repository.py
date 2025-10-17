from typing import Optional, List
from datetime import datetime
from sqlmodel import Session, select
from sqlalchemy import func

from app.domain.reviews.interfaces import ReviewRepository
from app.domain.reviews.entities import ReviewEntity
from app.models.review import Review as ReviewModel


class SqlModelReviewRepository(ReviewRepository):
    def __init__(self, db: Session):
        self.db = db

    def _to_entity(self, row: Optional[ReviewModel]) -> Optional[ReviewEntity]:
        if not row:
            return None
        return ReviewEntity(
            id=row.id,
            user_id=row.user_id,
            text=row.text,
            sentiment=getattr(row, "sentiment", None),
            polarity=getattr(row, "polarity", None),
            status=getattr(row, "status", None),
            suggestion=getattr(row, "suggestion", None),
            feedback=getattr(row, "feedback", None),
            created_at=getattr(row, "created_at", None),
            updated_at=getattr(row, "updated_at", None),
        )

    def _rows_to_entities(self, rows: List[ReviewModel]) -> List[ReviewEntity]:
        return [self._to_entity(r) for r in rows if r is not None]


    def create(self, *, user_id: int, text: str) -> ReviewEntity:
        row = ReviewModel(
            user_id=user_id,
            text=text,
            sentiment=None,
            polarity=None,
            status=getattr(ReviewModel, "status").default.arg if hasattr(getattr(ReviewModel, "status"), "default") else None,
            suggestion=None,
            feedback=None,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_entity(row)

    def update_analysis(
        self,
        *,
        review_id: int,
        sentiment: Optional[str],
        polarity: Optional[float],
        status: Optional[str],
        suggestion: Optional[str],
        feedback: Optional[str] = None,
    ) -> ReviewEntity:
        row = self.db.get(ReviewModel, review_id)
        if not row:
            return None
        if sentiment is not None:
            row.sentiment = sentiment
        if polarity is not None:
            row.polarity = polarity
        if status is not None:
            row.status = status
        if suggestion is not None:
            row.suggestion = suggestion
        if feedback is not None:
            row.feedback = feedback

        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_entity(row)

    def delete(self, review_id: int) -> bool:
        row = self.db.get(ReviewModel, review_id)
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True


    def get(self, review_id: int) -> Optional[ReviewEntity]:
        row = self.db.get(ReviewModel, review_id)
        return self._to_entity(row)

    def list_by_user(self, *, user_id: int) -> List[ReviewEntity]:
        stmt = select(ReviewModel).where(ReviewModel.user_id == user_id).order_by(ReviewModel.created_at.desc())
        rows = self.db.exec(stmt).all()
        return self._rows_to_entities(rows)

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
    ) -> List[ReviewEntity]:
        conditions = []
        if sentiment:
            conditions.append(ReviewModel.sentiment == sentiment)
        if status:
            conditions.append(ReviewModel.status == status)
        if user_id:
            conditions.append(ReviewModel.user_id == user_id)
        if created_from:
            conditions.append(ReviewModel.created_at >= created_from)
        if created_to:
            conditions.append(ReviewModel.created_at <= created_to)

        stmt = select(ReviewModel)
        if conditions:
            stmt = stmt.where(*conditions)
        stmt = stmt.order_by(ReviewModel.created_at.desc())

        if offset is not None:
            stmt = stmt.offset(offset)
        if limit is not None:
            stmt = stmt.limit(limit)

        rows = self.db.exec(stmt).all()
        return self._rows_to_entities(rows)

    def stats(
        self,
        *,
        created_from: Optional[datetime] = None,
        created_to: Optional[datetime] = None,
        user_id: Optional[int] = None,
    ) -> dict:
        conditions = []
        if user_id:
            conditions.append(ReviewModel.user_id == user_id)
        if created_from:
            conditions.append(ReviewModel.created_at >= created_from)
        if created_to:
            conditions.append(ReviewModel.created_at <= created_to)

        total_stmt = select(func.count(ReviewModel.id))
        if conditions:
            total_stmt = total_stmt.where(*conditions)
        total = self.db.exec(total_stmt).one()[0]

        by_sentiment_stmt = select(ReviewModel.sentiment, func.count(ReviewModel.id)).group_by(ReviewModel.sentiment)
        if conditions:
            by_sentiment_stmt = by_sentiment_stmt.where(*conditions)
        sentiment_rows = self.db.exec(by_sentiment_stmt).all()
        by_sentiment = {row[0]: row[1] for row in sentiment_rows}

        by_status_stmt = select(ReviewModel.status, func.count(ReviewModel.id)).group_by(ReviewModel.status)

        if conditions:
            by_status_stmt = by_status_stmt.where(*conditions)
        status_rows = self.db.exec(by_status_stmt).all()
        by_status = {row[0]: row[1] for row in status_rows}

        return {
            "total": int(total or 0),
            "by_sentiment": {k: int(v) for k, v in by_sentiment.items()},
            "by_status": {k: int(v) for k, v in by_status.items()},
        }

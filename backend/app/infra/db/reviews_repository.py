from typing import Optional, List, Dict
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
            text=getattr(row, "text", ""),
            corrected_text=getattr(row, "corrected_text", None),
            sentiment=getattr(row, "sentiment", "unknown") or "unknown",
            status=getattr(row, "status", "approved") or "approved",
            feedback=getattr(row, "feedback", "") or "",
            suggestion=getattr(row, "suggestion", None),
            created_at=getattr(row, "created_at", None),
            updated_at=getattr(row, "updated_at", None),
        )

    def _rows_to_entities(self, rows: List[ReviewModel]) -> List[ReviewEntity]:
        return [self._to_entity(r) for r in rows if r is not None]

    def create_approved(
        self,
        *,
        user_id: int,
        text: str,
        corrected_text: Optional[str],
        sentiment: str,
        status: str,
        feedback: str,
        suggestion: Optional[str],
    ) -> ReviewEntity:
        row = ReviewModel(
            user_id=user_id,
            text=text,
            corrected_text=corrected_text or "",
            sentiment=sentiment or "unknown",
            status=status or "approved",
            feedback=feedback or "",
            suggestion=suggestion,
        )
        self.db.add(row)
        self.db.commit()
        self.db.refresh(row)
        return self._to_entity(row)

    def get(self, review_id: int) -> Optional[ReviewEntity]:
        return self._to_entity(self.db.get(ReviewModel, review_id))

    def delete(self, review_id: int) -> bool:
        row = self.db.get(ReviewModel, review_id)
        if not row:
            return False
        self.db.delete(row)
        self.db.commit()
        return True

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
        conds = []
        if sentiment:
            conds.append(ReviewModel.sentiment == sentiment)
        if status:
            conds.append(ReviewModel.status == status)
        if user_id:
            conds.append(ReviewModel.user_id == user_id)
        if created_from:
            conds.append(ReviewModel.created_at >= created_from)
        if created_to:
            conds.append(ReviewModel.created_at <= created_to)

        stmt = select(ReviewModel)
        if conds:
            stmt = stmt.where(*conds)
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
    ) -> Dict:
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
        total_res = self.db.exec(total_stmt)
        first_row = total_res.first()
        if first_row is None:
            total = 0
        elif isinstance(first_row, tuple):
            total = int(first_row[0])
        else:
            total = int(first_row)


        by_sent_stmt = select(ReviewModel.sentiment, func.count(ReviewModel.id))
        if conditions:
            by_sent_stmt = by_sent_stmt.where(*conditions)
        by_sent_stmt = by_sent_stmt.group_by(ReviewModel.sentiment)
        sent_rows = self.db.exec(by_sent_stmt).all()
        by_sentiment = {k if k is not None else "unknown": int(v) for (k, v) in sent_rows}


        by_status_stmt = select(ReviewModel.status, func.count(ReviewModel.id))
        if conditions:
            by_status_stmt = by_status_stmt.where(*conditions)
        by_status_stmt = by_status_stmt.group_by(ReviewModel.status)
        status_rows = self.db.exec(by_status_stmt).all()
        by_status = {k if k is not None else "unknown": int(v) for (k, v) in status_rows}

        return {"total": total, "by_sentiment": by_sentiment, "by_status": by_status}

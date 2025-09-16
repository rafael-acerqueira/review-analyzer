from sqlmodel import select, Session

from app.embeddings import embed_text_passage
from app.models.review import Review
from typing import List, Optional
from datetime import datetime


def get_reviews(session: Session,
                sentiment: Optional[str] = None,
                status: Optional[str] = None,
                date_from: Optional[datetime] = None,
                date_to: Optional[datetime] = None
                ) -> List[Review]:

    query = select(Review)

    if sentiment:
        query = query.where(Review.sentiment == sentiment)
    if status:
        query = query.where(Review.status == status)
    if date_from:
        query = query.where(Review.created_at >= date_from)
    if date_to:
        query = query.where(Review.created_at <= date_to)

    return list(session.exec(query).all())

def delete_review(session: Session, review_id: int):
    review = session.get(Review, review_id)
    if review:
        session.delete(review)
        session.commit()
        return True
    return False

def create_review(session: Session, review: Review, user) -> Review:
    data = review.model_dump(exclude_unset=True)
    db_review = Review(**data, user_id=user.id)
    session.add(db_review)
    session.commit()
    session.refresh(db_review)

    final_text = _final_approved_text(db_review)
    if final_text:
        try:
            vec = embed_text_passage(final_text)
            if hasattr(vec, "tolist"):
                vec = vec.tolist()
            db_review.embedding = vec
            session.add(db_review)
            session.commit()
            session.refresh(db_review)
        except Exception as e:
            print(f"[embedding] fail trying to index review_id={db_review.id}: {e}")

    return db_review

def _final_approved_text(r: Review) -> str | None:
    ct = (r.corrected_text or "").strip()
    if ct:
        return ct
    t = (r.text or "").strip()
    return t if t else None
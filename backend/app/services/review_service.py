from sqlmodel import select, Session
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
    return db_review
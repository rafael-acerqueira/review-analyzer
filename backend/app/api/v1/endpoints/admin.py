from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from datetime import datetime, timedelta, timezone, date, time
from app.models.review import Review
from app.models.user import User
from app.database import get_session
from sqlmodel import Session, select, func

from app.schemas import ReviewRead
from app.services.review_service import get_reviews, delete_review
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/reviews", response_model=List[ReviewRead])
def list_reviews(
        current_user: User = Depends(get_current_user),
        sentiment: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        session: Session = Depends(get_session)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    return get_reviews(session, sentiment, status, date_from, date_to)

@router.delete("/reviews/{review_id}")
def remove_review(review_id: int, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")
    if not delete_review(session, review_id):
        raise HTTPException(status_code=404, detail="Review not found")
    return {"review_id": review_id}


@router.get("/stats")
def get_admin_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
    from_date: Optional[date] = Query(None, description="Start date for stats"),
    to_date: Optional[date] = Query(None, description="End date for stats"),
    user_id: Optional[int] = Query(None, description="Filter by user id"),
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    to_date_val = to_date or datetime.now(timezone.utc).date()
    from_date_val = from_date or (to_date_val - timedelta(days=30))

    from_dt = datetime.combine(from_date_val, time.min)
    to_dt = datetime.combine(to_date_val, time.max)

    query = select(Review).where(
        Review.created_at >= from_dt,
        Review.created_at <= to_dt
    )
    if user_id:
        query = query.where(Review.user_id == user_id)
    reviews = session.exec(query).all()

    by_sentiment = {}
    by_status = {}
    top_rejection_reasons = {}

    if reviews:

        sent_q = (
            session.exec(
                select(Review.sentiment, func.count())
                .where(
                    Review.created_at >= from_date_val,
                    Review.created_at <= to_date_val,
                    *( [Review.user_id == user_id] if user_id else [] )
                )
                .group_by(Review.sentiment)
            )
        ).all()
        by_sentiment = dict(sent_q)


        status_q = (
            session.exec(
                select(Review.status, func.count())
                .where(
                    Review.created_at >= from_date_val,
                    Review.created_at <= to_date_val,
                    *( [Review.user_id == user_id] if user_id else [] )
                )
                .group_by(Review.status)
            )
        ).all()
        by_status = dict(status_q)

        # Top motivos de rejeição (caso queira, se tiver esse campo)
        rejection_reasons = (
            session.exec(
                select(Review.feedback, func.count())
                .where(
                    Review.status == "Rejected",
                    Review.created_at >= from_date_val,
                    Review.created_at <= to_date_val,
                    *( [Review.user_id == user_id] if user_id else [] )
                )
                .group_by(Review.feedback)
                .order_by(func.count().desc())
                .limit(5)
            )
        ).all()
        top_rejection_reasons = [
            {"reason": reason, "count": count} for reason, count in rejection_reasons if reason
        ]
    else:
        by_sentiment = {}
        by_status = {}
        top_rejection_reasons = []

    total_reviews = len(reviews)
    percent_accepted = (
        by_status.get("Accepted", 0) / total_reviews * 100 if total_reviews else 0
    )
    percent_rejected = (
        by_status.get("Rejected", 0) / total_reviews * 100 if total_reviews else 0
    )


    return {
        "period": {
            "from": from_date_val,
            "to": to_date_val,
        },
        "total_reviews": total_reviews,
        "by_sentiment": by_sentiment,
        "by_status": by_status,
        "percent_accepted": percent_accepted,
        "percent_rejected": percent_rejected,
        "top_rejection_reasons": top_rejection_reasons,
        "filters": {
            "user_id": user_id,
        }
    }
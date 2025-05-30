from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from app.models.review import Review
from app.database import get_session
from sqlmodel import Session
from app.services.review_service import get_reviews, delete_review, create_review

router = APIRouter()

@router.get("/reviews", response_model=List[Review])
def list_reviews(
        sentiment: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        session: Session = Depends(get_session)
):
    return get_reviews(session, sentiment, status, date_from, date_to)

@router.delete("/reviews/{review_id}")
def remove_review(review_id: int, session: Session = Depends(get_session)):
    if not delete_review(session, review_id):
        raise HTTPException(status_code=404, detail="Review not found")
    return {"detail": "Review deleted successfully"}
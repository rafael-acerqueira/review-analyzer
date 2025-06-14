from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from app.models.review import Review
from app.models.user import User
from app.database import get_session
from sqlmodel import Session
from app.services.review_service import get_reviews, delete_review
from app.dependencies import get_current_user

router = APIRouter()

@router.get("/reviews", response_model=List[Review])
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
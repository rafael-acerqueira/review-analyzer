from fastapi import APIRouter, Depends, status, HTTPException

from app.dependencies import get_current_user
from app.schemas import ReviewRequest, ReviewResponse, ReviewRead
from app.models.user import User
from app.models.review import Review
from app.database import get_session
from app.services.review_service import create_review
from sqlmodel import Session, select


from app.services.sentiment_analysis_service import SentimentAnalysisService
from app.services.suggestion_service import SuggestionService

router = APIRouter()

@router.post("/reviews", status_code=status.HTTP_201_CREATED, response_model=ReviewRead)
def create_new_review(review: Review, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> Review:
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    return create_review(session, review, current_user)

@router.get("/my-reviews", response_model=list[ReviewRead])
def get_my_reviews(session: Session = Depends(get_session), user: User = Depends(get_current_user)) -> ReviewRead:
    reviews = session.exec(select(Review).where(Review.user_id == user.id)).all()
    return reviews

@router.post("/analyze_review")
def analyze_review(request: ReviewRequest, current_user: User = Depends(get_current_user), session: Session = Depends(get_session)) -> ReviewResponse:
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")
    sentiment, polarity  = SentimentAnalysisService.analyze(request.text)
    quality = SuggestionService.evaluate_review(text=request.text, session=session)

    return ReviewResponse(
        text=request.text,
        sentiment=sentiment,
        polarity=polarity,
        suggestion=quality['suggestion'],
        status=quality['status'],
        feedback=quality['feedback']
    )
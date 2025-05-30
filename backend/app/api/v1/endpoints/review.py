from fastapi import APIRouter, Depends
from app.schemas import ReviewRequest, ReviewResponse
from app.models.review import Review
from app.database import get_session
from app.services.review_service import create_review
from sqlmodel import Session


from app.services.sentiment_analysis_service import SentimentAnalysisService
from app.services.suggestion_service import SuggestionService

router = APIRouter()

@router.post("/reviews")
def create_new_review(review: Review, session: Session = Depends(get_session)) -> Review:
    return create_review(session, review)

@router.post("/analyze_review")
def analyze_review(request: ReviewRequest) -> ReviewResponse:
    sentiment, polarity  = SentimentAnalysisService.analyze(request.text)
    quality = SuggestionService.evaluate_review(request.text)

    return ReviewResponse(
        text=request.text,
        sentiment=sentiment,
        polarity=polarity,
        suggestion=quality['suggestion'],
        status=quality['status'],
        feedback=quality['feedback']
    )
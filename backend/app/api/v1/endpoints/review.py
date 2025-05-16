from fastapi import APIRouter
from app.schemas import ReviewRequest, ReviewResponse

from app.services.sentiment_analysis_service import SentimentAnalysisService
from app.services.suggestion_service import SuggestionService

router = APIRouter()

@router.post("/reviews")
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
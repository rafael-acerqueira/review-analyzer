from fastapi import APIRouter
from app.schemas import ReviewRequest, ReviewResponse

from app.services.sentiment_analysis_service import SentimentAnalysisService

router = APIRouter()

@router.post("/reviews")
def analyze_review(request: ReviewRequest) -> ReviewResponse:
    sentiment, polarity  = SentimentAnalysisService.analyze(request.text)
    return ReviewResponse(
        text='Test',
        sentiment=sentiment,
        polarity=polarity,
        suggestion="Should improve this feedback for X reasons",
        status="Accept",
        feedback="It's a good pillow"
    )

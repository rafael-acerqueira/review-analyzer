from fastapi import APIRouter
from schemas import ReviewRequest, ReviewResponse


router = APIRouter()

@router.post("/reviews")
def analyze_review(request: ReviewRequest) -> ReviewResponse:
    return ReviewResponse(
        text='Test',
        sentiment='Positive',
        polarity=0.5,
        suggestion="Should improve this feedback for X reasons",
        status="Accept",
        feedback="It's a good pillow"
    )

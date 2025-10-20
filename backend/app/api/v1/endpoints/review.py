from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.user import User

from app.schemas import (
    ReviewRequest,
    ReviewResponse,
    ReviewRead,
    ReviewSubmitIn,
    ReviewSubmitOut,
)

from app.domain.reviews.use_cases import EvaluateText, SubmitReview, ListMyReviews

from app.domain.reviews.exceptions import InvalidReview

from app.api.v1.deps import (
    get_evaluate_text_uc,
    get_submit_review_uc,
    get_list_my_reviews_uc,
)

router = APIRouter()


@router.post("/evaluate", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
def evaluate_review(
    payload: ReviewRequest,
    current_user: User = Depends(get_current_user),
    uc: EvaluateText = Depends(get_evaluate_text_uc),
):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        ev = uc.execute(text=payload.text)
        return ReviewResponse(
            text=ev.text,
            sentiment=ev.sentiment,
            polarity=ev.polarity,
            suggestion=ev.suggestion,
            status=ev.status,
            feedback=ev.feedback,
        )
    except InvalidReview as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/submit", response_model=ReviewSubmitOut, status_code=status.HTTP_200_OK)
def submit_review(
    payload: ReviewSubmitIn,
    current_user: User = Depends(get_current_user),
    uc: SubmitReview = Depends(get_submit_review_uc),
):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    try:
        res = uc.execute(
            user_id=current_user.id,
            text=payload.text,
            draft_token=payload.draft_token,
            group_id=payload.group_id,
        )

        return ReviewSubmitOut(
            saved=res.saved,
            review_id=res.review_id,
            draft_token=res.draft_token,
            group_id=res.group_id,
            evaluation={
                "text": res.evaluation.text,
                "sentiment": res.evaluation.sentiment,
                "polarity": res.evaluation.polarity,
                "status": res.evaluation.status,
                "suggestion": res.evaluation.suggestion,
                "feedback": res.evaluation.feedback,
            },
        )
    except InvalidReview as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/mine", response_model=List[ReviewRead], status_code=status.HTTP_200_OK)
def list_my_reviews(
    current_user: User = Depends(get_current_user),
    uc: ListMyReviews = Depends(get_list_my_reviews_uc),
):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    entities = uc.execute(user_id=current_user.id)
    return [
        ReviewRead(
            id=e.id,
            user_id=e.user_id,
            original_text=e.original_text,
            corrected_text=e.corrected_text,
            sentiment=e.sentiment,
            polarity=e.polarity,
            status=e.status,
            suggestion=e.suggestion,
            feedback=e.feedback,
            created_at=e.created_at,
            updated_at=e.updated_at,
        )
        for e in entities
    ]

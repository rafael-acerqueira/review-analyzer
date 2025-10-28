from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.dependencies import get_current_user
from app.models.user import User

from app.schemas import (
    ReviewRequest,
    ReviewResponse,
    ReviewRead, ReviewCreate
)

from app.domain.reviews.use_cases import EvaluateText, ListMyReviews, SaveApprovedReview, SaveApprovedInput

from app.domain.reviews.exceptions import InvalidReview

from app.api.v1.deps import (
    get_evaluate_text_uc,
    get_list_my_reviews_uc, get_save_approved_uc,
)

router = APIRouter()


@router.post("/analyze_review", response_model=ReviewResponse, status_code=status.HTTP_200_OK)
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


@router.post("/reviews", response_model=ReviewRead, status_code=status.HTTP_201_CREATED)
def create_review(
    data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    uc: SaveApprovedReview = Depends(get_save_approved_uc),
):
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authorized")

    if not (data.text and data.text.strip()):
        raise HTTPException(400, detail="Missing original text (text)")

    try:
        ent = uc.execute(
            SaveApprovedInput(
                user_id=current_user.id,
                text=data.text,
                corrected_text=data.corrected_text,
                sentiment=data.sentiment,
                status=data.status,
                feedback=data.feedback,
                suggestion=data.suggestion,
            )
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return ReviewRead(
        id=ent.id,
        text=ent.text,
        corrected_text=ent.corrected_text,
        sentiment=ent.sentiment,
        status=ent.status,
        feedback=ent.feedback,
        suggestion=ent.suggestion,
        user_id=ent.user_id,
        created_at=ent.created_at,
    )


@router.get("/my-reviews", response_model=List[ReviewRead], status_code=status.HTTP_200_OK)
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
            text=e.text,
            corrected_text=e.corrected_text,
            sentiment=e.sentiment,
            status=e.status,
            suggestion=e.suggestion,
            feedback=e.feedback,
            created_at=e.created_at
        )
        for e in entities
    ]

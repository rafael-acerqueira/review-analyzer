# app/api/v1/endpoints/admin.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import List, Optional
from datetime import datetime, date

from app.models.user import User
from app.schemas import ReviewRead
from app.dependencies import get_current_user

from app.api.v1.deps import (
    get_admin_list_uc,
    get_admin_delete_uc,
    get_admin_stats_uc,
)

from app.domain.admin.use_cases import (
    ListReviews as AdminListReviews,
    DeleteReview as AdminDeleteReview,
    GetStats as AdminGetStats,
)

router = APIRouter()


def _ensure_admin(user: User):
    if not user or user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")


@router.get("/reviews", response_model=List[ReviewRead], status_code=status.HTTP_200_OK)
def list_reviews(
    current_user: User = Depends(get_current_user),
    sentiment: Optional[str] = None,
    status: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    uc: AdminListReviews = Depends(get_admin_list_uc),
):
    _ensure_admin(current_user)
    rows = uc.execute(
        sentiment=sentiment,
        status=status,
        date_from=date_from,
        date_to=date_to,
    )
    return [
        ReviewRead(
            id=r.id,
            text=r.text,
            corrected_text=r.corrected_text,
            sentiment=r.sentiment,
            status=r.status,
            feedback=r.feedback,
            suggestion=r.suggestion,
            user_id=r.user_id,
            created_at=r.created_at,
        )
        for r in rows
    ]


@router.delete("/reviews/{review_id}", status_code=status.HTTP_200_OK)
def remove_review(
    review_id: int,
    current_user: User = Depends(get_current_user),
    uc: AdminDeleteReview = Depends(get_admin_delete_uc),
):
    _ensure_admin(current_user)
    ok = uc.execute(review_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Review not found")

    return {"deleted": True, "review_id": review_id}


@router.get("/stats", status_code=status.HTTP_200_OK)
def get_admin_stats(
    current_user: User = Depends(get_current_user),
    from_date: Optional[date] = Query(None, description="Start date for stats"),
    to_date: Optional[date] = Query(None, description="End date for stats"),
    user_id: Optional[int] = Query(None, description="Filter by user id"),
    uc: AdminGetStats = Depends(get_admin_stats_uc),
):
    _ensure_admin(current_user)
    agg = uc.execute(from_date=from_date, to_date=to_date, user_id=user_id)

    return {
        "period": {
            "from": agg.period.from_date,
            "to": agg.period.to_date,
        },
        "total_reviews": agg.total_reviews,
        "by_sentiment": agg.by_sentiment,
        "by_status": agg.by_status,
        "percent_accepted": agg.percent_accepted,
        "percent_rejected": agg.percent_rejected,
        "top_rejection_reasons": [
            {"reason": r.reason, "count": r.count} for r in agg.top_rejection_reasons
        ],
        "filters": {
            "user_id": agg.user_id,
        },
    }

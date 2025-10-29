from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional, Dict, List


@dataclass
class Period:
    from_date: date
    to_date: date


@dataclass
class RejectionReason:
    reason: str
    count: int


@dataclass
class AdminStats:
    period: Period
    total_reviews: int
    by_sentiment: Dict[str, int]
    by_status: Dict[str, int]
    percent_accepted: float
    percent_rejected: float
    top_rejection_reasons: List[RejectionReason]
    user_id: Optional[int] = None

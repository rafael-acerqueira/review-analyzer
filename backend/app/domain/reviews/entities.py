from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass(frozen=True)
class ReviewEntity:
    id: int
    user_id: int
    text: str
    corrected_text: str


    sentiment: Optional[str] = None
    polarity: Optional[float] = None
    status: Optional[str] = None
    suggestion: Optional[str] = None
    feedback: Optional[str] = None

    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


__all__ = ["ReviewEntity"]

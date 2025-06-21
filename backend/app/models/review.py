from sqlmodel import SQLModel, Field,Relationship
from typing import Optional
from datetime import datetime, timezone

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    corrected_text: Optional[str] = ""
    sentiment: str
    status: str
    feedback: str
    suggestion: Optional[str] = ""
    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"] = Relationship(back_populates="reviews")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
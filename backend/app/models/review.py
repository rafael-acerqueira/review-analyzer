from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime, timezone

class Review(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    text: str
    sentiment: str
    status: str
    feedback: str
    suggestion: Optional[str] = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
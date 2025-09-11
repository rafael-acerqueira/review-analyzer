from sqlmodel import SQLModel, Field,Relationship
from typing import Optional, List
from datetime import datetime, timezone
from sqlalchemy import Column
from pgvector.sqlalchemy import Vector

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

    embedding: Optional[List[float]] = Field(
        default=None,
        sa_column=Column(Vector(384))
    )
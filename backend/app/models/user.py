from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from datetime import datetime, timezone

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    hashed_password: str | None = None
    provider: str = "credentials"
    sub: str | None = None
    role: str = Field(default="user")
    reviews: list["Review"] = Relationship(back_populates="user")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
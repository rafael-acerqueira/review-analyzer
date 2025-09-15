from typing import List, Optional

from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime


class ReviewRequest(BaseModel):
    text: str

class ReviewResponse(BaseModel):
    text: str
    sentiment: str
    polarity: float
    suggestion: str
    status: str
    feedback: str

class ReviewRead(BaseModel):
    id: int
    text: str
    corrected_text: str | None = None
    sentiment: str
    status: str
    feedback: str
    suggestion: str | None = None
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class GoogleUser(BaseModel):
    email: EmailStr
    sub: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class TokenExchangeIn(BaseModel):
    email: EmailStr
    sub: str

class RefreshIn(BaseModel):
    refresh_token: str

class TokensOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 15 * 60

class RagSearchIn(BaseModel):
    text: str
    k: int = 5
    min_score: Optional[float] = None

class RagHit(BaseModel):
    id: int
    text: str
    score: float

class RagSearchOut(BaseModel):
    results: List[RagHit]
    model_config = ConfigDict(from_attributes=True)
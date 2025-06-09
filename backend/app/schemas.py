from pydantic import BaseModel, EmailStr


class ReviewRequest(BaseModel):
    text: str

class ReviewResponse(BaseModel):
    text: str
    sentiment: str
    polarity: float
    suggestion: str
    status: str
    feedback: str

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class GoogleUser(BaseModel):
    email: EmailStr
    provider_id: str
    sub: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str
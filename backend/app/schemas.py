from pydantic import BaseModel

class ReviewRequest(BaseModel):
    text: str

class ReviewResponse(BaseModel):
    text: str
    sentiment: str
    polarity: float
    suggestion: str
    status: str
    feedback: str
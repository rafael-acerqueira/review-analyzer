from fastapi import FastAPI
from api.v1.endpoints import review

app = FastAPI(title="Review Helper API")

app.include_router(review.router, prefix="/api/v1")
from fastapi import FastAPI
from app.api.v1.endpoints import review, admin

app = FastAPI(title="Review Helper API")

@app.get("/")
async def root():
    return {"status": "ok"}

app.include_router(review.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1/admin")

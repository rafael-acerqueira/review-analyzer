from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import review, admin, auth, rag
import os
import uvicorn

app = FastAPI(title="Review Helper API")

@app.get("/")
async def root():
    return {"status": "ok"}

def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "https://review-analyzer.vercel.app")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1/admin")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(rag.router, prefix="/api/v1/rag")

if __name__ == "__main__":
    port = int(os.getenv("PORT", "7860"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

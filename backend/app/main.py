from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import review, admin, auth, rag
from app.core.settings import get_settings
import uvicorn

settings = get_settings()
app = FastAPI(title="Review Helper API")

@app.get("/")
async def root():
    return {"status": "ok"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(review.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1/admin")
app.include_router(auth.router, prefix="/api/v1/auth")
app.include_router(rag.router, prefix="/api/v1/rag")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=False)

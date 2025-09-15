from fastapi import APIRouter, Depends
from sqlmodel import Session
from app.schemas import RagSearchIn, RagSearchOut, RagHit
from app.dependencies import get_session
from app.services.retriever import search_similar_reviews

router = APIRouter()

@router.post("/search", response_model=RagSearchOut)
def rag_search(payload: RagSearchIn, session: Session = Depends(get_session)):
    hits = search_similar_reviews(
        session=session,
        query_text=payload.text,
        k=payload.k,
        min_score=payload.min_score,
    )
    return RagSearchOut(results=[RagHit(**h) for h in hits])
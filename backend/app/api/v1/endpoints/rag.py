from fastapi import APIRouter, Depends
from app.schemas import RagSearchIn, RagSearchOut, RagHit as RagHitSchema

from app.domain.rag.use_cases import SearchRag
from app.api.v1.deps import get_rag_uc

router = APIRouter()


@router.post("/search", response_model=RagSearchOut)
def rag_search(payload: RagSearchIn, uc: SearchRag = Depends(get_rag_uc)):
    result = uc.execute(text=payload.text, k=payload.k, min_score=payload.min_score)
    hits = [RagHitSchema(id=h.id, text=h.text, score=h.score) for h in result.hits]
    return RagSearchOut(results=hits)
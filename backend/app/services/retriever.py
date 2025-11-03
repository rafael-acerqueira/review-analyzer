from typing import Sequence
from sqlmodel import Session, select
from sqlalchemy import text
from sqlalchemy.sql import func
from app.models.review import Review
import os

_IVFFLAT_PROBES = int(os.getenv("RAG_PROBES", "15"))

def retrieve_candidates(
    session: Session,
    qemb: list[float],
    top_n: int = 50,
    min_score: float | None = None,
) -> list[dict]:
    try:
        session.exec(text("SET ivfflat.probes = 15"))
    except Exception:
        pass

    dist = Review.embedding.cosine_distance(qemb)
    score = (1 - dist).label("score")
    stmt = (
        select(
            Review.id,
            func.coalesce(func.nullif(Review.corrected_text, ""), Review.text).label("content"),
            Review.embedding,
            score,
        )
        .where(
            Review.status == "approved",
            Review.embedding.isnot(None),
        )
        .order_by(score.desc())
        .limit(top_n)
    )

    rows = session.exec(stmt).all()
    out = []
    for rid, content, emb, s in rows:
        if hasattr(emb, "tolist"):
            emb = emb.tolist()
        item = {"id": rid, "content": (content or "")[:2000], "embedding": emb, "score": float(s)}
        out.append(item)

    if min_score is not None:
        out = [x for x in out if x["score"] >= min_score]
    return out


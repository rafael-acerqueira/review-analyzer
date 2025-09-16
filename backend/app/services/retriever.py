from typing import List, Dict, Any, Sequence
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlmodel import Session, select
from sqlalchemy import text
from sqlalchemy.sql import func
from app.models.review import Review
from app.embeddings import embed_text_query


def _is_postgres(session: Session) -> bool:
    return session.get_bind().dialect.name.startswith("postgres")

def _to_list(x: Sequence[float]) -> list[float]:
    try:
        return [float(v) for v in x]
    except Exception:
        return []

def _to_vector_literal(values: list[float]) -> str:
    return "[" + ",".join(f"{v:.8f}" for v in values) + "]"

def search_similar_reviews(
    session: Session,
    query_text: str,
    k: int = 5,
    min_score: float = 0.7,
) -> List[Dict[str, Any]]:

    qemb = _to_list(embed_text_query(query_text))
    if not qemb:
        return []

    col_dim = getattr(Review.__table__.c.embedding.type, "dim", None)
    dim = col_dim or len(qemb)

    if dim is not None and len(qemb) != dim:
        print(f"[RAG] embedding dimension ({len(qemb)}) != column ({dim})")
        return []

    qemb_vec = sa.cast(sa.literal(_to_vector_literal(qemb), sa.String()), Vector(dim))

    if not _is_postgres(session):
        return []

    try:
        session.exec(text("SET ivfflat.probes = 10"))
    except Exception:
        pass

    dist_expr = sa.cast(Review.embedding.op("<=>")(qemb_vec), sa.Float).label("distance")

    stmt = (
        select(
            Review.id,
            func.coalesce(func.nullif(Review.corrected_text, ""), Review.text).label("content"),
            dist_expr,
        )
        .where(
            Review.embedding.isnot(None),
        )
        .order_by(dist_expr.asc())
        .limit(k)
    )

    rows = session.exec(stmt).all()

    results: List[Dict[str, Any]] = []
    for r in rows:
        score = 1.0 - float(r.distance)
        if min_score is None or score >= min_score:
            snippet = (r.content or "")[:400]
            results.append({"id": r.id, "text": snippet, "score": score})

    return results

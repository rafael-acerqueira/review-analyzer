from __future__ import annotations

from typing import List, Optional

from sqlalchemy import text
from sqlmodel import Session

from app.domain.rag.entities import RagHit
from app.domain.rag.interfaces import RagRepository


__all__ = ["SqlModelRagRepository"]


class SqlModelRagRepository(RagRepository):
    def __init__(self, db: Session):
        self.db = db

    def _format_vector_literal(self, emb: List[float]) -> str:
        return "[" + ",".join(f"{x:.6f}" for x in emb) + "]"

    def search_by_embedding(
        self,
        *,
        embedding: List[float],
        k: int = 5,
        min_score: Optional[float] = None,
    ) -> List[RagHit]:
        k = max(1, int(k or 5))

        q_vec = self._format_vector_literal(embedding)

        sql = text(
            """
            SET LOCAL ivfflat.probes = 15;

            SELECT
                r.id,
                r.text,
                1 - (r.embedding <=> CAST(:q AS vector)) AS score
            FROM review AS r
            WHERE r.embedding IS NOT NULL
            ORDER BY r.embedding <=> CAST(:q AS vector) ASC
            LIMIT :k
            """
        )

        rows = self.db.execute(sql, {"q": q_vec, "k": k}).all()

        hits = [RagHit(id=row.id, text=row.text, score=float(row.score)) for row in rows]

        if min_score is not None:
            hits = [h for h in hits if h.score >= float(min_score)]

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits

    def ensure_ivfflat_cosine_index(self) -> None:
        create_idx_sql = text(
            """
            CREATE INDEX IF NOT EXISTS review_embedding_cosine_idx
            ON review
            USING ivfflat (embedding vector_cosine_ops);
            """
        )
        self.db.exec(create_idx_sql)
        self.db.commit()

# app/infra/embeddings/local_sentence_transformer.py
from __future__ import annotations

import os
import threading
from typing import List, Optional

from app.domain.rag.interfaces import Embedder

try:
    from sentence_transformers import SentenceTransformer
except Exception:
    SentenceTransformer = None  # type: ignore


__all__ = ["LocalSentenceTransformerEmbedder"]


class LocalSentenceTransformerEmbedder(Embedder):
    _model_lock = threading.Lock()
    _model: Optional["SentenceTransformer"] = None

    def __init__(
        self,
        model_name: Optional[str] = None,
        device: Optional[str] = None,
        expected_dim: Optional[int] = None,
        query_prefix: Optional[str] = None,
    ) -> None:
        if SentenceTransformer is None:
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Add it to your dependencies or provide a different Embedder."
            )

        self.model_name = model_name or os.getenv(
            "EMBEDDINGS_MODEL_NAME",
            "intfloat/multilingual-e5-small",
        )
        self.device = device or os.getenv("RAG_EMBEDDING_DEVICE", "cpu")
        self.expected_dim = expected_dim
        if self.expected_dim is None:
            try:
                self.expected_dim = int(os.getenv("RAG_EXPECTED_DIM", "").strip() or 0) or None
            except Exception:
                self.expected_dim = None

        self.query_prefix = query_prefix if query_prefix is not None else os.getenv(
            "RAG_E5_QUERY_PREFIX", "query: "
        )

        if self.__class__._model is None:
            with self.__class__._model_lock:
                if self.__class__._model is None:
                    self.__class__._model = SentenceTransformer(self.model_name, device=self.device)

        self._m = self.__class__._model

    def embed(self, text: str) -> List[float]:
        t = (text or "").strip()
        if not t:
            return []

        q = f"{self.query_prefix}{t}" if self.query_prefix else t

        vec = self._m.encode(q, normalize_embeddings=True)  # np.ndarray
        emb = [float(x) for x in vec.tolist()]

        if self.expected_dim is not None and len(emb) != self.expected_dim:
            raise RuntimeError(
                f"Embedding dimension mismatch: expected {self.expected_dim}, got {len(emb)} "
                f"(model={self.model_name})"
            )
        return emb

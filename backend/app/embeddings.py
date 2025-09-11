from typing import List
from sentence_transformers import SentenceTransformer
import os

_MODEL_NAME = os.getenv("EMBEDDINGS_MODEL_NAME", "intfloat/multilingual-e5-small")
_model = SentenceTransformer(_MODEL_NAME)

def embed_text_passage(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        return []
    v = _model.encode(f"passage: {text}", normalize_embeddings=True)
    return v.tolist()

def embed_text_query(text: str) -> List[float]:
    text = (text or "").strip()
    if not text:
        return []
    v = _model.encode(f"query: {text}", normalize_embeddings=True)
    return v.tolist()
from typing import List, Dict
from sentence_transformers import CrossEncoder

_reranker = None

def get_reranker(model_name: str) -> CrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = CrossEncoder(model_name, trust_remote_code=True)
    return _reranker

def rerank(query: str, docs: List[Dict], model_name: str, topk: int = 3) -> List[Dict]:
    if not docs:
        return []
    ce = get_reranker(model_name)
    pairs = [(query, d["content"]) for d in docs]
    scores = ce.predict(pairs)  # np.ndarray
    ranked = sorted(
        [dict(d, rerank_score=float(s)) for d, s in zip(docs, scores)],
        key=lambda x: x["rerank_score"],
        reverse=True
    )
    return ranked[:topk]
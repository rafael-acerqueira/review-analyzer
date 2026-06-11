from typing import Any, Dict, List, Callable, Optional, Protocol
import json
import logging
import os

import numpy as np
from app.utils.prompts import suggestion_prompt_template
from app.core.clients import call_llm
from app.services.ranking import mmr_select
from app.services.reranker import rerank


RAG_ENABLED      = os.getenv("RAG_ENABLED", "true").lower() in ("1", "true", "yes")
TOPN             = int(os.getenv("RAG_TOPN", "50"))
MMR_L            = float(os.getenv("RAG_MMR_LAMBDA", "0.7"))
MMR_K            = int(os.getenv("RAG_MMR_K", "8"))
RERANK_MODEL     = os.getenv("RAG_RERANKER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2")
RERANK_TOPK      = int(os.getenv("RAG_RERANKER_TOPK", "3"))
MAX_USER_TEXT    = int(os.getenv("MAX_USER_TEXT_CHARS", "2000"))
MAX_SNIPPET_CHARS= int(os.getenv("MAX_SNIPPET_CHARS", "400"))

logger = logging.getLogger(__name__)

def _cut(s: str, n: int) -> str:
    return (s or "").strip()[:n]

def _render_examples_block(docs: List[Dict[str, Any]]) -> str:
    if not docs:
        return "NO_EXAMPLES_FOUND"
    lines = []
    for d in docs[:RERANK_TOPK]:
        snippet = _cut((d.get("content") or "").replace("\n", " "), MAX_SNIPPET_CHARS)
        base = f'[ID={d.get("id","NA")} | score={d.get("score",0.0):.2f}]'
        if "rerank_score" in d:
            base += f' [rerank={d["rerank_score"]:.2f}]'
        lines.append(f'{base}\n"{snippet}"')
    return "\n\n".join(lines)

def _parse_llm_json(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    decoder = json.JSONDecoder()

    for idx, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed

    raise json.JSONDecodeError("No JSON object found", text, 0)

def _normalize_status(value: Any) -> Optional[str]:
    status = str(value or "").strip().lower()
    if status in ("accepted", "accept", "approved", "approve"):
        return "Accepted"
    if status in ("rejected", "reject"):
        return "Rejected"
    return None

def _as_text(value: Any, max_chars: Optional[int] = None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        text = value
    else:
        text = json.dumps(value, ensure_ascii=False)
    text = text.strip()
    return text[:max_chars] if max_chars is not None else text

RetrieverFn = Callable[[str, int, Optional[float]], List[Dict[str, Any]]]

class Embedder(Protocol):
    def embed(self, text: str) -> List[float]:
        ...

class SuggestionService:
    def __init__(self, retriever: Optional[RetrieverFn] = None, query_embedder: Optional[Embedder] = None) -> None:
        self.retriever = retriever
        self.query_embedder = query_embedder

    def evaluate(
        self,
        *,
        text: str,
        min_score: float = 0.70,
    ) -> Dict[str, Any]:
        user_text = _cut(text, MAX_USER_TEXT)

        examples: List[Dict[str, Any]] = []
        if RAG_ENABLED and self.retriever:
            try:
                cands = self.retriever(user_text, TOPN, min_score) or []

                cands = [
                    {"id": c.get("id"), "text": c.get("text"), "content": c.get("text"), "score": float(c.get("score", 0.0))}
                    for c in cands
                ]
                if cands and self.query_embedder:
                    try:
                        q = np.asarray(self.query_embedder.embed(user_text), dtype=np.float32)
                        cands = mmr_select(q, cands, k=MMR_K, lamb=MMR_L)
                    except Exception:
                        logger.warning("RAG MMR selection failed; continuing without MMR", exc_info=True)

                if cands:
                    try:
                        cands = rerank(user_text, cands, model_name=RERANK_MODEL, topk=RERANK_TOPK)
                    except Exception:
                        logger.warning("RAG reranker failed; using top candidates without reranking", exc_info=True)
                        cands = cands[:RERANK_TOPK]

                examples = cands
            except Exception:
                logger.warning("RAG retrieval failed; evaluating without examples", exc_info=True)
                examples = []

        prompt = suggestion_prompt_template(review_text=user_text, examples_block=_render_examples_block(examples))

        try:
            raw = call_llm(prompt)
        except Exception:
            return {"status": "Rejected", "feedback": "AI error. Please try again later.", "suggestion": ""}

        try:
            parsed = _parse_llm_json(raw)
            status = _normalize_status(parsed.get("status"))
            if status is None:
                status = "Accepted" if len(user_text.split()) >= 20 else "Rejected"
            return {
                "status": status,
                "feedback": _as_text(parsed.get("feedback"), max_chars=200),
                "suggestion": _as_text(parsed.get("suggestion")),
            }
        except json.JSONDecodeError:
            return {"status": "Rejected", "feedback": "Unexpected AI response.", "suggestion": ""}

from dataclasses import dataclass
from typing import Optional, List

from app.domain.reviews.entities import ReviewEntity
from app.domain.reviews.interfaces import ReviewRepository, SentimentAnalyzer, SuggestionEngine, DraftProvider
from app.domain.reviews.exceptions import InvalidReview

from app.domain.rag.interfaces import Embedder

@dataclass(frozen=True)
class EvaluationResult:
    text: str
    sentiment: Optional[str]
    polarity: Optional[float]
    status: Optional[str]
    suggestion: Optional[str]
    feedback: Optional[str]

@dataclass(frozen=True)
class SubmitResult:
    saved: bool
    review_id: Optional[int]
    draft_token: Optional[str]
    group_id: Optional[str]
    evaluation: EvaluationResult

class EvaluateText:
    def __init__(self, sentiment: SentimentAnalyzer, sugg: SuggestionEngine, min_length: int = 20):
        self.sentiment = sentiment
        self.sugg = sugg
        self.min_length = min_length

    def execute(self, *, text: str) -> EvaluationResult:
        text = (text or "").strip()
        if not text or len(text) < self.min_length:
            raise InvalidReview("too_short")
        try:
            s, p = self.sentiment.analyze(text)
        except Exception:
            s, p = None, None
        try:
            sdict = self.sugg.evaluate(text=text) or {}
            status = sdict.get("status")
            suggestion = sdict.get("suggestion")
            feedback = sdict.get("feedback")
        except Exception:
            status = suggestion = feedback = None

        s = s or "unknown"
        p = float(p) if p is not None else 0.0
        status = status or "pending"
        suggestion = suggestion or ""
        feedback = feedback or ""

        return EvaluationResult(
            text=text,
            sentiment=s,
            polarity=p,
            status=status,
            suggestion=suggestion,
            feedback=feedback,
        )

@dataclass(frozen=True)
class SaveApprovedInput:
    user_id: int
    text: str
    corrected_text: str
    sentiment: str
    status: str
    feedback: str
    suggestion: Optional[str]

@dataclass
class SaveApprovedReview:
    repo: ReviewRepository
    embedder: Embedder

    def execute(self, data: SaveApprovedInput) -> ReviewEntity:
        status = (data.status or "").strip().lower()
        if status != "accepted":
            raise ValueError("Only Accepted reviews can be created")

        original = (data.text or "").strip()
        corrected = (data.corrected_text or "").strip()
        if not original:
            raise ValueError("Missing original text")

        doc_text = corrected or original

        embedding: List[float] = self.embedder.embed(doc_text)
        if not embedding:
            raise ValueError("Failed to generate embedding")

        return self.repo.create_approved(
            user_id=data.user_id,
            text=original,
            corrected_text=corrected,
            sentiment=(data.sentiment or "unknown"),
            status=status,
            feedback=(data.feedback or ""),
            suggestion=(data.suggestion or ""),
            embedding=embedding,  # << NOVO
        )

class ListMyReviews:
    def __init__(self, reviews: ReviewRepository):
        self.reviews = reviews

    def execute(self, *, user_id: int) -> List[ReviewEntity]:
        return self.reviews.list_by_user(user_id=user_id)
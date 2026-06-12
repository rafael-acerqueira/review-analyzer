from dataclasses import dataclass
from typing import Optional, List

from app.domain.reviews.entities import ReviewEntity
from app.domain.reviews.interfaces import ReviewRepository, SentimentAnalyzer, SuggestionEngine
from app.domain.reviews.exceptions import InvalidReview

from app.domain.rag.interfaces import Embedder

ACCEPTED_STATUSES = {"accepted", "accept", "approved", "approve"}
REJECTED_STATUSES = {"rejected", "reject", "denied", "deny"}


def normalize_review_status(value: Optional[str]) -> str:
    status = (value or "").strip().lower()
    if status in ACCEPTED_STATUSES:
        return "Accepted"
    if status in REJECTED_STATUSES:
        return "Rejected"
    return "Rejected"


def normalize_sentiment(value: Optional[str]) -> str:
    sentiment = (value or "UNKNOWN").strip()
    return sentiment.upper() if sentiment else "UNKNOWN"


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

        s = normalize_sentiment(s)
        p = float(p) if p is not None else 0.0
        status = normalize_review_status(status)
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
    expected_embedding_dim: int = 384

    def execute(self, data: SaveApprovedInput) -> ReviewEntity:
        status = (data.status or "").strip()
        if status.lower() != "accepted":
            raise ValueError("Only Accepted reviews can be created")

        original = (data.text or "").strip()
        corrected = (data.corrected_text or "").strip()
        if not original:
            raise ValueError("Missing original text")

        doc_text = corrected or original

        embedding = self.embedder.embed(doc_text) or []
        if embedding and len(embedding) != self.expected_embedding_dim:
            raise ValueError(
                f"Invalid embedding dimension: expected {self.expected_embedding_dim}, got {len(embedding)}"
            )

        return self.repo.create_approved(
            user_id=data.user_id,
            text=original,
            corrected_text=corrected,
            sentiment=(data.sentiment or "unknown"),
            status="Accepted",
            feedback=(data.feedback or ""),
            suggestion=(data.suggestion or ""),
            embedding=embedding if embedding else None,
        )

class ListMyReviews:
    def __init__(self, reviews: ReviewRepository):
        self.reviews = reviews

    def execute(self, *, user_id: int) -> List[ReviewEntity]:
        return self.reviews.list_by_user(user_id=user_id)

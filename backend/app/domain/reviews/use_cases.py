from dataclasses import dataclass
from typing import Optional, List
import uuid
from app.domain.reviews.entities import ReviewEntity
from app.domain.reviews.interfaces import ReviewRepository, SentimentAnalyzer, SuggestionEngine, DraftProvider
from app.domain.reviews.exceptions import InvalidReview

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
    def __init__(self, sentiment: SentimentAnalyzer, sugg: SuggestionEngine, min_length: int = 5):
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
        return EvaluationResult(text=text, sentiment=s, polarity=p, status=status, suggestion=suggestion, feedback=feedback)

class SubmitReview:
    def __init__(self, reviews: ReviewRepository, evaluator: EvaluateText, drafts: DraftProvider):
        self.reviews = reviews
        self.evaluator = evaluator
        self.drafts = drafts

    def execute(self, *, user_id: int, text: str, draft_token: Optional[str] = None, group_id: Optional[str] = None) -> SubmitResult:
        ev = self.evaluator.execute(text=text)

        text: Optional[str] = None
        draft_group_id = group_id or str(uuid.uuid4())

        if draft_token:
            try:
                payload = self.drafts.decode(draft_token)

                if str(user_id) == str(payload.get("sub")):
                    text = payload.get("text")

                    draft_group_id = payload.get("group_id") or draft_group_id
            except Exception:
                text = None

        if ev.status == "approved":
            if not text:
                text = ev.text

            created = self.reviews.create_approved(
                user_id=user_id,
                text=text,
                corrected_text=ev.text,
                sentiment=ev.sentiment,
                polarity=ev.polarity,
                suggestion=ev.suggestion,
                feedback=ev.feedback,
            )
            return SubmitResult(
                saved=True,
                review_id=created.id,
                draft_token=None,
                group_id=draft_group_id,
                evaluation=ev,
            )

        if not text:
            text = ev.text

        token = self.drafts.create(user_id=user_id, text=text, group_id=draft_group_id)
        return SubmitResult(
            saved=False,
            review_id=None,
            draft_token=token,
            group_id=draft_group_id,
            evaluation=ev,
        )

class ListMyReviews:
    def __init__(self, reviews: ReviewRepository):
        self.reviews = reviews

    def execute(self, *, user_id: int) -> List[ReviewEntity]:
        return self.reviews.list_by_user(user_id=user_id)
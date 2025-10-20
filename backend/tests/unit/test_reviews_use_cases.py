import pytest
from dataclasses import dataclass
from typing import Optional, List, Dict

from app.domain.reviews.entities import ReviewEntity
from app.domain.reviews.use_cases import EvaluateText, SubmitReview, ListMyReviews
from app.domain.reviews.exceptions import InvalidReview
from app.domain.reviews.interfaces import (
    ReviewRepository, SentimentAnalyzer, SuggestionEngine, DraftProvider
)



class FakeReviewRepository(ReviewRepository):
    def __init__(self):
        self._auto_id = 1
        self.saved: Dict[int, ReviewEntity] = {}
        self.by_user: Dict[int, List[int]] = {}

    def create_approved(
        self,
        *,
        user_id: int,
        text: str,
        corrected_text: str,
        sentiment: Optional[str],
        polarity: Optional[float],
        suggestion: Optional[str],
        feedback: Optional[str] = None,
    ) -> ReviewEntity:
        rid = self._auto_id
        self._auto_id += 1
        ent = ReviewEntity(
            id=rid,
            user_id=user_id,
            text=text,
            corrected_text=corrected_text,
            sentiment=sentiment,
            polarity=polarity,
            status="approved",
            suggestion=suggestion,
            feedback=feedback,
            created_at=None,
            updated_at=None,
        )
        self.saved[rid] = ent
        self.by_user.setdefault(user_id, []).append(rid)
        return ent

    def get(self, review_id: int) -> Optional[ReviewEntity]:
        return self.saved.get(review_id)

    def list_by_user(self, *, user_id: int) -> List[ReviewEntity]:
        return [self.saved[i] for i in self.by_user.get(user_id, [])]

    def list_filtered(self, **kwargs) -> List[ReviewEntity]: return []
    def delete(self, review_id: int) -> bool: return False
    def stats(self, **kwargs) -> dict: return {}


class FakeSentimentAnalyzer(SentimentAnalyzer):
    def __init__(self, sentiment: str = "positive", polarity: float = 0.9):
        self.sentiment = sentiment
        self.polarity = polarity

    def analyze(self, text: str):
        return self.sentiment, self.polarity


class FakeSuggestionEngine(SuggestionEngine):
    def __init__(self, status: str = "approved", suggestion: Optional[str] = None, feedback: Optional[str] = None):
        self._status = status
        self._suggestion = suggestion
        self._feedback = feedback

    def evaluate(self, *, text: str) -> dict:
        return {
            "status": self._status,
            "suggestion": self._suggestion,
            "feedback": self._feedback,
        }


class FakeDraftProvider(DraftProvider):
    def __init__(self):
        self._store: Dict[str, dict] = {}
        self._seq = 1

    def create(self, *, user_id: int, text: str, group_id: str) -> str:
        tok = f"T{self._seq}"
        self._seq += 1
        self._store[tok] = {"sub": str(user_id), "text": text, "group_id": group_id}
        return tok

    def decode(self, token: str) -> dict:
        return self._store[token]




def test_evaluate_text_rejects_too_short():
    sentiment = FakeSentimentAnalyzer()
    sugg = FakeSuggestionEngine()
    uc = EvaluateText(sentiment=sentiment, sugg=sugg, min_length=5)

    with pytest.raises(InvalidReview):
        uc.execute(text="hi")


def test_evaluate_text_ok():
    sentiment = FakeSentimentAnalyzer(sentiment="neutral", polarity=0.1)
    sugg = FakeSuggestionEngine(status="rejected", suggestion="add more details", feedback="too short")
    uc = EvaluateText(sentiment=sentiment, sugg=sugg, min_length=3)

    ev = uc.execute(text="hello world")
    assert ev.text == "hello world"
    assert ev.sentiment == "neutral"
    assert ev.polarity == 0.1
    assert ev.status == "rejected"
    assert ev.suggestion == "add more details"
    assert ev.feedback == "too short"




def test_submit_review_first_attempt_approved_saves_with_original_equals_corrected():
    repo = FakeReviewRepository()
    sentiment = FakeSentimentAnalyzer("positive", 0.8)
    sugg = FakeSuggestionEngine(status="approved", suggestion="looks good")
    evaluator = EvaluateText(sentiment, sugg, min_length=3)
    drafts = FakeDraftProvider()

    uc = SubmitReview(reviews=repo, evaluator=evaluator, drafts=drafts)
    res = uc.execute(user_id=10, text="great product!")

    assert res.saved is True
    assert res.review_id is not None
    saved = repo.get(res.review_id)
    assert saved is not None
    assert saved.text == "great product!"
    assert saved.corrected_text == "great product!"
    assert saved.status == "approved"
    assert saved.sentiment == "positive"
    assert saved.polarity == 0.8
    assert res.draft_token is None


def test_submit_review_first_attempt_rejected_returns_draft_token_without_saving():
    repo = FakeReviewRepository()
    sentiment = FakeSentimentAnalyzer("negative", -0.3)
    sugg = FakeSuggestionEngine(status="rejected", suggestion="please explain more", feedback="vague")
    evaluator = EvaluateText(sentiment, sugg, min_length=3)
    drafts = FakeDraftProvider()

    uc = SubmitReview(reviews=repo, evaluator=evaluator, drafts=drafts)
    res = uc.execute(user_id=20, text="bad")

    assert res.saved is False
    assert res.review_id is None
    assert res.draft_token is not None
    assert len(repo.list_by_user(user_id=20)) == 0


def test_submit_review_second_attempt_with_draft_token_saves_original_and_corrected():
    repo = FakeReviewRepository()
    drafts = FakeDraftProvider()

    evaluator1 = EvaluateText(
        sentiment=FakeSentimentAnalyzer("negative", -0.2),
        sugg=FakeSuggestionEngine(status="rejected", suggestion="add details"),
        min_length=3,
    )
    uc = SubmitReview(reviews=repo, evaluator=evaluator1, drafts=drafts)
    res1 = uc.execute(user_id=30, text="ok man")
    assert res1.saved is False
    assert res1.draft_token is not None

    evaluator2 = EvaluateText(
        sentiment=FakeSentimentAnalyzer("positive", 0.7),
        sugg=FakeSuggestionEngine(status="approved", suggestion=""),
        min_length=3,
    )
    uc2 = SubmitReview(reviews=repo, evaluator=evaluator2, drafts=drafts)
    res2 = uc2.execute(user_id=30, text="now with enough details", draft_token=res1.draft_token)

    assert res2.saved is True
    saved = repo.get(res2.review_id)
    assert saved is not None
    assert saved.text == "ok man"
    assert saved.corrected_text == "now with enough details"
    assert saved.sentiment == "positive"
    assert saved.polarity == 0.7



def test_list_my_reviews_returns_saved_reviews():
    repo = FakeReviewRepository()

    r1 = repo.create_approved(
        user_id=7, text="orig1", corrected_text="corr1",
        sentiment="pos", polarity=0.9, suggestion=None
    )
    r2 = repo.create_approved(
        user_id=7, text="orig2", corrected_text="corr2",
        sentiment="neu", polarity=0.0, suggestion=None
    )

    uc = ListMyReviews(reviews=repo)
    items = uc.execute(user_id=7)
    assert [r.id for r in items] == [r1.id, r2.id]

import pytest
from sqlmodel import Session
from app.models.review import Review
from app.services import review_service
from datetime import datetime, timezone, timedelta


def test_filter_by_sentiment(session: Session, reviews_data, user_factory):
    user = user_factory(email="mockuser@example.com")
    for review in reviews_data:
        review_service.create_review(session, review, user)

    positives = review_service.get_reviews(session, sentiment="positive")
    assert len(positives) == 1
    assert positives[0].sentiment == "positive"

    negatives = review_service.get_reviews(session, sentiment="negative")
    assert len(negatives) == 1
    assert negatives[0].sentiment == "negative"

def test_filter_by_status(session: Session, reviews_data, user_factory):
    user = user_factory(email="mockuser@example.com")
    for review in reviews_data:
        review_service.create_review(session, review, user)

    accepted = review_service.get_reviews(session, status="Accepted")
    assert len(accepted) == 2
    for r in accepted:
        assert r.status == "Accepted"

    rejected = review_service.get_reviews(session, status="Rejected")
    assert len(rejected) == 1
    assert rejected[0].status == "Rejected"

def test_filter_by_created_at(session: Session, user_factory):
    now = datetime.now(timezone.utc)
    user = user_factory(email="mockuser@example.com")

    older_review = Review(
        text="Old review",
        sentiment="neutral",
        status="Accepted",
        feedback="Old feedback",
        created_at=now - timedelta(days=5),
        user_id=user.id
    )
    recent_review = Review(
        text="Recent review",
        sentiment="positive",
        status="Accepted",
        feedback="Recent feedback",
        created_at=now - timedelta(days=1),
        user_id=user.id
    )
    newest_review = Review(
        text="Newest review",
        sentiment="positive",
        status="Accepted",
        feedback="Newest feedback",
        created_at=now,
        user_id=user.id
    )

    session.add_all([older_review, recent_review, newest_review])
    session.commit()

    date_from = now - timedelta(days=2)
    reviews = review_service.get_reviews(session, date_from=date_from)
    assert len(reviews) == 2
    for r in reviews:
        if r.created_at.tzinfo is None:
            r_dt = r.created_at.replace(tzinfo=timezone.utc)
        else:
            r_dt = r.created_at

        assert r_dt >= date_from

    date_to = now - timedelta(days=2)
    reviews = review_service.get_reviews(session, date_to=date_to)
    assert len(reviews) == 1
    assert reviews[0].text == "Old review"

    reviews = review_service.get_reviews(
        session,
        date_from=now - timedelta(days=4),
        date_to=now - timedelta(days=2),
    )
    assert reviews == []

def test_list_reviews_returns_all(session: Session, sample_review: Review, user_factory):
    user = user_factory(email="mockuser@example.com")
    review_service.create_review(session, sample_review, user)
    reviews = review_service.get_reviews(session)
    assert len(reviews) == 1
    assert reviews[0].text == sample_review.text

def test_create_review_inserts_to_db(session: Session, sample_review: Review, user_factory):
    user = user_factory(email="mockuser@example.com")
    created = review_service.create_review(session, sample_review, user)
    assert created.id is not None
    assert created.text == "This product is excellent"

def test_remove_review(session: Session, sample_review: Review, user_factory):
    user = user_factory(email="mockuser@example.com")
    created = review_service.create_review(session, sample_review, user)
    review_service.delete_review(session, created.id)
    assert review_service.get_reviews(session) == []
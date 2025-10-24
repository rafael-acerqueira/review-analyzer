import pytest
from sqlmodel import SQLModel, create_engine, Session
from app.infra.db.reviews_repository import SqlModelReviewRepository
from typing import Dict


@pytest.fixture(scope="function")
def engine():
    eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(eng)
    return eng


@pytest.fixture(scope="function")
def session(engine):
    with Session(engine) as s:
        yield s


@pytest.fixture(scope="function")
def repo(session):
    return SqlModelReviewRepository(session)


def test_create_approved_and_get(repo):
    user_id = 101

    ent = repo.create_approved(
        user_id=user_id,
        text="original text",
        corrected_text="corrected text",
        sentiment="positive",
        status="approved",
        suggestion="looks good",
        feedback="ok man",
    )

    assert ent.id is not None
    loaded = repo.get(ent.id)
    assert loaded is not None
    assert loaded.user_id == user_id
    assert loaded.text == "original text"
    assert loaded.corrected_text == "corrected text"
    assert loaded.sentiment == "positive"
    assert loaded.status == "approved"


def test_list_by_user(repo):
    r1 = repo.create_approved(
        user_id=7, text="o1", corrected_text="c1",
        sentiment="pos", status="approved", suggestion="s1", feedback="f1",
    )
    r2 = repo.create_approved(
        user_id=7, text="o2", corrected_text="c2",
        sentiment="neu", status="approved", suggestion="s2", feedback="f2",
    )
    _r3 = repo.create_approved(
        user_id=8, text="o3", corrected_text="c3",
        sentiment="neg", status="approved", suggestion="s3", feedback="f3",
    )
    items = repo.list_by_user(user_id=7)
    ids = sorted([i.id for i in items])
    assert ids == sorted([r1.id, r2.id])


def test_delete(repo):
    item = repo.create_approved(
        user_id=11, text="o", corrected_text="c",
        sentiment="pos", status="approved", suggestion="s", feedback="f",
    )
    ok = repo.delete(item.id)
    assert ok is True
    assert repo.get(item.id) is None
    assert repo.delete(999999) is False


def test_stats_minimal(repo):
    repo.create_approved(
        user_id=1, text="o1", corrected_text="c1",
        sentiment="pos", status="approved", suggestion="s1", feedback="f1",
    )
    repo.create_approved(
        user_id=1, text="o2", corrected_text="c2",
        sentiment="neu", status="approved", suggestion="s2", feedback="f2",
    )
    repo.create_approved(
        user_id=2, text="o3", corrected_text="c3",
        sentiment="pos", status="approved", suggestion="s3", feedback="f3",
    )
    agg = repo.stats()
    assert isinstance(agg, dict)
    assert "total" in agg
    assert agg["total"] >= 3

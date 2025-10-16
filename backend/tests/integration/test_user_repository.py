import pytest
from sqlmodel import SQLModel, create_engine, Session
from app.infra.db.repositories import SqlModelUserRepository


@pytest.fixture(scope="module")
def engine():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    try:
        yield engine
    finally:
        engine.dispose()


@pytest.fixture
def session(engine):
    with Session(engine) as s:
        yield s
        s.rollback()


def test_create_local_and_get_by_email(session):
    repo = SqlModelUserRepository(session)

    user = repo.create_local(email="a@a.com", hashed_password="hash123")
    assert user.id is not None
    assert user.email == "a@a.com"
    assert user.hashed_password == "hash123"
    assert user.role in (None, "user")

    fetched = repo.get_by_email("a@a.com")
    assert fetched is not None
    assert fetched.id == user.id
    assert fetched.email == "a@a.com"


def test_exists_email_true_false(session):
    repo = SqlModelUserRepository(session)
    assert repo.exists_email("x@x.com") is False
    repo.create_local(email="x@x.com", hashed_password="h")
    assert repo.exists_email("x@x.com") is True


def test_upsert_google_user_create_and_update(session):
    repo = SqlModelUserRepository(session)

    u1 = repo.upsert_google_user(email="g@a.com", sub="sub-1")
    assert u1.id is not None
    assert u1.email == "g@a.com"
    assert u1.provider == "google"
    assert u1.sub == "sub-1"

    u2 = repo.upsert_google_user(email="g@a.com", sub="sub-2")
    assert u2.id == u1.id
    assert u2.sub == "sub-2"
    assert u2.provider == "google"


def test_update_google_sub_if_needed(session):
    repo = SqlModelUserRepository(session)

    created = repo.create_local(email="b@b.com", hashed_password="h")
    ent = repo.update_google_sub_if_needed(user_id=created.id, sub="sub-xyz")
    assert ent is not None
    assert ent.sub == "sub-xyz"

    ent2 = repo.update_google_sub_if_needed(user_id=created.id, sub="sub-xyz")
    assert ent2 is not None
    assert ent2.sub == "sub-xyz"

    assert repo.update_google_sub_if_needed(user_id=9999, sub="noop") is None

import pytest
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from starlette.testclient import TestClient

from app.dependencies import get_current_user
from app.database import get_session
from app.domain.reviews.use_cases import SaveApprovedReview, ListMyReviews, EvaluateText
from app.infra.db.admin_repository import SqlModelAdminRepository
from app.infra.db.reviews_repository import SqlModelReviewRepository
from app.models.review import Review
from app.models.user import User
from app.main import app

from app.api.v1.deps import (
    get_list_my_reviews_uc,
    get_save_approved_uc,
    get_evaluate_text_uc, get_doc_embedder,
    get_admin_repo,
    get_admin_list_uc,
    get_admin_delete_uc,
    get_admin_stats_uc,
)

from app.domain.admin.use_cases import (
    ListReviews as AdminListReviews,
    DeleteReview as AdminDeleteReview,
    GetStats as AdminGetStats
)

from sqlmodel import create_engine, SQLModel, Session, select

from app.security import create_access_token

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/review_analyzer_test"

engine = create_engine(DATABASE_URL, echo=False, future=True)

@pytest.fixture(scope="session", autouse=True)
def _create_schema_once():
    with engine.begin() as conn:
         conn.exec_driver_sql("CREATE EXTENSION IF NOT EXISTS vector;")
         SQLModel.metadata.create_all(bind=conn)
    yield

    with engine.begin() as conn:
        SQLModel.metadata.drop_all(bind=conn)

@pytest.fixture
def client(session):
    def override_get_session():
        yield session
    app.dependency_overrides[get_session] = override_get_session

    def override_get_save_approved_uc():
        repo = SqlModelReviewRepository(session)
        embedder = FakeDocEmbedder()
        return SaveApprovedReview(repo=repo, embedder=embedder)

    app.dependency_overrides[get_save_approved_uc] = override_get_save_approved_uc

    def override_get_list_my_reviews_uc():
        repo = SqlModelReviewRepository(session)
        return ListMyReviews(repo)
    app.dependency_overrides[get_list_my_reviews_uc] = override_get_list_my_reviews_uc

    def override_get_evaluate_text_uc():
        class _DummySentiment:
            def analyze(self, text: str):
                return "POSITIVE", 0.9
        class _DummySuggest:
            def evaluate(self, *, text: str):
                return {"status": "approved", "suggestion": "", "feedback": "ok"}
        return EvaluateText(sentiment=_DummySentiment(), sugg=_DummySuggest(), min_length=1)
    app.dependency_overrides[get_evaluate_text_uc] = override_get_evaluate_text_uc

    def override_get_admin_repo():
        return SqlModelAdminRepository(session)

    app.dependency_overrides[override_get_admin_repo] = override_get_admin_repo

    def override_get_admin_list_uc():
        return AdminListReviews(repo=SqlModelAdminRepository(session))

    app.dependency_overrides[override_get_admin_list_uc] = override_get_admin_list_uc

    def override_get_admin_delete_uc():
        return AdminDeleteReview(repo=SqlModelAdminRepository(session))

    app.dependency_overrides[override_get_admin_delete_uc] = override_get_admin_delete_uc

    def override_get_admin_stats_uc():
        return AdminGetStats(repo=SqlModelAdminRepository(session))

    app.dependency_overrides[override_get_admin_stats_uc] = override_get_admin_stats_uc

    app.dependency_overrides[get_admin_repo] = lambda: SqlModelAdminRepository(session)
    app.dependency_overrides[get_admin_list_uc] = lambda: AdminListReviews(repo=SqlModelAdminRepository(session))
    app.dependency_overrides[get_admin_delete_uc] = lambda: AdminDeleteReview(repo=SqlModelAdminRepository(session))
    app.dependency_overrides[get_admin_stats_uc] = lambda: AdminGetStats(repo=SqlModelAdminRepository(session))

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture
def session():
    connection = engine.connect()
    tx = connection.begin()

    TestingSessionLocal = sessionmaker(bind=connection, class_=Session, expire_on_commit=False)
    db = TestingSessionLocal()

    @event.listens_for(db, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    db.begin_nested()

    try:
        yield db
    finally:
        db.close()
        tx.rollback()
        connection.close()

@pytest.fixture
def user_factory(session):
    def create_user(email="user@example.com", role="user"):
        user = session.exec(select(User).where(User.email == email)).first()
        if not user:
            user = User(
                email=email,
                hashed_password="fakehash",
                provider="credentials",
                role=role,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
        return user
    return create_user

@pytest.fixture
def mock_user(user_factory):
    user = user_factory(email="mockuser@example.com", role="user")
    app.dependency_overrides[get_current_user] = lambda: user
    yield user
    app.dependency_overrides.clear()

@pytest.fixture
def user_and_token(user_factory):
    def create(email="user@example.com", role="user"):
        user = user_factory(email=email, role=role)
        token = create_access_token({"sub": str(user.id)})
        return user, token
    return create

@pytest.fixture
def admin_user(user_factory):
    return user_factory(email="admin@example.com", role="admin")

@pytest.fixture
def mock_admin_user(admin_user):

    app.dependency_overrides[get_current_user] = lambda: admin_user
    yield admin_user
    app.dependency_overrides.clear()


@pytest.fixture
def sample_review():
    return Review(
        text="This product is excellent",
        corrected_text="This product is excellent",
        sentiment="positive",
        status="approved",
        feedback="Great detail!",
        suggestion=None
    )

@pytest.fixture
def reviews_data():
    return [
        Review(text="Amazing!", sentiment="positive", status="Accepted", feedback="Great!", suggestion=None),
        Review(text="Terrible!", sentiment="negative", status="Rejected", feedback="Needs more detail", suggestion="Include specific complaints."),
        Review(text="Just okay.", sentiment="neutral", status="Accepted", feedback="Be more specific.", suggestion="Add examples."),
    ]

class FakeDocEmbedder:
    def embed(self, text: str): return [0.1]*384

@pytest.fixture(autouse=True)
def mock_doc_embedder():
    app.dependency_overrides[get_doc_embedder] = lambda: FakeDocEmbedder()
    yield
    app.dependency_overrides.pop(get_doc_embedder, None)
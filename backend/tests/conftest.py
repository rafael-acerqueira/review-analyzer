import pytest
import tempfile
from fastapi.testclient import TestClient

from app.dependencies import get_current_user
from app.database import get_session
from app.models.review import Review
from app.models.user import User
from app.main import app

from sqlmodel import create_engine, SQLModel, Session

from app.security import create_access_token

temp_db = tempfile.NamedTemporaryFile(delete=False)
DATABASE_URL = f"sqlite:///{temp_db.name}"

@pytest.fixture
def client(session):
    def override_get_session():
        yield session
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

    SQLModel.metadata.drop_all(engine)

@pytest.fixture
def user_factory(session):
    def create_user(email="user@example.com", role="user"):
        user = User(
            email=email,
            hashed_password="fakehash",
            provider="credentials",
            role=role
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    return create_user

@pytest.fixture
def mock_user(user_factory):
    user = user_factory(email="mockuser@example.com")
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
def admin_user(session):

    user = User(id=1, email="admin@example.com", provider="credentials", role="admin", hashed_password="fake")
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@pytest.fixture
def mock_admin_user(admin_user):

    app.dependency_overrides[get_current_user] = lambda: admin_user
    yield admin_user
    app.dependency_overrides.clear()


@pytest.fixture
def sample_review():
    return Review(
        text="This product is excellent",
        sentiment="positive",
        status="Accepted",
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


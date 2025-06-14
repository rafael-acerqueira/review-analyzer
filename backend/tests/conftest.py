import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_current_user
from app.models.user import User
from app.main import app

from sqlmodel import create_engine, SQLModel, Session

DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="module")
def client():
    return TestClient(app)

@pytest.fixture(name="session")
def session_fixture():
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session

@pytest.fixture
def mock_user():
    app.dependency_overrides[get_current_user] = lambda: User(id=1, email="user@example.com", role="user")
    yield
    app.dependency_overrides.clear()
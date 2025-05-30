import pytest
from fastapi.testclient import TestClient
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
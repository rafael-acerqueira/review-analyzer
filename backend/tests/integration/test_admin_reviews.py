from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.dependencies import get_current_user

client = TestClient(app)


def mock_admin_user():
    return User(id=1, email="admin@example.com", role="admin")

def test_admin_reviews_requires_auth():

    app.dependency_overrides = {}
    response = client.get("/api/v1/admin/reviews")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

def test_admin_reviews_rejects_non_admin(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    response = client.get("/api/v1/admin/reviews")
    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized"
    app.dependency_overrides.clear()

def test_admin_reviews_with_valid_admin_user(mock_admin_user):
    response = client.get("/api/v1/admin/reviews")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_delete_review(client, mock_admin_user):
    payload = {
        "text": "Product was great!",
        "sentiment": "positive",
        "status": "Accepted",
        "feedback": "Nice",
        "suggestion": ""
    }
    create_resp = client.post("/api/v1/reviews", json=payload)
    assert create_resp.status_code == 201
    review_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/admin/reviews/{review_id}")
    assert delete_resp.status_code == 200
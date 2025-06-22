from fastapi.testclient import TestClient
from app.main import app
from app.models.user import User
from app.models.review import Review
from app.dependencies import get_current_user
from datetime import datetime, timedelta, timezone


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

def test_stats_requires_admin_auth():
    resp = client.get("/api/v1/admin/stats")
    assert resp.status_code == 401

def test_stats_rejects_non_admin(mock_user):
    app.dependency_overrides[get_current_user] = lambda: mock_user
    resp = client.get("/api/v1/admin/stats")
    assert resp.status_code == 403
    assert resp.json()["detail"] == "Not authorized"
    app.dependency_overrides.clear()

def test_stats_returns_expected_fields(client, session, user_and_token, mock_admin_user):
    user1, token1 = user_and_token("user1@example.com")
    user2, token2 = user_and_token("user2@example.com")
    now = datetime.now(timezone.utc)
    old = now - timedelta(days=20)


    review1 = Review(text="A", sentiment="positive", status="Accepted", feedback="ok", user_id=user1.id,
                  created_at=now)

    review2 = Review(text="B", sentiment="negative", status="Rejected", feedback="too short",
                  user_id=user1.id, created_at=now)

    review3 = Review(text="C", sentiment="positive", status="Accepted", feedback="good", user_id=user2.id,
                  created_at=old)

    session.add_all([review1, review2, review3])
    session.commit()

    client.app.dependency_overrides[get_current_user] = lambda: mock_admin_user

    resp = client.get("/api/v1/admin/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert "by_sentiment" in data
    assert "by_status" in data
    assert "total_reviews" in data
    assert "period" in data
    assert "percent_accepted" in data
    assert "percent_rejected" in data
    assert "top_rejection_reasons" in data

    assert data["total_reviews"] >= 1

    resp2 = client.get("/api/v1/admin/stats", params={
        "user_id": user1.id,
        "from_date": "2000-01-01",
        "to_date": "2100-01-01"
    })
    data2 = resp2.json()
    assert data2["total_reviews"] == 2


    from_date = (now - timedelta(days=2)).date()
    to_date = now.date()
    resp3 = client.get(f"/api/v1/admin/stats?from_date={from_date}&to_date={to_date}")
    data3 = resp3.json()
    assert data3["total_reviews"] == 2

    client.app.dependency_overrides.clear()

def test_stats_no_reviews(client, session, mock_admin_user):
    client.app.dependency_overrides["get_current_user"] = lambda: mock_admin_user
    resp = client.get("/api/v1/admin/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_reviews"] == 0
    client.app.dependency_overrides.clear()
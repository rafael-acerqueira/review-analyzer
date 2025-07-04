from app.dependencies import get_current_user
from app.models.review import Review
from app.models.user import User
from app.main import app

def test_post_reviews_200(client, mock_user):
    payload = {
        "text": "The charger was missing and the screen cracked. I want a refund."
    }
    response = client.post("api/v1/analyze_review", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["Accepted", "Rejected"]
    assert "feedback" in data
    assert "suggestion" in data
    assert "sentiment" in data
    assert 0.0 <= data["polarity"] <= 1.0

def test_create_review_route(client, mock_user):
    payload = {
        "text": "The camera exceeded my expectations, with excellent battery life and image quality.",
        "sentiment": "positive",
        "status": "Accepted",
        "feedback": "Good details",
        "suggestion": ""
    }

    response = client.post("/api/v1/reviews", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == mock_user.id
    assert data["id"] > 0
    assert data["text"] == "The camera exceeded my expectations, with excellent battery life and image quality."

def test_authenticated_user_sees_only_their_reviews(client, user_and_token, session):

    user1, token1 = user_and_token("user1@example.com")
    user2, token2 = user_and_token("user2@example.com")

    review1 = Review(text="review user1", sentiment="POS", status="approved", feedback="", user_id=user1.id)
    review2 = Review(text="review user2", sentiment="NEG", status="approved", feedback="", user_id=user2.id)
    session.add_all([review1, review2])
    session.commit()


    response = client.get(
        "/api/v1/my-reviews",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == user1.id
    assert data[0]["text"] == "review user1"


    response = client.get(
        "/api/v1/my-reviews",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == user2.id
    assert data[0]["text"] == "review user2"

def mock_admin_user():
    return User(id=1, email="admin@example.com", role="admin")

def test_list_reviews_route(client):
    app.dependency_overrides[get_current_user] = mock_admin_user

    response = client.get("/api/v1/admin/reviews")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

    app.dependency_overrides.clear()

def test_remove_review_route(client):
    payload = {
        "text": "The delivery was fast and the packaging was perfect. I’m satisfied.",
        "sentiment": "neutral",
        "status": "Accepted",
        "feedback": "OK",
        "suggestion": ""
    }
    app.dependency_overrides[get_current_user] = mock_admin_user
    create_resp = client.post("/api/v1/reviews", json=payload)
    assert create_resp.status_code == 201
    review_id = create_resp.json()["id"]




    delete_resp = client.delete(f"/api/v1/admin/reviews/{review_id}")
    assert delete_resp.status_code == 200

    app.dependency_overrides.clear()
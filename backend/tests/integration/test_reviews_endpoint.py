

def test_post_reviews_200(client):
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

def test_create_review_route(client):
    payload = {
        "text": "The camera exceeded my expectations, with excellent battery life and image quality.",
        "sentiment": "positive",
        "status": "Accepted",
        "feedback": "Good details",
        "suggestion": ""
    }

    response = client.post("/api/v1/reviews", json=payload)
    assert response.status_code == 200
    data = response.json()
    print(data)
    assert data["id"] > 0
    assert data["text"] == "The camera exceeded my expectations, with excellent battery life and image quality."

def test_list_reviews_route(client):
    response = client.get("/api/v1/admin/reviews")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_remove_review_route(client):
    payload = {
        "text": "The delivery was fast and the packaging was perfect. I’m satisfied.",
        "sentiment": "neutral",
        "status": "Accepted",
        "feedback": "OK",
        "suggestion": ""
    }
    create_resp = client.post("/api/v1/reviews", json=payload)
    review_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/api/v1/admin/reviews/{review_id}")
    assert delete_resp.status_code == 200
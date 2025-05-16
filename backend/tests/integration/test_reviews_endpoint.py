def test_post_reviews_200(client):
    payload = {
        "text": "The charger was missing and the screen cracked. I want a refund."
    }
    response = client.post("api/v1/reviews", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["Accepted", "Rejected"]
    assert "feedback" in data
    assert "suggestion" in data
    assert "sentiment" in data
    assert 0.0 <= data["polarity"] <= 1.0
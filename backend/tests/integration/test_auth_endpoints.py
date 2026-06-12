def test_google_login_requires_internal_auth(client):
    payload = {"email": "google-user@example.com", "sub": "google-sub"}

    response = client.post("/api/v1/auth/google", json=payload)

    assert response.status_code == 403


def test_google_login_accepts_internal_auth_header(client, monkeypatch):
    from app import security
    from app.core.settings import get_settings

    monkeypatch.setenv("SECRET_KEY", "test-secret")
    get_settings.cache_clear()
    monkeypatch.setattr(security, "SECRET_KEY", "test-secret")

    payload = {"email": "google-user@example.com", "sub": "google-sub"}

    response = client.post(
        "/api/v1/auth/google",
        json=payload,
        headers={"X-Internal-Auth": "test-secret"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == payload["email"]
    assert data["access_token"]
    assert data["refresh_token"]
    get_settings.cache_clear()


def test_token_exchange_requires_internal_auth(client):
    payload = {"email": "google-user@example.com", "sub": "google-sub"}

    response = client.post("/api/v1/auth/token/exchange", json=payload)

    assert response.status_code == 403

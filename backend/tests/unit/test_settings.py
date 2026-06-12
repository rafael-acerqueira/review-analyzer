from app.core.settings import get_settings


def test_settings_loads_core_environment(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("INTERNAL_AUTH_SECRET", "internal-secret")
    monkeypatch.setenv("SQL_ECHO", "true")
    monkeypatch.setenv("CORS_ORIGINS", " http://localhost:3000, https://example.com ,, ")
    monkeypatch.setenv("PORT", "9999")
    monkeypatch.setenv("E2E_FAKE_ANALYSIS", "true")
    get_settings.cache_clear()

    settings = get_settings()

    assert settings.database_url == "sqlite:///:memory:"
    assert settings.secret_key == "test-secret"
    assert settings.internal_auth_secret == "internal-secret"
    assert settings.sql_echo is True
    assert settings.cors_origins == ["http://localhost:3000", "https://example.com"]
    assert settings.port == 9999
    assert settings.e2e_fake_analysis is True

    get_settings.cache_clear()

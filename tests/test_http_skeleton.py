import pytest
from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app


@pytest.fixture(autouse=True)
def basic_auth_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BASIC_AUTH_USERNAME", "test-user")
    monkeypatch.setenv("BASIC_AUTH_PASSWORD", "test-password")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


def test_openapi_is_available(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200


def test_create_url_requires_basic_auth(client: TestClient) -> None:
    response = client.post("/urls", json={"url": "https://example.com"})

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


def test_create_url_with_valid_basic_auth_reaches_placeholder(client: TestClient) -> None:
    response = client.post(
        "/urls",
        json={"url": "https://example.com"},
        auth=("test-user", "test-password"),
    )

    assert response.status_code == 501
    assert "not implemented yet" in response.json()["detail"]


def test_resolve_short_code_is_public_placeholder(client: TestClient) -> None:
    response = client.get("/abc123")

    assert response.status_code == 501
    assert response.json()["detail"] == {
        "message": "Short URL resolution is not implemented yet.",
        "short_code": "abc123",
    }
    assert "www-authenticate" not in response.headers

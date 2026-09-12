from collections.abc import AsyncIterator

import httpx
import pytest

from app.api.dependencies import get_url_shortener_service
from app.core.config import get_settings
from app.helpers.base62 import encode_base62
from app.helpers.obfuscation import obfuscate_base62
from app.infrastructure.cassandra_url_store import CassandraUrlStoreError
from app.infrastructure.redis_id_generator import RedisIdGenerationError
from app.main import app
from app.services.url_service import UrlShortenerService


TEST_USERNAME = "test-user"
TEST_PASSWORD = "test-password"
TEST_SHORT_URL_BASE = "https://sho.rt"
TEST_OBFUSCATING_KEY = "test-http-obfuscating-key"
URL_ID_START = 62**4

pytestmark = pytest.mark.anyio


class FakeIdGenerator:
    def __init__(self, generated_id: int = URL_ID_START) -> None:
        self.generated_id = generated_id
        self.calls = 0

    def generate_id(self) -> int:
        self.calls += 1
        return self.generated_id


class FailingIdGenerator:
    def generate_id(self) -> int:
        raise RedisIdGenerationError("Redis is unavailable.")


class FakeUrlStore:
    def __init__(self, stored_urls: dict[int, str] | None = None) -> None:
        self.stored_urls = stored_urls or {}
        self.saved: list[tuple[int, str]] = []
        self.lookups: list[int] = []

    def store_url(self, url_id: int, original_url: str) -> None:
        self.saved.append((url_id, original_url))
        self.stored_urls[url_id] = original_url

    def get_url(self, url_id: int) -> str | None:
        self.lookups.append(url_id)
        return self.stored_urls.get(url_id)


class FailingUrlStore(FakeUrlStore):
    def get_url(self, url_id: int) -> str | None:
        raise CassandraUrlStoreError("Cassandra is unavailable.")


@pytest.fixture(autouse=True)
def test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("BASIC_AUTH_USERNAME", TEST_USERNAME)
    monkeypatch.setenv("BASIC_AUTH_PASSWORD", TEST_PASSWORD)
    monkeypatch.setenv("SHORT_URL_BASE", TEST_SHORT_URL_BASE)
    monkeypatch.setenv("OBFUSCATING_KEY", TEST_OBFUSCATING_KEY)
    get_settings.cache_clear()

    yield

    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def client() -> AsyncIterator[httpx.AsyncClient]:
    override_service(FakeIdGenerator(), FakeUrlStore())
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://testserver",
    ) as async_client:
        yield async_client


def override_service(
    id_generator: FakeIdGenerator | FailingIdGenerator,
    url_store: FakeUrlStore,
) -> UrlShortenerService:
    service = UrlShortenerService(
        id_generator=id_generator,
        url_store=url_store,
        settings=get_settings(),
    )
    app.dependency_overrides[get_url_shortener_service] = lambda: service
    return service


def auth() -> tuple[str, str]:
    return (TEST_USERNAME, TEST_PASSWORD)


def short_code_for(url_id: int) -> str:
    return obfuscate_base62(encode_base62(url_id))


async def test_openapi_is_available_and_marks_only_post_as_authenticated(
    client: httpx.AsyncClient,
) -> None:
    response = await client.get("/openapi.json")

    assert response.status_code == 200
    paths = response.json()["paths"]
    assert paths["/urls"]["post"].get("security")
    assert not paths["/{short_code}"]["get"].get("security")


async def test_create_url_without_credentials_returns_basic_auth_challenge(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/urls",
        json={"url": "https://example.com/docs"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


async def test_create_url_with_incorrect_username_returns_basic_auth_challenge(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/urls",
        json={"url": "https://example.com/docs"},
        auth=("wrong-user", TEST_PASSWORD),
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


async def test_create_url_with_incorrect_password_returns_basic_auth_challenge(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/urls",
        json={"url": "https://example.com/docs"},
        auth=(TEST_USERNAME, "wrong-password"),
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"


async def test_create_url_rejects_missing_body(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post("/urls", auth=auth())

    assert response.status_code == 422


async def test_create_url_rejects_invalid_url(
    client: httpx.AsyncClient,
) -> None:
    response = await client.post(
        "/urls",
        json={"url": "not-a-url"},
        auth=auth(),
    )

    assert response.status_code == 422


async def test_create_url_with_valid_auth_generates_persists_and_returns_short_url(
    client: httpx.AsyncClient,
) -> None:
    id_generator = FakeIdGenerator()
    url_store = FakeUrlStore()
    override_service(id_generator, url_store)

    response = await client.post(
        "/urls",
        json={"url": "https://example.com/docs"},
        auth=auth(),
    )

    expected_short_code = short_code_for(URL_ID_START)
    assert response.status_code == 201
    assert response.json() == {
        "short_code": expected_short_code,
        "short_url": f"{TEST_SHORT_URL_BASE}/{expected_short_code}",
    }
    assert len(response.json()["short_code"]) == 7
    assert id_generator.calls == 1
    assert url_store.saved == [(URL_ID_START, "https://example.com/docs")]


async def test_create_url_returns_503_when_redis_id_generation_fails(
    client: httpx.AsyncClient,
) -> None:
    override_service(FailingIdGenerator(), FakeUrlStore())

    response = await client.post(
        "/urls",
        json={"url": "https://example.com/docs"},
        auth=auth(),
    )

    assert response.status_code == 503


async def test_resolve_short_code_is_public_and_redirects_without_auth(
    client: httpx.AsyncClient,
) -> None:
    short_code = short_code_for(URL_ID_START)
    url_store = FakeUrlStore(
        {URL_ID_START: "https://example.com/original"},
    )
    override_service(FakeIdGenerator(), url_store)

    response = await client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert response.status_code == 301
    assert response.headers["location"] == "https://example.com/original"
    assert "www-authenticate" not in response.headers
    assert url_store.lookups == [URL_ID_START]


async def test_resolve_unknown_short_code_returns_404_without_auth_challenge(
    client: httpx.AsyncClient,
) -> None:
    short_code = short_code_for(URL_ID_START)
    override_service(FakeIdGenerator(), FakeUrlStore())

    response = await client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert response.status_code == 404
    assert "www-authenticate" not in response.headers


async def test_resolve_malformed_short_code_returns_404_without_auth_challenge(
    client: httpx.AsyncClient,
) -> None:
    override_service(FakeIdGenerator(), FakeUrlStore())

    response = await client.get(
        "/abc",
        follow_redirects=False,
    )

    assert response.status_code == 404
    assert "www-authenticate" not in response.headers


async def test_resolve_short_code_returns_503_for_cassandra_failures(
    client: httpx.AsyncClient,
) -> None:
    short_code = short_code_for(URL_ID_START)
    override_service(FakeIdGenerator(), FailingUrlStore())

    response = await client.get(
        f"/{short_code}",
        follow_redirects=False,
    )

    assert response.status_code == 503
    assert "www-authenticate" not in response.headers

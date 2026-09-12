import pytest

from app.core.config import get_settings
from app.helpers.base62 import encode_base62
from app.helpers.obfuscation import obfuscate_base62
from app.infrastructure.cassandra_url_store import CassandraUrlStoreError
from app.infrastructure.redis_id_generator import RedisIdGenerationError
from app.schemas import CreateUrlRequest
from app.services.url_service import (
    InvalidShortCode,
    ShortCodeNotFound,
    UrlShortenerInfrastructureError,
    UrlShortenerService,
)


URL_ID_START = 62**4


class FakeIdGenerator:
    def __init__(self, generated_id: int = URL_ID_START) -> None:
        self.generated_id = generated_id
        self.calls = 0

    def generate_id(self) -> int:
        self.calls += 1
        return self.generated_id


class FailingIdGenerator:
    def generate_id(self) -> int:
        raise RedisIdGenerationError("Redis failure.")


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
    def store_url(self, url_id: int, original_url: str) -> None:
        raise CassandraUrlStoreError("Cassandra write failure.")

    def get_url(self, url_id: int) -> str | None:
        raise CassandraUrlStoreError("Cassandra read failure.")


@pytest.fixture(autouse=True)
def service_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SHORT_URL_BASE", "https://sho.rt/")
    monkeypatch.setenv("OBFUSCATING_KEY", "test-service-obfuscating-key")
    get_settings.cache_clear()

    yield

    get_settings.cache_clear()


def make_service(
    id_generator: FakeIdGenerator | FailingIdGenerator,
    url_store: FakeUrlStore,
) -> UrlShortenerService:
    return UrlShortenerService(
        id_generator=id_generator,
        url_store=url_store,
        settings=get_settings(),
    )


def short_code_for(url_id: int) -> str:
    return obfuscate_base62(encode_base62(url_id))


def test_create_short_url_runs_the_expected_pipeline() -> None:
    id_generator = FakeIdGenerator()
    url_store = FakeUrlStore()
    service = make_service(id_generator, url_store)
    payload = CreateUrlRequest(url="https://example.com/docs")

    response = service.create_short_url(payload)

    expected_short_code = short_code_for(URL_ID_START)
    assert response.short_code == expected_short_code
    assert response.short_url == f"https://sho.rt/{expected_short_code}"
    assert id_generator.calls == 1
    assert url_store.saved == [(URL_ID_START, "https://example.com/docs")]


def test_resolve_short_url_reverses_code_and_reads_cassandra() -> None:
    short_code = short_code_for(URL_ID_START)
    url_store = FakeUrlStore(
        {URL_ID_START: "https://example.com/original"},
    )
    service = make_service(FakeIdGenerator(), url_store)

    resolved = service.resolve_short_url(short_code)

    assert resolved == "https://example.com/original"
    assert url_store.lookups == [URL_ID_START]


def test_resolve_short_url_raises_not_found_for_missing_id() -> None:
    service = make_service(FakeIdGenerator(), FakeUrlStore())

    with pytest.raises(ShortCodeNotFound):
        service.resolve_short_url(short_code_for(URL_ID_START))


def test_resolve_short_url_raises_invalid_for_malformed_code() -> None:
    service = make_service(FakeIdGenerator(), FakeUrlStore())

    with pytest.raises(InvalidShortCode):
        service.resolve_short_url("abc")


def test_create_short_url_wraps_redis_failures() -> None:
    service = make_service(FailingIdGenerator(), FakeUrlStore())
    payload = CreateUrlRequest(url="https://example.com/docs")

    with pytest.raises(UrlShortenerInfrastructureError):
        service.create_short_url(payload)


def test_create_short_url_wraps_cassandra_failures() -> None:
    service = make_service(FakeIdGenerator(), FailingUrlStore())
    payload = CreateUrlRequest(url="https://example.com/docs")

    with pytest.raises(UrlShortenerInfrastructureError):
        service.create_short_url(payload)


def test_resolve_short_url_wraps_cassandra_failures() -> None:
    service = make_service(FakeIdGenerator(), FailingUrlStore())

    with pytest.raises(UrlShortenerInfrastructureError):
        service.resolve_short_url(short_code_for(URL_ID_START))

from dataclasses import dataclass
from typing import Any

from app.infrastructure.cassandra_url_store import (
    URL_TABLE_NAME,
    CassandraUrlStore,
)


@dataclass(frozen=True)
class Row:
    original_url: str


class FakeResult:
    def __init__(self, row: Row | None = None) -> None:
        self._row = row

    def one(self) -> Row | None:
        return self._row


class FakeSession:
    def __init__(self) -> None:
        self.urls: dict[int, str] = {}
        self.calls: list[tuple[str, tuple[Any, ...] | None]] = []

    def execute(
        self,
        query: str,
        parameters: tuple[Any, ...] | None = None,
    ) -> FakeResult:
        normalized_query = " ".join(query.split()).lower()
        self.calls.append((normalized_query, parameters))

        if normalized_query.startswith("insert"):
            assert parameters is not None
            url_id, original_url = parameters
            self.urls[int(url_id)] = str(original_url)
            return FakeResult()

        if normalized_query.startswith("select"):
            assert parameters is not None
            original_url = self.urls.get(int(parameters[0]))
            if original_url is None:
                return FakeResult()
            return FakeResult(Row(original_url=original_url))

        return FakeResult()


def test_initialize_schema_creates_the_id_lookup_table() -> None:
    session = FakeSession()
    store = CassandraUrlStore(session)

    store.initialize_schema()

    query, parameters = session.calls[0]
    assert parameters is None
    assert f"create table if not exists {URL_TABLE_NAME}" in query
    assert "id bigint primary key" in query
    assert "original_url text" in query


def test_store_url_persists_id_to_original_url() -> None:
    session = FakeSession()
    store = CassandraUrlStore(session)

    store.store_url(14_776_336, "https://example.com/docs")

    assert session.urls == {
        14_776_336: "https://example.com/docs",
    }


def test_get_url_retrieves_original_url_by_id() -> None:
    session = FakeSession()
    session.urls[14_776_336] = "https://example.com/docs"
    store = CassandraUrlStore(session)

    original_url = store.get_url(14_776_336)

    assert original_url == "https://example.com/docs"


def test_get_url_returns_none_for_missing_id() -> None:
    session = FakeSession()
    store = CassandraUrlStore(session)

    original_url = store.get_url(14_776_336)

    assert original_url is None

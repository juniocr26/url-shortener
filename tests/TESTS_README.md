# Project Tests

This directory contains the automated test suite for the implemented URL shortener backend.

The suite is written with `pytest` and is intended to run inside the Docker application container.

## Running All Tests

Run the complete suite:

```bash
docker compose exec app uv run pytest
```

Verbose mode:

```bash
docker compose exec app uv run pytest -v
```

Stop on first failure:

```bash
docker compose exec app uv run pytest -x
```

## Running Individual Test Files

HTTP/API tests:

```bash
docker compose exec app uv run pytest tests/test_http.py
```

Service tests:

```bash
docker compose exec app uv run pytest tests/test_url_service.py
```

Redis ID generator tests:

```bash
docker compose exec app uv run pytest tests/test_redis_id_generator.py
```

Cassandra URL store tests:

```bash
docker compose exec app uv run pytest tests/test_cassandra_url_store.py
```

Base62 tests:

```bash
docker compose exec app uv run pytest tests/test_base62.py
```

Obfuscation tests:

```bash
docker compose exec app uv run pytest tests/test_obfuscation.py
```

Run a specific test:

```bash
docker compose exec app uv run pytest tests/test_http.py::test_resolve_short_code_is_public_and_redirects_without_auth -v
```

## Test Directory Structure

```text
tests/
├── TESTS_README.md
├── TESTS_README.pt-BR.md
├── test_base62.py
├── test_cassandra_url_store.py
├── test_http.py
├── test_obfuscation.py
├── test_redis_id_generator.py
└── test_url_service.py
```

## Coverage

Current coverage includes:

- OpenAPI availability.
- `POST /urls` Basic Authentication requirement.
- `POST /urls` rejection without credentials.
- `POST /urls` rejection with incorrect username.
- `POST /urls` rejection with incorrect password.
- `POST /urls` request validation for missing body and invalid URL.
- Successful URL creation response contract.
- Redis ID generation invocation through the service flow.
- Base62 encoding in the creation flow.
- Reversible obfuscation in the creation flow.
- Seven-character public short codes.
- `SHORT_URL_BASE` usage.
- Cassandra persistence call with the expected ID and original URL.
- Public `GET /{short_code}` without an `Authorization` header.
- `301 Moved Permanently` redirect behavior.
- Redirect `Location` header validation.
- Absence of `WWW-Authenticate` on successful public GET.
- Unknown and malformed short-code handling.
- Redis and Cassandra failure mapping to service/HTTP errors.
- Base62 encode/decode examples and round trips.
- Obfuscation/deobfuscation round trips.
- Redis counter initialization, non-overwrite behavior, sequential increments, and `INCR` usage.
- Cassandra URL store behavior for storing, retrieving, and missing IDs.

## Unit, API, and Integration Distinction

The default suite is a unit/API suite:

- HTTP tests use `httpx.AsyncClient` with ASGI transport.
- Service tests use fake Redis ID generators and fake Cassandra stores.
- Redis tests use a fake Redis client to validate counter semantics.
- Cassandra tests use a fake Cassandra session to validate the store contract.
- Base62 and obfuscation tests are pure helper tests.

The default suite does not require live Redis or live Cassandra for every run. It should not be described as a full Cassandra or Redis integration test suite.

Docker Compose validation and manual checks are used for local infrastructure confidence:

```bash
docker compose config
docker compose up -d
docker compose ps
```

## Test Environment Variables

Tests use `monkeypatch` to provide isolated values such as:

- `BASIC_AUTH_USERNAME`
- `BASIC_AUTH_PASSWORD`
- `SHORT_URL_BASE`
- `OBFUSCATING_KEY`

These are test-only values. The suite does not use or expose real local `.env` secrets.

The expected Base62 alphabet is:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

## Planned Coverage

Additional coverage that would be useful but is not part of the current default suite:

- live Redis integration tests against the Docker Redis service;
- live Cassandra integration tests against the Docker Cassandra cluster;
- end-to-end HTTP tests through the running Uvicorn container;
- failure-mode tests for Docker service restarts.

Those items should only be documented as implemented after corresponding tests are added.

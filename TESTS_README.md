# Project Tests

This project includes automated tests focused on the current backend foundation, HTTP contract, Base62 encoding/decoding, and reversible short-code obfuscation used by the URL shortener.

The test suite is written with `pytest` and runs inside the Docker development environment.

## Running All Tests

To run the complete test suite inside the application container:

```bash
docker compose exec app uv run pytest
```

For more detailed output:

```bash
docker compose exec app uv run pytest -v
```

To stop execution after the first failure:

```bash
docker compose exec app uv run pytest -x
```

## HTTP Tests

The HTTP tests validate the current FastAPI HTTP contract and authentication behavior.

Run only the HTTP test suite:

```bash
docker compose exec app uv run pytest tests/test_http_skeleton.py
```

Current coverage includes:

- OpenAPI availability
- Basic Authentication requirement for `POST /urls`
- Access to the protected URL creation endpoint with valid credentials
- Public access to `GET /{short_code}`
- Permanent HTTP redirect behavior for short-code resolution
- `Location` header validation for HTTP redirects
- Verification that the public short-code route does not require Basic Authentication

The URL creation and short-code resolution business logic will evolve as Redis ID generation and Cassandra persistence are implemented.

## Base62 Tests

The Base62 tests validate the conversion between integer identifiers and Base62 values.

Run only the Base62 tests:

```bash
docker compose exec app uv run pytest tests/test_base62.py
```

Run the Base62 tests with verbose output:

```bash
docker compose exec app uv run pytest tests/test_base62.py -v
```

The application uses the following Base62 alphabet:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

The tests validate:

- Encoding known integer values into Base62
- Decoding known Base62 values into integers
- Encode/decode round trips
- Zero handling
- Negative integer rejection
- Empty value rejection
- Invalid Base62 character rejection

An important property validated by the suite is:

```text
decode_base62(encode_base62(value)) == value
```

For example:

```text
62^4 = 14,776,336

14,776,336
    ↓ encode
  10000
    ↓ decode
14,776,336
```

This round-trip behavior is important because the application will eventually use an integer identifier during URL creation and recover the same identifier from the short code during URL resolution.

## Obfuscation Tests

The obfuscation tests validate the reversible transformation applied to Base62 values before they are exposed as public short codes.

Run only the obfuscation tests:

```bash
docker compose exec app uv run pytest tests/test_obfuscation.py
```

Run the obfuscation tests with verbose output:

```bash
docker compose exec app uv run pytest tests/test_obfuscation.py -v
```

The obfuscation layer transforms a Base62 value into a fixed-length, seven-character Base62 short code.

The reverse operation restores the original Base62 value.

The expected flow is:

```text
Base62 value
    ↓
obfuscate_base62()
    ↓
7-character short code
    ↓
deobfuscate_base62()
    ↓
original Base62 value
```

An important property validated by the suite is:

```text
deobfuscate_base62(obfuscate_base62(value)) == value
```

The tests validate:

- Obfuscation/deobfuscation round trips
- Fixed seven-character output
- Deterministic output when using the same value and key
- Different outputs for different input values
- Different outputs when different obfuscation keys are used
- Behavior when attempting to restore a value with a different key
- Rejection of obfuscated values shorter than seven characters
- Rejection of obfuscated values longer than seven characters
- Rejection of values outside the supported seven-character Base62 space

The obfuscation tests use a temporary test value for `OBFUSCATING_KEY`.

The test key is provided through Pytest's `monkeypatch` and does not depend on the real key configured in the project's local `.env`.

The obfuscation mechanism is intended to hide sequential identifiers before exposing them as public short codes. It should not be treated as a replacement for cryptographic encryption when cryptographic confidentiality is required.

## Running a Specific Test

Pytest allows individual tests to be executed directly.

For example, to run only the Base62 round-trip test:

```bash
docker compose exec app uv run pytest tests/test_base62.py::test_base62_round_trip -v
```

To run only the obfuscation round-trip test:

```bash
docker compose exec app uv run pytest tests/test_obfuscation.py::test_obfuscation_round_trip -v
```

To run only the Basic Authentication requirement test:

```bash
docker compose exec app uv run pytest tests/test_http_skeleton.py::test_create_url_requires_basic_auth -v
```

To run only the short-code redirect test:

```bash
docker compose exec app uv run pytest tests/test_http_skeleton.py::test_resolve_short_code_is_public_and_redirects -v
```

This is useful when working on a specific behavior without running the entire suite.

## Test Structure

The current test structure is:

```text
tests/
├── TESTS_README.md
├── test_base62.py
├── test_http_skeleton.py
└── test_obfuscation.py
```

### `test_http_skeleton.py`

Tests the current FastAPI HTTP contract, Basic Authentication behavior, public short-code route, and permanent redirect response.

### `test_base62.py`

Tests the Base62 helper responsible for encoding integer identifiers and decoding Base62 values back into integers.

### `test_obfuscation.py`

Tests the reversible obfuscation helper responsible for transforming Base62 values into fixed-length public short codes and restoring the original Base62 values.

## Docker Environment

The project is designed to run through Docker.

Tests should therefore be executed from the application container whenever possible:

```bash
docker compose exec app uv run pytest
```

This ensures that the tests run with the same Python version, dependencies, and environment used by the application.

The host machine does not need to provide the project's Python runtime or dependencies directly.

## Environment Variables

Some tests temporarily override environment variables using Pytest's `monkeypatch`.

For example, the HTTP authentication tests provide temporary Basic Authentication credentials during execution.

The obfuscation tests provide a temporary `OBFUSCATING_KEY`.

These values exist only for the test process and do not replace the project's local `.env` configuration.

The Base62 helper uses the application's `BASE62_ALPHABET` configuration.

The expected alphabet is:

```text
0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz
```

The obfuscation helper uses:

```text
OBFUSCATING_KEY
```

The real obfuscation key must not be hardcoded in the test suite or committed to the repository.

## Current Test Coverage

The current test suite covers the implemented parts of the project:

- FastAPI application availability
- OpenAPI endpoint
- Basic Authentication behavior
- Protected `POST /urls` route behavior
- Public `GET /{short_code}` route behavior
- Permanent `301 Moved Permanently` redirect behavior
- Redirect `Location` header validation
- Base62 encoding
- Base62 decoding
- Base62 round-trip validation
- Base62 input validation
- Base62 value obfuscation
- Base62 value deobfuscation
- Obfuscation/deobfuscation round-trip validation
- Fixed seven-character obfuscated output
- Obfuscation key behavior
- Obfuscation input validation

## Planned Test Coverage

As the project evolves, additional tests are expected to cover:

- Redis atomic ID generation
- Redis counter initialization
- Cassandra persistence
- URL creation
- Complete short-code generation flow
- Short-code resolution backed by persisted data
- Redirect behavior using URLs retrieved from persistence
- Failure scenarios
- Infrastructure integration behavior

These items represent planned coverage and should only be moved to the current coverage section after the corresponding behavior has been implemented and tested.

## Notes

- Tests are executed with `pytest`.
- Python dependencies are managed with `uv`.
- Docker is the primary development environment.
- Base62 tests do not require Redis or Cassandra.
- Obfuscation tests do not require Redis or Cassandra.
- Test-specific secrets are provided through Pytest and must not use production or local development secrets.
- The current HTTP tests validate the route contract, authentication behavior, and redirect response, but do not yet validate the complete Redis and Cassandra-backed URL shortening flow.
- Redirect tests may use controlled test data until short-code resolution is connected to persistent storage.

# url-shortener

[English](guide.md) | [Português](../pt-BR/guide.md)

`url-shortener` is a Docker-first backend/system-design portfolio project that implements URL creation and public redirect resolution with FastAPI, Redis, Cassandra, Base62 encoding, and reversible short-code obfuscation.

The project is intentionally small enough to explain in an interview while still exercising real backend concerns: authenticated writes, public reads, atomic ID generation, persistent storage, containerized infrastructure, and automated tests.

## Technology Stack

- Python 3.14
- FastAPI and Uvicorn
- Redis 7 with AOF persistence
- Apache Cassandra 5.0, three local nodes, datacenter `datacenter1`
- Base62 encoding with `0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz`
- Reversible seven-character short-code obfuscation
- Pytest
- `uv`
- Docker and Docker Compose

## API

### `POST /urls`

Creates a shortened URL. This endpoint requires HTTP Basic Authentication using `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD`.

Request:

```json
{
  "url": "https://example.com/docs"
}
```

Successful response: `201 Created`

```json
{
  "short_code": "Ab3xZ90",
  "short_url": "http://localhost:8000/Ab3xZ90"
}
```

### `GET /{short_code}`

Resolves a public short code. This endpoint is intentionally public and does not require an `Authorization` header.

Successful response: `301 Moved Permanently`

```text
Location: https://example.com/docs
```

Unknown or malformed short codes return `404 Not Found`. Infrastructure failures return `503 Service Unavailable` without exposing internal hostnames, credentials, or stack traces.

OpenAPI remains available at:

```text
http://localhost:8000/docs
```

## Configuration

Copy the public environment contract and fill local secret values:

```sh
if [ ! -e .env ]; then cp .env.example .env; fi
```

The `.env` file is ignored by Git. Do not commit real Redis passwords, Cassandra passwords, Basic Auth passwords, or `OBFUSCATING_KEY` values.

Important variables:

- `SHORT_URL_BASE`: base URL used to build `short_url`.
- `URL_ID_START`: first generated ID target. The default is `14776336`, which is `62^4`.
- `BASIC_AUTH_USERNAME` / `BASIC_AUTH_PASSWORD`: required for `POST /urls`.
- `OBFUSCATING_KEY`: private key used by reversible short-code obfuscation.
- `REDIS_*`: Redis connection settings.
- `CASSANDRA_*`: Cassandra connection, keyspace, role, and datacenter settings.

Startup can create/alter Cassandra roles/keyspaces/tables. Do not run it against existing data during a preservation-only review. Use a verified disposable environment for writes. Compose reads `.env`, but host curl does not automatically inherit it: set Basic Auth variables locally in the shell without printing credentials. Replace the quoted short-code placeholder before running GET.

## Running Locally

Validate the Compose configuration:

```sh
docker compose config --quiet
```

Start the full environment:

```sh
docker compose up -d
```

Check service status:

```sh
docker compose ps
```

The API is published on:

```text
http://localhost:8000
```

Create a URL:

```sh
curl -i \
  -u "$BASIC_AUTH_USERNAME:$BASIC_AUTH_PASSWORD" \
  -X POST http://localhost:8000/urls \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://example.com/docs"}'
```

Resolve a URL without authentication:

```sh
curl -i --max-redirs 0 "http://localhost:8000/REPLACE_WITH_SHORT_CODE"
```

Stop containers without deleting Redis or Cassandra data:

```sh
docker compose stop
```


[Testing](testing.md) · [Architecture and trade-offs](architecture.md) · [Docker](docker.md) · [Postman](postman.md)

## Author

Júnio Rosa

[LinkedIn](https://www.linkedin.com/in/j%C3%BAnio-rosa-94b5731b2/)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

For safe host-persisted dependencies and configuration recovery, see [Docker development setup](docker-development-setup.md).

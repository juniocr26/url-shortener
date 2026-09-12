# url-shortener

`url-shortener` is a Docker-first backend/system-design portfolio project that implements URL creation and public redirect resolution with FastAPI, Redis, Cassandra, Base62 encoding, and reversible short-code obfuscation.

The project is intentionally small enough to explain in an interview while still exercising real backend concerns: authenticated writes, public reads, atomic ID generation, persistent storage, containerized infrastructure, and automated tests.

## Architecture

The application runs as a FastAPI service backed by Redis and a three-node Cassandra cluster.

```mermaid
flowchart LR
    client[Client]
    app[FastAPI app]
    redis[Redis<br/>atomic INCR + AOF]
    c1[cassandra-1<br/>seed, not leader]
    c2[cassandra-2]
    c3[cassandra-3]

    client -->|POST /urls<br/>Basic Auth| app
    client -->|GET /{short_code}<br/>public| app
    app --> redis
    app --> c1
    app --> c2
    app --> c3
    c1 --- c2
    c2 --- c3
    c1 --- c3
```

POST flow:

```text
POST /urls
  -> Basic Authentication
  -> URL validation
  -> Redis INCR
  -> integer ID
  -> Base62
  -> reversible obfuscation
  -> seven-character public code
  -> Cassandra persistence
  -> 201 Created
```

GET flow:

```text
GET /{short_code}
  -> public endpoint, no authentication
  -> deobfuscate code
  -> Base62 decode
  -> Cassandra lookup by integer ID
  -> 301 Moved Permanently
  -> Location: original URL
```

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
cp .env.example .env
```

The `.env` file is ignored by Git. Do not commit real Redis passwords, Cassandra passwords, Basic Auth passwords, or `OBFUSCATING_KEY` values.

Important variables:

- `SHORT_URL_BASE`: base URL used to build `short_url`.
- `URL_ID_START`: first generated ID target. The default is `14776336`, which is `62^4`.
- `BASIC_AUTH_USERNAME` / `BASIC_AUTH_PASSWORD`: required for `POST /urls`.
- `OBFUSCATING_KEY`: private key used by reversible short-code obfuscation.
- `REDIS_*`: Redis connection settings.
- `CASSANDRA_*`: Cassandra connection, keyspace, role, and datacenter settings.

## Running Locally

Validate the Compose configuration:

```sh
docker compose config
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
curl -i --max-redirs 0 http://localhost:8000/<short_code>
```

Stop containers without deleting Redis or Cassandra data:

```sh
docker compose down
```

## Tests

Run the complete test suite inside the application container:

```sh
docker compose exec app uv run pytest
```

Verbose mode:

```sh
docker compose exec app uv run pytest -v
```

Stop on first failure:

```sh
docker compose exec app uv run pytest -x
```

The default suite uses fakes for Redis and Cassandra API behavior. It does not require live Redis or Cassandra for every unit/API test. See [tests/TESTS_README.md](tests/TESTS_README.md) for the full test guide.

## Internal Documentation

- [Architecture](docs/en/architecture.md)
- [Docker development](docs/en/docker.md)
- [Test guide](tests/TESTS_README.md)
- [Arquitetura em português](docs/pt-BR/architecture.md)
- [Docker em português](docs/pt-BR/docker.md)
- [Guia de testes em português](tests/TESTS_README.pt-BR.md)

## Trade-offs

- Redis AOF improves local durability, but it is not a high-availability or failover mechanism.
- Redis is the source of atomic ID generation. If Redis loses acknowledged counter state while Cassandra keeps rows already written, ID reuse can become a correctness risk.
- Cassandra is peer-to-peer. The seed node helps bootstrap discovery; it is not a leader.
- Successful resolution uses `301 Moved Permanently`, which may be cached aggressively. Changing the destination of an existing short code is not reliably supported.
- The seven-character public code is reversible obfuscation, not strong encryption.
- URL creation is authenticated, while public URL resolution is deliberately unauthenticated.

## Author

Júnio Rosa

[LinkedIn](https://www.linkedin.com/in/j%C3%BAnio-rosa-94b5731b2/)

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

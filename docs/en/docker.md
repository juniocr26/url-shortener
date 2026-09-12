# Docker Development

## Philosophy

This project is Docker-first. The host machine should mainly provide:

- Git
- Docker
- Docker Compose

Python 3.14, `uv`, FastAPI, Redis, Cassandra, and project commands are expected to run inside containers whenever possible.

## Environment Files

`.env.example` is the public configuration contract. `.env` is local, private, ignored by Git, and consumed by Docker Compose.

Create a local file:

```sh
cp .env.example .env
```

Fill local values for:

- `BASIC_AUTH_USERNAME`
- `BASIC_AUTH_PASSWORD`
- `OBFUSCATING_KEY`
- `CASSANDRA_USERNAME`
- `CASSANDRA_PASSWORD`
- optional `REDIS_PASSWORD`

Do not commit `.env` or real secret values.

## Build and Start

Validate Compose interpolation and service definitions:

```sh
docker compose config
```

Build the application image:

```sh
docker compose build
```

Start the full stack:

```sh
docker compose up -d
```

The `app` service depends on:

- healthy Redis;
- completed Cassandra bootstrap.

Cassandra bootstrap waits for the three Cassandra nodes to become healthy, creates or updates the configured role and keyspace, and creates the `urls_by_id` table if it does not already exist.

Check service health:

```sh
docker compose ps
```

## Application

The application runs Uvicorn with reload enabled for local development. Source code is bind-mounted into `/app`.

Default URL:

```text
http://localhost:8000
```

OpenAPI:

```text
http://localhost:8000/docs
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

`GET /{short_code}` should not send or require Basic Auth.

## Tests

Run all tests inside the running application container:

```sh
docker compose exec app uv run pytest
```

Verbose output:

```sh
docker compose exec app uv run pytest -v
```

Stop on first failure:

```sh
docker compose exec app uv run pytest -x
```

Run an individual file:

```sh
docker compose exec app uv run pytest tests/test_http.py
```

The default test suite uses fakes for Redis and Cassandra behavior. It does not require live infrastructure for every test case.

## Redis

Redis uses:

- image: `redis:7-alpine`;
- data directory: `.dockerized-redis/`;
- AOF enabled;
- `appendfsync everysec`;
- optional password from `REDIS_PASSWORD`;
- host port `127.0.0.1:6379`.

Check Redis health:

```sh
docker compose exec redis sh -c 'if [ -n "$REDIS_PASSWORD" ]; then REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli ping; else redis-cli ping; fi'
```

Expected result:

```text
PONG
```

Redis generates URL IDs with atomic `INCR`. The application initializes the counter with `SET ... NX` so existing persisted counter state is not overwritten.

Redis AOF improves durability, but it is not failover or high availability.

## Cassandra

The local Cassandra cluster has three peer-to-peer nodes:

- `cassandra-1`
- `cassandra-2`
- `cassandra-3`

`cassandra-1` is the seed node for discovery. Seed does not mean leader.

Authentication uses Cassandra `PasswordAuthenticator`. The configured role, keyspace, and URL table are initialized idempotently by `cassandra-init`.

The keyspace uses `NetworkTopologyStrategy` with replication factor 3 in the configured datacenter, defaulting to `datacenter1`.

Only `cassandra-1` is published to the host:

```text
127.0.0.1:9042:9042
```

Check CQL readiness:

```sh
docker compose exec cassandra-1 bash /usr/local/bin/url-shortener-cassandra-healthcheck
```

Check cluster membership:

```sh
docker compose exec cassandra-1 nodetool status
```

Each node has its own ignored local data directory:

- `.dockerized-cassandra/cassandra-1/`
- `.dockerized-cassandra/cassandra-2/`
- `.dockerized-cassandra/cassandra-3/`

No Cassandra data directory is shared between nodes.

## Stop and Reset

Stop services without deleting data:

```sh
docker compose down
```

Delete containers and local Docker volumes:

```sh
docker compose down --volumes
```

The Redis and Cassandra bind-mounted data directories are not deleted by normal `docker compose down`. Delete them only when a local data reset is intentional.

# Docker Development

## Philosophy

This project uses a Docker-first development workflow. The host machine should mainly provide:

- Git
- Docker
- Docker Compose

Python 3.14, `uv`, FastAPI, Uvicorn, Redis, Cassandra, and project-specific commands should run inside containers whenever technically applicable.

This avoids making the host Python installation part of the operational requirements for the project.

## Environment Files

`.env.example` is the public configuration contract. `.env` is local, private, ignored by Git, and consumed by Docker Compose through environment interpolation.

Create a local `.env` from the public example:

```sh
cp .env.example .env
```

Do not commit `.env`, credentials, tokens, or private keys.

`POST /urls` requires `BASIC_AUTH_USERNAME` and `BASIC_AUTH_PASSWORD` in the local `.env`. Keep real values private and do not place them in documentation.

## Build

```sh
docker compose build
```

The application image uses a multi-stage Dockerfile:

- `uv` stage: provides the `uv` and `uvx` binaries.
- `build` stage: resolves and installs project dependencies into `/opt/venv`.
- `runtime` stage: contains Python, `uv`, the virtual environment, and project files, without build-only layers from the dependency stage.

Dependency files are copied before the rest of the project so normal code changes do not unnecessarily invalidate dependency layers.

## Start and Stop

Start all services:

```sh
docker compose up -d
```

Stop services without deleting data:

```sh
docker compose down
```

Delete containers and volumes:

```sh
docker compose down --volumes
```

The volume removal command deletes Redis and Cassandra local data. Use it only when resetting the local environment is intentional.

## Rebuild

Rebuild images and start the stack:

```sh
docker compose up -d --build
```

Rebuild the application image without cache:

```sh
docker compose build --no-cache app
```

## Application Container

The `app` service runs the FastAPI skeleton with Uvicorn. In Docker Compose it uses `--reload` for local development, with the source code mounted into the container.

The API is published to the host on `APP_PORT`, which defaults to `8000`:

```text
http://localhost:8000
```

Automatic OpenAPI documentation is available at:

```text
http://localhost:8000/docs
```

Run Python:

```sh
docker compose run --rm --no-deps app python --version
```

Run `uv`:

```sh
docker compose run --rm --no-deps app uv --version
```

Synchronize dependencies inside Docker:

```sh
docker compose run --rm --no-deps app uv sync --frozen
```

Run tests:

```sh
docker compose run --rm --no-deps app uv run pytest
```

Open a shell:

```sh
docker compose run --rm --no-deps app sh
```

If the stack is already running, you can also use:

```sh
docker compose exec app sh
```

Check the public route placeholder:

```sh
curl -i http://localhost:8000/abc123
```

Check unauthenticated `POST /urls`:

```sh
curl -i -X POST http://localhost:8000/urls -H 'Content-Type: application/json' -d '{"url":"https://example.com"}'
```

Check authenticated `POST /urls` with local private credentials:

```sh
curl -i -u "$BASIC_AUTH_USERNAME:$BASIC_AUTH_PASSWORD" -X POST http://localhost:8000/urls -H 'Content-Type: application/json' -d '{"url":"https://example.com"}'
```

## Logs and Health

Show container status and health:

```sh
docker compose ps
```

Follow all logs:

```sh
docker compose logs -f
```

Follow one service:

```sh
docker compose logs -f app
```

## Redis

Redis uses:

- image: `redis:7-alpine`
- data volume: `redis_data`
- AOF: enabled
- fsync policy: `everysec`

Check Redis health:

```sh
docker compose exec redis sh -c 'if [ -n "$REDIS_PASSWORD" ]; then REDISCLI_AUTH="$REDIS_PASSWORD" redis-cli ping; else redis-cli ping; fi'
```

Expected result:

```text
PONG
```

Redis is planned to generate IDs with `INCR url:id`, but this milestone does not initialize or mutate the counter.

## Cassandra

The local Cassandra cluster uses three peer-to-peer nodes:

- `cassandra-1`
- `cassandra-2`
- `cassandra-3`

`cassandra-1` is the seed node for topology discovery. Seed does not mean leader.

Check CQL readiness:

```sh
docker compose exec cassandra-1 cqlsh 127.0.0.1 9042 -e "DESCRIBE KEYSPACES;"
```

Check cluster membership:

```sh
docker compose exec cassandra-1 nodetool status
```

Each Cassandra node has its own volume:

- `cassandra_data_1`
- `cassandra_data_2`
- `cassandra_data_3`

The health check uses `cqlsh` against the local node. This verifies that CQL native transport is accepting requests, but a deeper topology check should still use `nodetool status`.

## Docker Network

All services join the same Compose bridge network and communicate through service names. No hardcoded container IPs are used.

The Compose file does not publish service ports to the host by default. Commands are executed through containers to preserve the Docker-first workflow.

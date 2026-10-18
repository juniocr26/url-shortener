# url-shortener

[English](README.md) | [Português brasileiro](README.pt-BR.md)

A FastAPI portfolio demonstrating authenticated URL creation and public permanent redirects. Redis allocates IDs; Cassandra stores mappings; Base62 and reversible obfuscation produce short codes. It explores system-design trade-offs without claiming measured production capacity.

## Documentation catalog and reading path

- [Complete categorized catalog](docs/en/index.md)
- [Review checklist and evidence gaps](docs/en/operations/completion-checklist.md)

Read purpose/setup first, then architecture and contracts, security and failures, tests/evidence, and local deployment/recovery. This is an independent portfolio project; runtime procedures in the documentation were not executed in the 2026-10-10 review.

## Documentation

- [Architecture](docs/en/architecture/overview.md)
- [Development dependencies and recovery](docs/en/docker/development.md)
- [Docker and configuration](docs/en/docker/runtime.md)
- [Project guide](docs/en/guides/project-guide.md)
- [Postman collection](docs/en/api/postman.md)
- [Testing](docs/en/testing/strategy.md)
- [Validation results](docs/en/testing/verification.md)

[License](LICENSE)

## Quick start and scope

For a fresh clone, install Docker/Compose, copy the example and privately configure Basic Auth, obfuscation and database credentials:

```sh
cp .env.example .env
# Configure private local credentials before starting.
docker compose build
docker compose up -d
```

API: http://localhost:8000. Startup includes three Cassandra nodes and role/schema bootstrap. POST /urls requires Basic Auth; GET /{short_code} is public. Coordinate counter and mapping recovery; there is no cross-store transaction.

For existing checkouts, update configuration deliberately instead of overwriting the local file.

[Installation, execution flow, operational limits and project interview](docs/en/guides/implementation-study.md). Commands are guidance; this documentation maintenance ran no application tests.

# Documentation validation — 2026-10-06

## Isolation before startup

No containers were running before this project. Base Compose/bootstrap and FastAPI lifespan were reviewed: they can alter roles/keyspaces/tables. Existing `.dockerized-redis` and `.dockerized-cassandra` were excluded from validation. A separate Compose project `portfolio-url-doc-validation` used the existing `compose.yaml` and `compose.development.yaml` plus a temporary safety override outside the repository.

Every Redis/Cassandra data target was replaced by a freshly created, verified empty directory under a task-specific `/private/tmp/portfolio-url-doc-*` root. App connections were forced to redis:6379 and cassandra-1/2/3:9042, with disposable fixture credentials and keyspace `documentation_isolated`. A dedicated internal backend network prevented external connections. Isolation was established from resolved Compose JSON before `up -d` and rechecked against actual container mounts/network before POST. This is storage/connection isolation, not merely a database named test. Existing environment files and persisted data were not changed.

## Commands and results

Commands used the following prefix, with `TEMP_OVERRIDE` pointing only to that verified temporary configuration:

```sh
docker compose -p portfolio-url-doc-validation -f compose.yaml -f compose.development.yaml -f "$TEMP_OVERRIDE"
```

| Command or check | Actual result |
| --- | --- |
| `config --format json` with assertions on mounts/connections/network | Passed before startup; no existing data target |
| `up -d` | Passed; app, Redis and three Cassandra nodes healthy; bootstrap exited 0 |
| `run --rm --no-deps -T --entrypoint sh app -c 'uv run --no-sync pytest -p no:cacheprovider'` | 82 passed in 0.54 seconds; existing tests use in-memory fakes and do not run lifespan |
| Actual Docker mounts/network | Passed isolation recheck |
| `exec -T cassandra-1 nodetool status` | Three nodes Up/Normal in datacenter1 |
| Container Python/urllib GET `/openapi.json` | HTTP 200 |
| POST `/urls` without credentials | HTTP 401 |
| POST `/urls` with disposable credentials | HTTP 201 and seven-character code |
| Public GET of generated code, without following redirect | HTTP 301, expected Location |
| GET `/abc` | HTTP 404 |
| Isolated Cassandra rows/Redis counter before smoke | Empty table and absent counter |
| Isolated rows after smoke | Exactly one task-created mapping |

The temporary Python smoke script used the application's configuration and Cassandra/Redis adapters to verify connection targets and initial emptiness before issuing the one write. It did not follow the external example.com redirect. These are live isolated smoke checks in addition to fake-based tests, not an existing full integration/failure suite. Dependency image build/pulls used existing Docker targets; no manifests or lockfiles were changed. The internal network did not expose usable host listeners; HTTP checks ran inside app.

## Shutdown and cleanup

With the same Compose prefix, `stop app redis cassandra-1 cassandra-2 cassandra-3 cassandra-init` stopped only task-created services. Only that disposable project's containers and internal network were removed afterwards. The newly created temporary database directories, mapping, counter and fixture provisioning were removed after shutdown. Original portfolio containers, volumes, database directories and existing records/schema were preserved. No down -v, pruning, database reset, truncate or destructive migration was run.

## Limits and documentation checks

No live check ran against existing application databases. Production deployment, browser/Postman execution, load, failover, restart/recovery and multi-host fault isolation were not tested. Postman JSON was inspected: the tracked `url-shortener.local.postman_environment.json` declares collection v2.1, contains two requests and empty Basic Auth defaults. Updated docs point to that actual filename. Local bilingual page pairs, links/anchors, paths and whitespace checks passed; no required-location documentation exceptions remain.

## Static documentation audit — 2026-10-09

Inspected HTTP/service/configuration, counter allocation, Base62/obfuscation, Cassandra adapter, fake tests, manifests and Compose/bootstrap. Documented custom-alphabet padding and counter-loss-after-initialization limits without changing source. Updated configuration guidance and interview follow-ups/study order. No tests, requests, bootstrap, dependency installation or Redis/Cassandra operations were executed. Historical 82-test and isolated smoke results above were not repeated.

Static local-link/anchor, fence, language-pair and documentation-only SHA-256 checks are recorded in the shared [interview review](../../../../engineering-library/docs/en/testing/verification.md). Runtime environment files and secret-bearing backups were not read or modified.

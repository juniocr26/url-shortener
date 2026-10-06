# Docker development setup and recovery

Execute every command below from the host `url-shortener/` directory. Require Docker Engine/Desktop, Compose (audit v5.1.4), registry access and enough disk space for Python wheels. No host Python/uv installation is needed. Build arguments default to Python 3.14 and uv 0.8.17; the manifest requires Python >=3.14. Redis uses redis:7-alpine and Cassandra cassandra:5.0. Floating image tags can change patch versions; record the actual versions with the safe commands below. Python dependencies and dev tools come from pyproject.toml/uv.lock using uv, not Uvicorn.

## Services and startup side effects

Compose project name is `url-shortener`. `app` runs FastAPI through Uvicorn with reload; `redis` stores the persistent ID counter; `cassandra-1`, `cassandra-2`, `cassandra-3` form the database cluster. `cassandra-init` bootstraps authentication/schema. The app listens on loopback APP_PORT (default 8000), Redis on REDIS_PORT (6379), and cassandra-1 on fixed port 9042.

Cassandra node entrypoints modify authenticator/authorizer settings in container `/etc/cassandra/cassandra.yaml`. Bootstrap can create/alter roles, alter system_auth replication, create/alter the application keyspace and create a table. FastAPI lifespan connects to Cassandra and runs CREATE TABLE IF NOT EXISTS. Redis writes happen on URL generation. There is no separate worker or scheduler in this Compose configuration. Ordinary `up` is not a safe dependency audit, even if resources already exist. None of these startup operations were run here.

## Fresh clone: safe setup without database startup

```sh
if [ ! -e .env ]; then cp .env.example .env; fi
# Edit local configuration with your own credentials/settings; never print or commit it.
mkdir -p .venv .cache/uv
docker ps --format '{{.Names}} {{.Ports}}'
docker compose -f compose.yaml -f compose.development.yaml config --quiet
docker compose -f compose.yaml -f compose.development.yaml build app
docker compose -f compose.yaml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh app -c 'uv sync --frozen --no-install-project'
docker compose -f compose.yaml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh app -c 'python --version; uv --version; python -c "import sys,fastapi,uvicorn,redis,cassandra.cluster; print(sys.prefix); print(fastapi.__file__)"'
```

Compose still requires CASSANDRA_USERNAME/CASSANDRA_PASSWORD for interpolation, even when only app is selected. Supply actual local values, not invented credentials. Other custom authentication/obfuscation settings follow `.env.example`. `--no-deps` avoids Redis, all Cassandra nodes and cassandra-init; `--entrypoint sh` bypasses Uvicorn. Commands run at container `/app` and publish no ports. `uv sync --frozen --no-install-project` installs locked dependencies including the dev group; the repository has no packaged project build requirement. Use `--no-dev` only when intentionally omitting dev tools, matching the production image installation. Do not run uv lock or dependency upgrades to repair deleted packages.

## Host dependency mapping

| Component / installer | Container path | Host path relative to project | Mount | Purpose |
| --- | --- | --- | --- | --- |
| Python / uv | `/opt/venv` | `.venv` | Bind | Installed Python virtual environment |
| Python / uv | `/opt/venv/lib/python3.14/site-packages` | `.venv/lib/python3.14/site-packages` | Same bind | Installed runtime/dev packages |
| uv download cache | `/home/app/.cache/uv` | `.cache/uv` | Bind | Downloaded wheels/source archives and reusable cache metadata |
| Application source | `/app` | Project root | Bind | Live source; also exposes .venv via `/app/.venv` |

The override replaces the named app_uv_cache mount at the same target. UV_PROJECT_ENVIRONMENT remains `/opt/venv`, and PATH starts with `/opt/venv/bin`; installation and Uvicorn use the same host-persisted environment. Existing named caches were not deleted. Source mounting alone did not persist the original `/opt/venv`, which was copied into the image. The development image has uv/Python/user setup but no baked application dependencies; base runtime still installs locked no-dev dependencies into its image and retains its existing startup command.

The uv cache is downloaded material, not the installed environment. Clearing it costs downloads but does not uninstall .venv. Python bytecode, pytest/coverage output and other generated artifacts are not configuration backups. This project has no node_modules/vendor/Maven/Go component. .venv and .cache stay ignored and excluded from build contexts.

## Startup and shutdown

The safe initial startup is the one-off setup/import flow above. Full application startup is blocked for this audit because both Compose bootstrap and application lifespan perform schema writes. The normal repository command is `docker compose -f compose.yaml -f compose.development.yaml up -d`; it starts databases and schema bootstrap and must only be used as an intentional application operation with the correct database/credentials, outside this dependency-only procedure. A fresh clone needs intentional schema initialization; dependency installation cannot provide it. Do not assume `--no-deps app` disables the application's own schema initialization.

If you started application services separately, stop only those you started, explicitly naming them:

```sh
docker compose -f compose.yaml -f compose.development.yaml stop app
# Only if YOU started these database services:
docker compose -f compose.yaml -f compose.development.yaml stop redis cassandra-1 cassandra-2 cassandra-3 cassandra-init
```

One-off `run --rm` containers exit and remove themselves. Do not remove volumes, delete database directories or prune resources for dependency recovery.

## Recovery after accidental deletion

If your app is running, stop it before synchronizing .venv; database services do not need to be stopped for a dependency install. Restore missing directories and rerun the one-off frozen sync above. It works without an app that can stay running and does not need an image rebuild. Deleting .cache/uv alone leaves installed packages intact; uv repopulates the cache on a subsequent required download. Deleting .venv requires uv sync to recreate the environment; its generated pyvenv.cfg/bin scripts/site-packages are rebuilt by uv, not restored custom settings.

If an existing app container holds a stale bind after host directory deletion/recreation, recreate that container only after database/application startup writes are acceptable:

```sh
docker compose -f compose.yaml -f compose.development.yaml up -d --no-deps --force-recreate app
```

This launches FastAPI and still runs its lifespan schema initialization. It was not executed here. Rebuild only for Python/uv/system image changes, not missing dependency files.

## Configuration files and generated configuration recovery

Missing `.env`: use the guarded template copy; restore custom values from a backup/secret source. In particular, preserve the original OBFUSCATING_KEY for existing short codes, and the existing database/auth credentials. Template copying cannot recover those values. Never rotate or invent them as a dependency fix.

Missing tracked `compose.yaml`, `compose.development.yaml`, Dockerfile, `docker/cassandra/*.sh`, pyproject.toml, uv.lock or application config source: confirm the exact path is absent, then restore it individually with `git restore --source=HEAD -- path/to/missing-file` once that file has been committed. Newly added uncommitted override/guide files need your working-tree backup until committed. Do not restore whole directories over existing edits. No tracked environment generation command recovers custom settings.

`.venv/pyvenv.cfg` is generated virtual environment metadata and uv sync recreates it as part of restoring an absent environment. For an otherwise intact environment whose generated pyvenv.cfg was deleted, stop your app and run this tested repair (it preserves existing environment files):

```sh
docker compose -f compose.yaml -f compose.development.yaml run --rm --no-deps -T --entrypoint sh app -c 'uv venv --allow-existing --python /usr/local/bin/python3 /opt/venv && uv sync --frozen --no-install-project'
```

This repairs generated metadata/scripts; it does not recover custom configuration. Other partial-corruption scenarios were not tested. uv cache metadata is likewise disposable/recreated; custom configuration mistakenly stored there requires backup.

Cassandra `/etc/cassandra` comes from its image and the official/wrapper entrypoints; it is not host-persisted configuration. A replacement node container regenerates defaults from the image/environment, but that starts database processes and was not tested. Lost manual container configuration requires backup, not uv sync. `.dockerized-cassandra/cassandra-*` and `.dockerized-redis` contain persistent database state, including generated metadata/AOF configuration; recover lost contents only through database backup procedures. Never initialize an empty replacement and claim the old records/counters were recovered. No other application-generated configuration directory was identified.

## Troubleshooting

Use both Compose files. Base Compose alone uses image `/opt/venv` and a named uv cache. Inspect an actual container with `docker inspect CONTAINER --format '{{json .Mounts}}'`; verify `/opt/venv` and `/home/app/.cache/uv` are binds. `python -c 'import sys; print(sys.prefix)'` must print `/opt/venv`. `uvicorn --version` checks the executable without starting FastAPI. Do not treat uvicorn as an installer or run database-dependent app/tests for missing-package diagnosis.

The image's app UID/GID default to 1000 and must be able to write the two binds. Docker Desktop translation worked during this audit. For Linux host permissions, build with APP_UID/APP_GID matching the intended host owner, or run only setup with `--user "$(id -u):$(id -g)" -e HOME=/tmp`, keeping explicit UV_CACHE_DIR/UV_PROJECT_ENVIRONMENT. Inspect/correct ownership only for the affected generated directories. Never use chmod 777 or broad recursive permissions.

Inspect host listeners before application startup. APP_PORT and REDIS_PORT are configurable in local .env; Cassandra port 9042 is fixed in base Compose, so use a scoped port override or leave startup blocked when occupied. Do not stop unrelated services. The APP_PORT setting also affects the internal app port; Redis's app connection configuration deserves separate review if changing REDIS_PORT, since Redis listens internally on 6379. Such network changes are outside this audit.

The host .venv contains Linux interpreter links, scripts with `/opt/venv` paths and native extension wheels for the container platform. Do not activate/use it directly on macOS or Windows. Reinstall in the intended matching container platform after changing Python version/architecture. A host-native environment must be separate; host persistence does not make binary dependencies portable.

## Verification (2026-10-06)

Inspected Docker/Compose manifests, locked installer model, Cassandra entrypoints/bootstrap/healthchecks, FastAPI lifespan and database adapters. Resolved mounts confirm host binds for environment/cache and preserved database mounts. Built the dependency-only development target; normal production target structure remains intact. No pre-existing containers or conflicting listeners on 8000/6379/9042 were observed. Installation/import/recovery results follow below. Full application startup, database connections, schema bootstrap and tests are intentionally unverified/blocked due to database write side effects.

`uv sync --frozen --no-install-project` installed 32 locked packages including dev tools. Observed runtime: CPython 3.14.8, uv 0.8.17, Uvicorn 0.52.4 on Linux. The host `.venv/lib/python3.14/site-packages/fastapi/__init__.py`, `.venv/pyvenv.cfg` and uv wheel cache physically exist. The install container and a fresh container both reported sys.prefix `/opt/venv` and FastAPI's file under that environment; the fresh container also completed frozen offline sync and Uvicorn version check. No app module/lifespan or database resources were instantiated.

Empty-directory recovery passed using temporary host binds for both /opt/venv and the uv cache: frozen sync installed all 32 packages and imports succeeded; host package/cache files were confirmed. In that same isolated environment only generated pyvenv.cfg was then deleted; `uv venv --allow-existing --python /usr/local/bin/python3 /opt/venv`, offline frozen sync and imports restored it successfully. Normal host dependencies/configuration were never deleted or renamed. Temporary directories were removed after all setup containers exited. No audit containers remain running.

## Copyable host verification and tracked configuration recovery

```sh
# From the host project root.
test -f .venv/lib/python3.14/site-packages/fastapi/__init__.py
test -f .venv/pyvenv.cfg
test -d .cache/uv/wheels-v5
for path in .env.example compose.yaml docker/Dockerfile docker/cassandra/entrypoint.sh docker/cassandra/bootstrap.sh docker/cassandra/healthcheck.sh pyproject.toml uv.lock app/core/config.py; do
  if [ ! -e "$path" ]; then git restore --source=HEAD -- "$path"; fi
done
```

This restores only absent tracked files, preserving existing edits. Custom untracked configuration still requires a backup. Until the new development override and guide are committed, their recovery requires a working-tree backup. The base production image build was not rerun; production stage behavior was reviewed from the Dockerfile.

#!/usr/bin/env bash
set -euo pipefail

required_env() {
  local name="$1"
  if [ -z "${!name:-}" ]; then
    echo "Missing required environment variable: ${name}" >&2
    exit 1
  fi
}

required_env "CASSANDRA_USERNAME"
required_env "CASSANDRA_PASSWORD"
required_env "CASSANDRA_KEYSPACE"
required_env "CASSANDRA_DATACENTER"

host="${CASSANDRA_BOOTSTRAP_HOST:-cassandra-1}"
port="${CASSANDRA_PORT:-9042}"

write_credentials() {
  local path="$1"
  local username="$2"
  local password="$3"

  umask 077
  cat > "$path" <<EOF
[plain_text_auth]
username = ${username}
password = ${password}
EOF
}

run_cql_file() {
  local username="$1"
  local password="$2"
  local cql_file="$3"
  local credentials_file
  local error_file

  credentials_file="$(mktemp)"
  error_file="$(mktemp)"
  write_credentials "$credentials_file" "$username" "$password"

  if cqlsh "$host" "$port" \
    --credentials "$credentials_file" \
    --file "$cql_file" >/dev/null 2>"$error_file"; then
    rm -f "$credentials_file" "$error_file"
    return 0
  fi

  rm -f "$credentials_file" "$error_file"
  return 1
}

can_connect() {
  local username="$1"
  local password="$2"
  local cql_file
  local status

  cql_file="$(mktemp)"
  printf "SELECT release_version FROM system.local;\n" > "$cql_file"

  if run_cql_file "$username" "$password" "$cql_file"; then
    status=0
  else
    status=1
  fi

  rm -f "$cql_file"
  return "$status"
}

write_role_cql() {
  local path="$1"

  CQL_FILE="$path" python3 <<'PY'
import os


def quote_identifier(value: str) -> str:
    if not value:
        raise SystemExit("Cassandra role name must not be empty")
    return '"' + value.replace('"', '""') + '"'


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


role = quote_identifier(os.environ["CASSANDRA_USERNAME"])
password = quote_literal(os.environ["CASSANDRA_PASSWORD"])

with open(os.environ["CQL_FILE"], "w", encoding="utf-8") as cql:
    cql.write(
        f"CREATE ROLE IF NOT EXISTS {role} "
        f"WITH PASSWORD = {password} AND LOGIN = true AND SUPERUSER = true;\n"
    )
PY
}

write_role_update_cql() {
  local path="$1"

  CQL_FILE="$path" python3 <<'PY'
import os


def quote_identifier(value: str) -> str:
    if not value:
        raise SystemExit("Cassandra role name must not be empty")
    return '"' + value.replace('"', '""') + '"'


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


role = quote_identifier(os.environ["CASSANDRA_USERNAME"])
password = quote_literal(os.environ["CASSANDRA_PASSWORD"])

with open(os.environ["CQL_FILE"], "w", encoding="utf-8") as cql:
    cql.write(
        f"ALTER ROLE {role} "
        f"WITH PASSWORD = {password} AND LOGIN = true AND SUPERUSER = true;\n"
    )
PY
}

write_keyspace_cql() {
  local path="$1"

  CQL_FILE="$path" python3 <<'PY'
import os


def quote_identifier(value: str) -> str:
    if not value:
        raise SystemExit("Cassandra keyspace name must not be empty")
    return '"' + value.replace('"', '""') + '"'


def quote_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


keyspace = quote_identifier(os.environ["CASSANDRA_KEYSPACE"])
datacenter = quote_literal(os.environ["CASSANDRA_DATACENTER"])

replication = (
    "{'class': 'NetworkTopologyStrategy', "
    f"{datacenter}: 3"
    "}"
)

with open(os.environ["CQL_FILE"], "w", encoding="utf-8") as cql:
    cql.write(f"ALTER KEYSPACE system_auth WITH replication = {replication};\n")
    cql.write(f"CREATE KEYSPACE IF NOT EXISTS {keyspace} WITH replication = {replication};\n")
    cql.write(f"ALTER KEYSPACE {keyspace} WITH replication = {replication};\n")
PY
}

write_schema_cql() {
  local path="$1"

  CQL_FILE="$path" python3 <<'PY'
import os


def quote_identifier(value: str) -> str:
    if not value:
        raise SystemExit("Cassandra keyspace name must not be empty")
    return '"' + value.replace('"', '""') + '"'


keyspace = quote_identifier(os.environ["CASSANDRA_KEYSPACE"])

with open(os.environ["CQL_FILE"], "w", encoding="utf-8") as cql:
    cql.write(
        f"CREATE TABLE IF NOT EXISTS {keyspace}.urls_by_id ("
        "id bigint PRIMARY KEY, "
        "original_url text"
        ");\n"
    )
PY
}

role_create_cql="$(mktemp)"
role_update_cql="$(mktemp)"
keyspace_cql="$(mktemp)"
schema_cql="$(mktemp)"
trap 'rm -f "$role_create_cql" "$role_update_cql" "$keyspace_cql" "$schema_cql"' EXIT

if ! can_connect "$CASSANDRA_USERNAME" "$CASSANDRA_PASSWORD"; then
  write_role_cql "$role_create_cql"
  if ! run_cql_file "cassandra" "cassandra" "$role_create_cql"; then
    echo "Failed to create or update the configured Cassandra role." >&2
    exit 1
  fi
fi

if ! can_connect "$CASSANDRA_USERNAME" "$CASSANDRA_PASSWORD"; then
  write_role_update_cql "$role_update_cql"
  if ! run_cql_file "cassandra" "cassandra" "$role_update_cql"; then
    echo "Failed to update the configured Cassandra role." >&2
    exit 1
  fi
fi

if ! can_connect "$CASSANDRA_USERNAME" "$CASSANDRA_PASSWORD"; then
  echo "Configured Cassandra credentials did not authenticate after bootstrap." >&2
  exit 1
fi

write_keyspace_cql "$keyspace_cql"
if ! run_cql_file "$CASSANDRA_USERNAME" "$CASSANDRA_PASSWORD" "$keyspace_cql"; then
  echo "Failed to create or update the configured Cassandra keyspace." >&2
  exit 1
fi

write_schema_cql "$schema_cql"
if ! run_cql_file "$CASSANDRA_USERNAME" "$CASSANDRA_PASSWORD" "$schema_cql"; then
  echo "Failed to create or update the URL persistence table." >&2
  exit 1
fi

echo "Cassandra authentication, keyspace, and URL table bootstrap completed."

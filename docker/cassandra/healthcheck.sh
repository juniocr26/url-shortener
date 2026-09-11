#!/usr/bin/env bash
set -euo pipefail

host="${CQLSH_HOST:-127.0.0.1}"
port="${CQLSH_PORT:-9042}"

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

try_cql() {
  local username="$1"
  local password="$2"
  local credentials_file

  credentials_file="$(mktemp)"
  write_credentials "$credentials_file" "$username" "$password"

  if cqlsh "$host" "$port" \
    --credentials "$credentials_file" \
    -e "DESCRIBE KEYSPACES;" >/dev/null 2>&1; then
    rm -f "$credentials_file"
    return 0
  fi

  rm -f "$credentials_file"
  return 1
}

if [ -n "${CASSANDRA_USERNAME:-}" ] && [ -n "${CASSANDRA_PASSWORD:-}" ]; then
  if try_cql "$CASSANDRA_USERNAME" "$CASSANDRA_PASSWORD"; then
    exit 0
  fi
fi

try_cql "cassandra" "cassandra"

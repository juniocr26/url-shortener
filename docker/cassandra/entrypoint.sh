#!/usr/bin/env bash
set -euo pipefail

cassandra_yaml="${CASSANDRA_CONF:-/etc/cassandra}/cassandra.yaml"

patch_yaml_value() {
  local key="$1"
  local value="$2"

  sed -ri "s|^(# )?(${key}:).*|\\2 ${value}|" "$cassandra_yaml"
}

patch_yaml_value "authenticator" "PasswordAuthenticator"
patch_yaml_value "authorizer" "CassandraAuthorizer"

exec /usr/local/bin/docker-entrypoint.sh "$@"

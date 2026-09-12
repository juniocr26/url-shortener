import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_env: str
    app_host: str
    app_port: int
    basic_auth_username: str | None
    basic_auth_password: str | None
    redis_host: str
    redis_port: int
    redis_db: int
    redis_password: str | None
    cassandra_contact_points: tuple[str, ...]
    cassandra_port: int
    cassandra_keyspace: str
    cassandra_username: str | None
    cassandra_password: str | None
    cassandra_datacenter: str
    short_url_base: str
    url_id_start: int
    base62_alphabet: str
    obfuscating_key: str | None

    @property
    def basic_auth_configured(self) -> bool:
        return bool(self.basic_auth_username and self.basic_auth_password)

    @property
    def cassandra_auth_configured(self) -> bool:
        return bool(self.cassandra_username and self.cassandra_password)


def _optional_env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None or value == "":
        return None
    return value


def _int_env(name: str, default: int) -> int:
    return int(os.environ.get(name, str(default)))


def _csv_env(name: str, default: str) -> tuple[str, ...]:
    value = os.environ.get(name, default)
    items = tuple(item.strip() for item in value.split(",") if item.strip())

    if not items:
        raise ValueError(f"{name} must contain at least one value.")

    return items


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.environ.get("APP_ENV", "development"),
        app_host=os.environ.get("APP_HOST", "0.0.0.0"),
        app_port=_int_env("APP_PORT", 8000),
        basic_auth_username=_optional_env("BASIC_AUTH_USERNAME"),
        basic_auth_password=_optional_env("BASIC_AUTH_PASSWORD"),
        redis_host=os.environ.get("REDIS_HOST", "redis"),
        redis_port=_int_env("REDIS_PORT", 6379),
        redis_db=_int_env("REDIS_DB", 0),
        redis_password=_optional_env("REDIS_PASSWORD"),
        cassandra_contact_points=_csv_env(
            "CASSANDRA_CONTACT_POINTS",
            "cassandra-1,cassandra-2,cassandra-3",
        ),
        cassandra_port=_int_env("CASSANDRA_PORT", 9042),
        cassandra_keyspace=os.environ.get(
            "CASSANDRA_KEYSPACE",
            "url_shortener",
        ),
        cassandra_username=_optional_env("CASSANDRA_USERNAME"),
        cassandra_password=_optional_env("CASSANDRA_PASSWORD"),
        cassandra_datacenter=os.environ.get(
            "CASSANDRA_DATACENTER",
            "datacenter1",
        ),
        short_url_base=os.environ.get(
            "SHORT_URL_BASE",
            "http://localhost:8000",
        ),
        url_id_start=_int_env("URL_ID_START", 62**4),
        base62_alphabet=os.environ.get(
            "BASE62_ALPHABET",
            "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
        ),
        obfuscating_key=_optional_env("OBFUSCATING_KEY"),
    )

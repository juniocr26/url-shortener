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

    @property
    def basic_auth_configured(self) -> bool:
        return bool(self.basic_auth_username and self.basic_auth_password)


def _optional_env(name: str) -> str | None:
    value = os.environ.get(name)
    if value is None or value == "":
        return None
    return value


@lru_cache
def get_settings() -> Settings:
    return Settings(
        app_env=os.environ.get("APP_ENV", "development"),
        app_host=os.environ.get("APP_HOST", "0.0.0.0"),
        app_port=int(os.environ.get("APP_PORT", "8000")),
        basic_auth_username=_optional_env("BASIC_AUTH_USERNAME"),
        basic_auth_password=_optional_env("BASIC_AUTH_PASSWORD"),
    )

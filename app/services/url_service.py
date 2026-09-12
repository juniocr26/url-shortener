from app.core.config import Settings
from app.helpers.base62 import decode_base62, encode_base62
from app.helpers.obfuscation import (
    ObfuscationConfigurationError,
    deobfuscate_base62,
    obfuscate_base62,
)
from app.infrastructure.cassandra_url_store import (
    CassandraUrlStore,
    CassandraUrlStoreError,
)
from app.infrastructure.redis_id_generator import (
    RedisIdGenerationError,
    RedisIdGenerator,
)
from app.schemas import CreateUrlRequest, CreateUrlResponse


class UrlShortenerError(RuntimeError):
    pass


class InvalidShortCode(UrlShortenerError):
    pass


class ShortCodeNotFound(UrlShortenerError):
    pass


class UrlShortenerConfigurationError(UrlShortenerError):
    pass


class UrlShortenerInfrastructureError(UrlShortenerError):
    pass


class UrlShortenerService:
    def __init__(
        self,
        id_generator: RedisIdGenerator,
        url_store: CassandraUrlStore,
        settings: Settings,
    ) -> None:
        self._id_generator = id_generator
        self._url_store = url_store
        self._settings = settings

    def create_short_url(
        self,
        payload: CreateUrlRequest,
    ) -> CreateUrlResponse:
        original_url = str(payload.url)

        try:
            url_id = self._id_generator.generate_id()
            base62_id = encode_base62(url_id)
            short_code = obfuscate_base62(base62_id)
            self._url_store.store_url(url_id, original_url)
        except RedisIdGenerationError as exc:
            raise UrlShortenerInfrastructureError(
                "Redis ID generation is unavailable."
            ) from exc
        except CassandraUrlStoreError as exc:
            raise UrlShortenerInfrastructureError(
                "Cassandra persistence is unavailable."
            ) from exc
        except ObfuscationConfigurationError as exc:
            raise UrlShortenerConfigurationError(
                "URL obfuscation is not configured."
            ) from exc
        except ValueError as exc:
            raise UrlShortenerConfigurationError(
                "URL shortening configuration is invalid."
            ) from exc

        return CreateUrlResponse(
            short_code=short_code,
            short_url=self._build_short_url(short_code),
        )

    def resolve_short_url(self, short_code: str) -> str:
        try:
            base62_id = deobfuscate_base62(short_code)
            url_id = decode_base62(base62_id)
            original_url = self._url_store.get_url(url_id)
        except CassandraUrlStoreError as exc:
            raise UrlShortenerInfrastructureError(
                "Cassandra lookup is unavailable."
            ) from exc
        except ObfuscationConfigurationError as exc:
            raise UrlShortenerConfigurationError(
                "URL obfuscation is not configured."
            ) from exc
        except ValueError as exc:
            raise InvalidShortCode("Short code is invalid.") from exc

        if original_url is None:
            raise ShortCodeNotFound("Short code was not found.")

        return original_url

    def _build_short_url(self, short_code: str) -> str:
        return f"{self._settings.short_url_base.rstrip('/')}/{short_code}"

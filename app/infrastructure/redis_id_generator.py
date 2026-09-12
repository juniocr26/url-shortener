from threading import Lock

from redis import Redis
from redis.exceptions import RedisError

from app.core.config import Settings


REDIS_COUNTER_KEY = "url_shortener:url_id_counter"


class RedisIdGenerationError(RuntimeError):
    pass


class RedisIdGenerator:
    def __init__(
        self,
        client: Redis,
        start: int,
        counter_key: str = REDIS_COUNTER_KEY,
    ) -> None:
        if start < 1:
            raise ValueError("URL_ID_START must be greater than zero.")

        self._client = client
        self._start = start
        self._counter_key = counter_key
        self._initialized = False
        self._lock = Lock()

    @property
    def counter_key(self) -> str:
        return self._counter_key

    def initialize_counter(self) -> None:
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            try:
                self._client.set(
                    self._counter_key,
                    self._start - 1,
                    nx=True,
                )
            except RedisError as exc:
                raise RedisIdGenerationError(
                    "Redis counter initialization failed."
                ) from exc

            self._initialized = True

    def generate_id(self) -> int:
        self.initialize_counter()

        try:
            generated_id = self._client.incr(self._counter_key)
        except RedisError as exc:
            raise RedisIdGenerationError(
                "Redis ID generation failed."
            ) from exc

        return int(generated_id)


def create_redis_client(settings: Settings) -> Redis:
    return Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=settings.redis_db,
        password=settings.redis_password,
        decode_responses=True,
        socket_connect_timeout=5,
        socket_timeout=5,
    )

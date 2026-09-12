import pytest
from redis.exceptions import RedisError

from app.infrastructure.redis_id_generator import (
    REDIS_COUNTER_KEY,
    RedisIdGenerationError,
    RedisIdGenerator,
)


URL_ID_START = 62**4


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, int] = {}
        self.operations: list[tuple[str, str, int | bool | None]] = []

    def set(self, key: str, value: int, nx: bool = False) -> bool:
        self.operations.append(("set", key, value if not nx else True))

        if nx and key in self.values:
            return False

        self.values[key] = int(value)
        return True

    def incr(self, key: str) -> int:
        self.operations.append(("incr", key, None))
        self.values[key] = self.values.get(key, 0) + 1
        return self.values[key]


class FailingRedis(FakeRedis):
    def __init__(self, fail_on: str) -> None:
        super().__init__()
        self.fail_on = fail_on

    def set(self, key: str, value: int, nx: bool = False) -> bool:
        if self.fail_on == "set":
            raise RedisError("set failed")
        return super().set(key, value, nx)

    def incr(self, key: str) -> int:
        if self.fail_on == "incr":
            raise RedisError("incr failed")
        return super().incr(key)


def test_first_clean_generated_id_starts_at_62_to_the_fourth() -> None:
    redis = FakeRedis()
    generator = RedisIdGenerator(redis, start=URL_ID_START)

    generated_id = generator.generate_id()

    assert generated_id == URL_ID_START
    assert redis.values[REDIS_COUNTER_KEY] == URL_ID_START
    assert redis.operations == [
        ("set", REDIS_COUNTER_KEY, True),
        ("incr", REDIS_COUNTER_KEY, None),
    ]


def test_existing_counter_is_not_overwritten() -> None:
    redis = FakeRedis()
    redis.values[REDIS_COUNTER_KEY] = 20
    generator = RedisIdGenerator(redis, start=URL_ID_START)

    generated_id = generator.generate_id()

    assert generated_id == 21
    assert redis.values[REDIS_COUNTER_KEY] == 21


def test_subsequent_increments_are_sequential() -> None:
    redis = FakeRedis()
    generator = RedisIdGenerator(redis, start=URL_ID_START)

    generated_ids = [
        generator.generate_id(),
        generator.generate_id(),
        generator.generate_id(),
    ]

    assert generated_ids == [
        URL_ID_START,
        URL_ID_START + 1,
        URL_ID_START + 2,
    ]


def test_initialization_is_idempotent_for_one_generator() -> None:
    redis = FakeRedis()
    generator = RedisIdGenerator(redis, start=URL_ID_START)

    generator.initialize_counter()
    generator.initialize_counter()

    set_operations = [
        operation for operation in redis.operations if operation[0] == "set"
    ]
    assert len(set_operations) == 1
    assert redis.values[REDIS_COUNTER_KEY] == URL_ID_START - 1


def test_initialization_is_non_destructive_across_generators() -> None:
    redis = FakeRedis()
    first_generator = RedisIdGenerator(redis, start=URL_ID_START)
    second_generator = RedisIdGenerator(redis, start=URL_ID_START)

    first_generator.initialize_counter()
    redis.values[REDIS_COUNTER_KEY] = URL_ID_START + 10
    second_generator.initialize_counter()

    assert redis.values[REDIS_COUNTER_KEY] == URL_ID_START + 10


def test_id_generation_uses_atomic_redis_increment() -> None:
    redis = FakeRedis()
    generator = RedisIdGenerator(redis, start=URL_ID_START)

    generator.generate_id()

    assert ("incr", REDIS_COUNTER_KEY, None) in redis.operations


def test_initialization_failure_is_wrapped() -> None:
    generator = RedisIdGenerator(
        FailingRedis(fail_on="set"),
        start=URL_ID_START,
    )

    with pytest.raises(RedisIdGenerationError):
        generator.initialize_counter()


def test_increment_failure_is_wrapped() -> None:
    generator = RedisIdGenerator(
        FailingRedis(fail_on="incr"),
        start=URL_ID_START,
    )

    with pytest.raises(RedisIdGenerationError):
        generator.generate_id()

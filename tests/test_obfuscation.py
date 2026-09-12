import pytest

from app.core.config import get_settings
from app.helpers.obfuscation import (
    deobfuscate_base62,
    obfuscate_base62,
)


def set_obfuscating_key(
    monkeypatch: pytest.MonkeyPatch,
    key: str,
) -> None:
    monkeypatch.setenv("OBFUSCATING_KEY", key)
    get_settings.cache_clear()


@pytest.fixture(autouse=True)
def obfuscating_key_env(monkeypatch: pytest.MonkeyPatch) -> None:
    set_obfuscating_key(
        monkeypatch,
        "test-obfuscating-key-for-url-shortener",
    )

    yield

    get_settings.cache_clear()


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "1",
        "A",
        "z",
        "10",
        "100",
        "10000",
        "Ab3xZ9",
    ],
)
def test_obfuscation_round_trip(value: str) -> None:
    obfuscated = obfuscate_base62(value)
    restored = deobfuscate_base62(obfuscated)

    assert restored == value


@pytest.mark.parametrize(
    "value",
    [
        "0",
        "1",
        "10",
        "10000",
        "Ab3xZ9",
    ],
)
def test_obfuscated_value_always_has_seven_characters(value: str) -> None:
    obfuscated = obfuscate_base62(value)

    assert len(obfuscated) == 7


def test_same_value_with_same_key_produces_same_result() -> None:
    first = obfuscate_base62("10000")
    second = obfuscate_base62("10000")

    assert first == second


def test_different_values_produce_different_results() -> None:
    first = obfuscate_base62("10000")
    second = obfuscate_base62("10001")

    assert first != second


def test_different_keys_produce_different_results(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    set_obfuscating_key(monkeypatch, "first-test-key")

    first = obfuscate_base62("10000")

    set_obfuscating_key(monkeypatch, "second-test-key")

    second = obfuscate_base62("10000")

    assert first != second


def test_deobfuscation_with_wrong_key_does_not_restore_original(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    original = "10000"

    set_obfuscating_key(monkeypatch, "correct-test-key")

    obfuscated = obfuscate_base62(original)

    set_obfuscating_key(monkeypatch, "wrong-test-key")

    restored = deobfuscate_base62(obfuscated)

    assert restored != original


def test_deobfuscation_rejects_values_with_less_than_seven_characters() -> None:
    with pytest.raises(ValueError):
        deobfuscate_base62("abc123")


def test_deobfuscation_rejects_values_with_more_than_seven_characters() -> None:
    with pytest.raises(ValueError):
        deobfuscate_base62("abc12345")


def test_obfuscation_rejects_value_outside_seven_character_space() -> None:
    with pytest.raises(ValueError):
        obfuscate_base62("10000000")

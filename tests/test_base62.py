import pytest

from app.helpers.base62 import decode_base62, encode_base62


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (0, "0"),
        (1, "1"),
        (9, "9"),
        (10, "A"),
        (35, "Z"),
        (36, "a"),
        (61, "z"),
        (62, "10"),
        (62**2, "100"),
        (62**4, "10000"),
    ],
)
def test_encode_base62(value: int, expected: str) -> None:
    assert encode_base62(value) == expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("0", 0),
        ("1", 1),
        ("9", 9),
        ("A", 10),
        ("Z", 35),
        ("a", 36),
        ("z", 61),
        ("10", 62),
        ("100", 62**2),
        ("10000", 62**4),
    ],
)
def test_decode_base62(value: str, expected: int) -> None:
    assert decode_base62(value) == expected


@pytest.mark.parametrize(
    "value",
    [
        0,
        1,
        61,
        62,
        1_000,
        62**4,
        14_776_337,
        1_000_000_000,
    ],
)
def test_base62_round_trip(value: int) -> None:
    encoded = encode_base62(value)
    decoded = decode_base62(encoded)

    assert decoded == value


def test_encode_base62_rejects_negative_values() -> None:
    with pytest.raises(ValueError):
        encode_base62(-1)


def test_decode_base62_rejects_empty_value() -> None:
    with pytest.raises(ValueError):
        decode_base62("")


def test_decode_base62_rejects_invalid_characters() -> None:
    with pytest.raises(ValueError):
        decode_base62("abc-123")
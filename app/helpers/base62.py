import os


BASE62_ALPHABET = os.getenv(
    "BASE62_ALPHABET",
    "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz",
)

BASE = len(BASE62_ALPHABET)


def encode_base62(value: int) -> str:
    if value < 0:
        raise ValueError("Value must be a non-negative integer.")

    if value == 0:
        return BASE62_ALPHABET[0]

    encoded = []

    while value > 0:
        value, remainder = divmod(value, BASE)
        encoded.append(BASE62_ALPHABET[remainder])

    return "".join(reversed(encoded))


def decode_base62(value: str) -> int:
    if not value:
        raise ValueError("Value cannot be empty.")

    decoded = 0

    for character in value:
        try:
            index = BASE62_ALPHABET.index(character)
        except ValueError:
            raise ValueError(
                f"Invalid Base62 character: {character}"
            ) from None

        decoded = decoded * BASE + index

    return decoded
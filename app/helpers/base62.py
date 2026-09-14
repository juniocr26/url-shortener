from app.core.config import get_settings

def _get_alphabet() -> str:
    alphabet = get_settings().base62_alphabet

    if len(alphabet) != 62 or len(set(alphabet)) != 62:
        raise ValueError(
            "BASE62_ALPHABET must contain exactly 62 unique characters."
        )

    return alphabet


def encode_base62(value: int) -> str:
    if value < 0:
        raise ValueError("Value must be a non-negative integer.")

    alphabet = _get_alphabet()
    base = len(alphabet)

    if value == 0:
        return alphabet[0]

    encoded = []

    while value > 0:
        value, remainder = divmod(value, base)
        encoded.append(alphabet[remainder])

    return "".join(reversed(encoded))


def decode_base62(value: str) -> int:
    if not value:
        raise ValueError("Value cannot be empty.")

    alphabet = _get_alphabet()
    base = len(alphabet)
    decoded = 0

    for character in value:
        try:
            index = alphabet.index(character)
        except ValueError:
            raise ValueError(
                f"Invalid Base62 character: {character}"
            ) from None

        decoded = decoded * base + index

    return decoded

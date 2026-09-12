import hashlib
import math

from app.core.config import get_settings
from app.helpers.base62 import decode_base62, encode_base62


BASE62_LENGTH = 7
BASE = 62
MODULUS = BASE**BASE62_LENGTH


class ObfuscationConfigurationError(RuntimeError):
    pass


def _get_key() -> str:
    key = get_settings().obfuscating_key

    if not key:
        raise ObfuscationConfigurationError(
            "OBFUSCATING_KEY is not configured."
        )

    return key


def _derive_parameters() -> tuple[int, int]:
    key = _get_key().encode("utf-8")

    digest_a = hashlib.sha256(key + b":a").digest()
    digest_b = hashlib.sha256(key + b":b").digest()

    a = int.from_bytes(digest_a, "big") % MODULUS
    b = int.from_bytes(digest_b, "big") % MODULUS

    while math.gcd(a, MODULUS) != 1:
        a = (a + 1) % MODULUS

    return a, b


def obfuscate_base62(value: str) -> str:
    numeric_value = decode_base62(value)

    if numeric_value >= MODULUS:
        raise ValueError(
            f"Value exceeds the maximum supported Base62 length of "
            f"{BASE62_LENGTH} characters."
        )

    a, b = _derive_parameters()

    obfuscated_value = (a * numeric_value + b) % MODULUS

    encoded = encode_base62(obfuscated_value)

    return encoded.rjust(BASE62_LENGTH, "0")


def deobfuscate_base62(value: str) -> str:
    if len(value) != BASE62_LENGTH:
        raise ValueError(
            f"Obfuscated value must contain exactly "
            f"{BASE62_LENGTH} characters."
        )

    obfuscated_value = decode_base62(value)

    a, b = _derive_parameters()

    inverse_a = pow(a, -1, MODULUS)

    original_value = (
        inverse_a * (obfuscated_value - b)
    ) % MODULUS

    return encode_base62(original_value)

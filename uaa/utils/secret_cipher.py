import base64
import itertools
import os
from hashlib import blake2b


def _derive_key(master: str) -> bytes:
    if not master:
        raise ValueError("SOCIAL_CFG_KEY is required to encrypt/decrypt secrets")
    return blake2b(master.encode("utf-8"), digest_size=32).digest()


def encrypt_secret(plain: str, master: str) -> str:
    """
    Lightweight XOR + base64 obfuscation.
    Không thay thế HSM; đủ để tránh lưu secret thô trong DB.
    """
    if plain is None:
        raise ValueError("plain secret is required")
    key = _derive_key(master)
    data = plain.encode("utf-8")
    cipher = bytes(b ^ k for b, k in zip(data, itertools.cycle(key)))
    return base64.urlsafe_b64encode(cipher).decode("utf-8")


def decrypt_secret(cipher_b64: str, master: str) -> str:
    if cipher_b64 is None:
        raise ValueError("encrypted secret is required")
    key = _derive_key(master)
    data = base64.urlsafe_b64decode(cipher_b64.encode("utf-8"))
    plain = bytes(b ^ k for b, k in zip(data, itertools.cycle(key)))
    return plain.decode("utf-8")


def master_key_from_env() -> str:
    return os.getenv("SOCIAL_CFG_KEY", "")

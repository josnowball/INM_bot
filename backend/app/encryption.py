"""
AES-256-GCM encryption for sensitive user data at rest.
Every encrypted field gets its own random nonce — no nonce reuse.
"""

import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import get_settings


def _get_key() -> bytes:
    hex_key = get_settings().encryption_key
    if hex_key == "CHANGE-ME":
        raise RuntimeError("ENCRYPTION_KEY not configured — refusing to start")
    key = bytes.fromhex(hex_key)
    if len(key) != 32:
        raise ValueError("ENCRYPTION_KEY must be exactly 32 bytes (64 hex chars)")
    return key


def encrypt(plaintext: str) -> str:
    """Encrypt a string → base64 token (nonce || ciphertext)."""
    if not plaintext:
        return ""
    key = _get_key()
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, plaintext.encode(), None)
    return base64.urlsafe_b64encode(nonce + ct).decode()


def decrypt(token: str) -> str:
    """Decrypt a base64 token back to the original string."""
    if not token:
        return ""
    key = _get_key()
    raw = base64.urlsafe_b64decode(token)
    nonce, ct = raw[:12], raw[12:]
    return AESGCM(key).decrypt(nonce, ct, None).decode()

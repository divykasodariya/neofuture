"""
SHA-256 PII hashing utilities.

All identifiers are hashed before entering the system.
The raw PII never touches storage.
"""

import hashlib
from app.core.config import get_settings


def _hash(value: str, prefix: str) -> str:
    """Hash a value with the configured salt and a type prefix."""
    settings = get_settings()
    salted = f"{settings.pii_hash_salt}:{prefix}:{value}"
    return hashlib.sha256(salted.encode("utf-8")).hexdigest()


def hash_account(account_number: str) -> str:
    """Hash an account number. Returns deterministic hex digest."""
    return _hash(account_number, "account")


def hash_merchant(merchant_id: str) -> str:
    """Hash a merchant identifier."""
    return _hash(merchant_id, "merchant")


def hash_device(device_fingerprint: str) -> str:
    """Hash a device fingerprint."""
    return _hash(device_fingerprint, "device")


def hash_email(email: str) -> str:
    """Hash an email address."""
    return _hash(email.lower().strip(), "email")


def hash_ip(ip_address: str) -> str:
    """Hash an IP address."""
    return _hash(ip_address, "ip")

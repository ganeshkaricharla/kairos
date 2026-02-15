"""Encryption utilities for sensitive data like API keys."""
from cryptography.fernet import Fernet
from app.config import settings


def _get_cipher():
    """Get Fernet cipher using encryption key from settings."""
    if not settings.encryption_key:
        raise RuntimeError("ENCRYPTION_KEY not set in environment")
    return Fernet(settings.encryption_key.encode())


def encrypt_api_key(api_key: str) -> str:
    """Encrypt an API key for storage."""
    if not api_key:
        return ""
    cipher = _get_cipher()
    encrypted = cipher.encrypt(api_key.encode())
    return encrypted.decode()


def decrypt_api_key(encrypted_key: str) -> str:
    """Decrypt an API key from storage."""
    if not encrypted_key:
        return ""
    cipher = _get_cipher()
    decrypted = cipher.decrypt(encrypted_key.encode())
    return decrypted.decode()


def mask_api_key(api_key: str) -> str:
    """Mask API key for safe display (show only last 6 characters)."""
    if not api_key or len(api_key) < 10:
        return "***"
    return f"{api_key[:3]}***...{api_key[-6:]}"

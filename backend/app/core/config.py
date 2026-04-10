"""
Application configuration loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings — loaded from .env file or environment."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./zktransact.db"

    # PII Hashing
    pii_hash_salt: str = "zktransact-default-salt-change-me"

    # CORS
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Fraud detection thresholds
    shared_device_threshold: int = 2       # Flag if device used by N+ accounts
    velocity_window_seconds: int = 3600    # 1 hour window
    velocity_threshold: int = 10           # Flag if N+ txns in window
    fan_out_threshold: int = 5             # Flag if account hits N+ merchants in window

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()

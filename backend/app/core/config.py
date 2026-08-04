"""
AgriNova AI — Core Configuration.

Loads all settings from environment variables via Pydantic Settings.
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from .env file."""

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Application ──
    APP_NAME: str = "AgriNova AI"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # ── Security ──
    SECRET_KEY: str = "change-me-to-a-random-64-char-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours

    # ── Database ──
    DATABASE_URL: str = "sqlite+aiosqlite:///./agrinova.db"

    # ── Redis ──
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── External APIs ──
    WEATHER_API_BASE_URL: str = "https://api.open-meteo.com"
    GEOCODING_API_URL: str = "https://geocoding-api.open-meteo.com"

    # ── File Storage ──
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE_MB: int = 10

    # ── ML Models ──
    ML_MODEL_DIR: str = "./ml/models"

    @property
    def is_sqlite(self) -> bool:
        """Check if we're using SQLite (for dev convenience)."""
        return "sqlite" in self.DATABASE_URL


settings = Settings()

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

    # ── AI Agronomist (V3) ──
    GEMINI_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-3.5-flash"
    
    # ── AI Provider Failover (Phase 9.5) ──
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL_NAME: str = ""
    AI_PRIMARY_PROVIDER: str = "gemini"
    AI_ENABLE_FALLBACK: bool = True


    # ── Rate Limiting ──
    AI_RATE_LIMIT_MAX_REQUESTS: int = 20
    AI_RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Global backstop rate limit
    AI_GLOBAL_RATE_LIMIT_MAX_REQUESTS: int = 200
    AI_GLOBAL_RATE_LIMIT_WINDOW_SECONDS: int = 60

    # ── AI Evaluation (Phase 10) ──
    EVAL_JUDGE_MODEL: str = "gemini-3.5-flash"
    AI_EVAL_MAX_ESTIMATED_COST: float = 2.0  # Max estimated cost in USD (or arbitrary units) for a test run

    # ── Market Data (V5) ──
    MARKET_DATA_API_KEY: str = ""
    MARKET_DATA_API_URL: str = "https://api.data.gov.in/resource"
    MARKET_DATA_RESOURCE_ID: str = ""  # data.gov.in resource UUID
    MARKET_DATA_PROVIDER: str = "demo"  # "data_gov_in" | "demo"
    MARKET_ALERT_THRESHOLD_PERCENT: float = 10.0  # Configurable price alert threshold

    # ── Email (V5) ──
    EMAIL_PROVIDER: str = "console"  # "brevo" | "sendgrid" | "console"
    EMAIL_API_KEY: str = ""
    EMAIL_FROM_ADDRESS: str = "alerts@agrinova.ai"
    EMAIL_FROM_NAME: str = "AgriNova AI"

    @property
    def is_sqlite(self) -> bool:
        """Check if we're using SQLite (for dev convenience)."""
        return "sqlite" in self.DATABASE_URL


settings = Settings()

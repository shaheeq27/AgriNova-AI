import pytest
from app.core.config import Settings
import os

def test_development_without_cors_retains_behavior():
    settings = Settings(APP_ENV="development", SECRET_KEY="change-me-to-a-random-64-char-string")
    assert settings.CORS_ORIGINS == "http://localhost:3000,http://localhost:3001"

def test_production_without_cors_fails_validation():
    with pytest.raises(ValueError) as exc:
        Settings(APP_ENV="production", SECRET_KEY="x" * 64, DEBUG=False, CORS_ORIGINS="http://localhost:3000,http://localhost:3001")
    assert "explicit CORS_ORIGINS environment variable is required" in str(exc.value)

def test_production_with_explicit_cors_succeeds():
    settings = Settings(APP_ENV="production", SECRET_KEY="x" * 64, DEBUG=False, CORS_ORIGINS="https://example.com")
    assert settings.CORS_ORIGINS == "https://example.com"

def test_multiple_comma_separated_production_origins():
    settings = Settings(APP_ENV="production", SECRET_KEY="x" * 64, DEBUG=False, CORS_ORIGINS="https://example.com,https://admin.example.com")
    assert settings.CORS_ORIGINS == "https://example.com,https://admin.example.com"

def test_no_wildcard_production_fallback():
    with pytest.raises(ValueError) as exc:
        Settings(APP_ENV="production", SECRET_KEY="x" * 64, DEBUG=False, CORS_ORIGINS="https://example.com, *")
    assert "Wildcard CORS origins are not allowed in production." in str(exc.value)


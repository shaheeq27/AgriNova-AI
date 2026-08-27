"""
AgriNova AI — Integration Configuration Validator (V5).

Validates that external integration credentials are present at startup
and logs clear warnings for missing optional configuration.  Never
hard-codes secrets — all values come from ``app.core.config.Settings``.

Called during application startup to surface configuration issues early.
"""

from __future__ import annotations

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def validate_integration_config() -> dict[str, bool]:
    """Validate all V5 integration configurations.

    Returns:
        Dict mapping integration name to readiness status.
        ``True`` = configured and ready, ``False`` = missing credentials.

    This function never raises.  Missing optional credentials are
    logged as warnings; the application continues with demo/fallback
    providers.
    """
    status: dict[str, bool] = {}

    # ── Market Data ──────────────────────────────────────────────────
    if settings.MARKET_DATA_PROVIDER == "data_gov_in":
        if settings.MARKET_DATA_API_KEY:
            logger.info("✓ Market data: data.gov.in configured")
            status["market_data"] = True
        else:
            logger.warning(
                "✗ Market data: MARKET_DATA_API_KEY is not set. "
                "data.gov.in provider will not work. "
                "Falling back to demo provider."
            )
            status["market_data"] = False
    elif settings.MARKET_DATA_PROVIDER == "demo":
        logger.info("✓ Market data: using demo provider (no credentials needed)")
        status["market_data"] = True
    else:
        logger.warning(
            "✗ Market data: unknown provider '%s'. "
            "Set MARKET_DATA_PROVIDER to 'data_gov_in' or 'demo'.",
            settings.MARKET_DATA_PROVIDER,
        )
        status["market_data"] = False

    # ── Email ────────────────────────────────────────────────────────
    if settings.EMAIL_PROVIDER == "brevo":
        if settings.EMAIL_API_KEY:
            logger.info("✓ Email: Brevo configured")
            status["email"] = True
        else:
            logger.warning(
                "✗ Email: EMAIL_API_KEY is not set. "
                "Brevo provider will not work. "
                "Falling back to console provider."
            )
            status["email"] = False
    elif settings.EMAIL_PROVIDER == "sendgrid":
        if settings.EMAIL_API_KEY:
            logger.info("✓ Email: SendGrid configured")
            status["email"] = True
        else:
            logger.warning(
                "✗ Email: EMAIL_API_KEY is not set. "
                "SendGrid provider will not work. "
                "Falling back to console provider."
            )
            status["email"] = False
    elif settings.EMAIL_PROVIDER == "console":
        logger.info("✓ Email: using console provider (dev mode, no credentials needed)")
        status["email"] = True
    else:
        logger.warning(
            "✗ Email: unknown provider '%s'. "
            "Set EMAIL_PROVIDER to 'brevo', 'sendgrid', or 'console'.",
            settings.EMAIL_PROVIDER,
        )
        status["email"] = False

    # ── Summary ──────────────────────────────────────────────────────
    ready_count = sum(1 for v in status.values() if v)
    total_count = len(status)
    logger.info(
        "Integration config: %d/%d integrations ready",
        ready_count,
        total_count,
    )

    return status

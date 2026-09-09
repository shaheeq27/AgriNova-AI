"""
AgriNova AI — Email Provider Factory (V5.2).

Instantiates the correct email provider based on environment config.
Mirrors the market provider factory pattern from V5.1.
"""

import logging

from app.core.config import settings
from app.integrations.email import BaseEmailProvider
from app.integrations.email.console import ConsoleEmailProvider

logger = logging.getLogger(__name__)


def get_email_provider() -> BaseEmailProvider:
    """Factory to get the configured email provider.

    Defaults to ConsoleEmailProvider if the configured provider fails
    to initialize (e.g., missing API key) to ensure email-dependent
    flows never crash the application.
    """
    provider_name = settings.EMAIL_PROVIDER.lower()

    if provider_name == "brevo":
        try:
            from app.integrations.email.brevo import BrevoEmailProvider
            return BrevoEmailProvider()
        except Exception as exc:
            logger.warning(
                "Failed to initialize BrevoEmailProvider: %s. "
                "Falling back to ConsoleEmailProvider.",
                exc,
            )
            return ConsoleEmailProvider()

    # Default to console for "console" or unknown
    return ConsoleEmailProvider()

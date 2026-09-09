"""
AgriNova AI — Brevo Email Provider (V5.2).

Transactional email delivery via Brevo (formerly Sendinblue) HTTP API v3.
Uses only the transactional SMTP endpoint — no marketing campaigns.

Free tier: 300 emails/day, unlimited contacts.
Docs: https://developers.brevo.com/reference/sendtransacemail

Requires:
  - EMAIL_API_KEY set to a valid Brevo API key
  - EMAIL_FROM_ADDRESS set to a verified sender address
"""

from __future__ import annotations

import logging
from typing import Any

from app.core.config import settings
from app.integrations.base import (
    IntegrationConfigError,
    IntegrationError,
    IntegrationTimeoutError,
)
from app.integrations.email import BaseEmailProvider, EmailMessage

logger = logging.getLogger(__name__)

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


class BrevoEmailProvider(BaseEmailProvider):
    """Send transactional emails via the Brevo HTTP API.

    Validates configuration on init so mis-configuration fails fast
    rather than silently dropping emails.
    """

    provider_name: str = "brevo"

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        if not settings.EMAIL_API_KEY:
            raise IntegrationConfigError(
                "EMAIL_API_KEY is required for the Brevo provider",
                provider="brevo",
            )
        self._api_key = settings.EMAIL_API_KEY
        self._from_email = settings.EMAIL_FROM_ADDRESS
        self._from_name = settings.EMAIL_FROM_NAME

    async def send_email(self, message: EmailMessage) -> str | None:
        """Send a transactional email via Brevo's SMTP API.

        Returns the Brevo messageId on success.
        """
        import httpx

        payload = {
            "sender": {
                "name": self._from_name,
                "email": self._from_email,
            },
            "to": [
                {
                    "email": message.to_email,
                    "name": message.to_name or message.to_email,
                }
            ],
            "subject": message.subject,
            "htmlContent": message.html_body,
        }

        if message.text_body:
            payload["textContent"] = message.text_body

        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "api-key": self._api_key,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    BREVO_API_URL,
                    json=payload,
                    headers=headers,
                )

            if response.status_code == 201:
                data = response.json()
                message_id = data.get("messageId")
                logger.info(
                    "[brevo] Email sent successfully to %s (id: %s)",
                    message.to_email,
                    message_id,
                )
                return message_id

            # Handle specific error codes
            if response.status_code == 401:
                raise IntegrationConfigError(
                    "Brevo API key is invalid or expired",
                    provider="brevo",
                )
            if response.status_code == 429:
                from app.integrations.base import IntegrationRateLimitError
                raise IntegrationRateLimitError(
                    "Brevo rate limit exceeded (300 emails/day on free tier)",
                    provider="brevo",
                )

            # General failure
            error_body = response.text[:500]
            raise IntegrationError(
                f"Brevo API returned {response.status_code}: {error_body}",
                provider="brevo",
                retriable=response.status_code >= 500,
            )

        except httpx.TimeoutException:
            raise IntegrationTimeoutError(
                "Brevo API request timed out after 15s",
                provider="brevo",
            )
        except httpx.RequestError as exc:
            raise IntegrationError(
                f"Network error calling Brevo API: {exc}",
                provider="brevo",
                retriable=True,
            )

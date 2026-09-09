"""
AgriNova AI — Base Email Provider (V5.2).

Abstract interface for email delivery services.  Inherits shared retry/error
handling from ``BaseIntegrationProvider``.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from app.integrations.base import BaseIntegrationProvider, IntegrationResult


@dataclass
class EmailMessage:
    """Provider-agnostic email payload.

    Created by the email service, consumed by providers.
    """

    to_email: str
    to_name: str | None = None
    subject: str = ""
    html_body: str = ""
    text_body: str | None = None  # Plain-text fallback
    category: str = "system"  # Maps to NotificationCategory
    template_name: str | None = None  # For audit logging


class BaseEmailProvider(BaseIntegrationProvider):
    """Abstract base class for email delivery providers.

    Concrete implementations:
      - ``ConsoleEmailProvider`` — logs to stdout (dev/test)
      - ``BrevoEmailProvider``   — Brevo (ex-Sendinblue) transactional API

    The provider sends a single email via ``send_email()`` and returns
    a provider-specific message ID on success.
    """

    provider_name: str = "base_email"

    @abstractmethod
    async def send_email(self, message: EmailMessage) -> str | None:
        """Send a single email.

        Args:
            message: The email content and recipient info.

        Returns:
            A provider-specific message ID if available, or ``None``.

        Raises:
            IntegrationError subclasses on failure.
        """
        ...

    async def execute(self, **kwargs: Any) -> IntegrationResult:
        """Bridge for ``execute_with_retry()`` compatibility.

        Delegates to ``send_email()`` and wraps the result.
        """
        message = kwargs.get("message")
        if not message or not isinstance(message, EmailMessage):
            return IntegrationResult.failure("No EmailMessage provided")

        try:
            message_id = await self.send_email(message)
            return IntegrationResult.success(data={"message_id": message_id})
        except Exception as exc:
            return IntegrationResult.failure(str(exc))

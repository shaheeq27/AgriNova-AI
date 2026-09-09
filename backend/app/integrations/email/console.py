"""
AgriNova AI — Console Email Provider (V5.2).

Development-only email provider that logs email content to stdout/logging
instead of sending real emails.  Default provider — no credentials required.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from app.integrations.email import BaseEmailProvider, EmailMessage

logger = logging.getLogger(__name__)


class ConsoleEmailProvider(BaseEmailProvider):
    """Logs emails to the console instead of sending them.

    Used in development and testing.  Produces a structured log entry
    that mimics a real delivery so that upstream services can exercise
    the full email pipeline without external dependencies.
    """

    provider_name: str = "console"

    async def send_email(self, message: EmailMessage) -> str | None:
        """Log the email to console and return a fake message ID."""
        fake_id = f"console-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"

        logger.info(
            "\n"
            "╔══════════════════════════════════════════════╗\n"
            "║         📧  CONSOLE EMAIL PROVIDER          ║\n"
            "╠══════════════════════════════════════════════╣\n"
            "║  To:       %-33s║\n"
            "║  Subject:  %-33s║\n"
            "║  Category: %-33s║\n"
            "║  Template: %-33s║\n"
            "║  ID:       %-33s║\n"
            "╠══════════════════════════════════════════════╣\n"
            "║  Body (first 200 chars):                    ║\n"
            "║  %-44s║\n"
            "╚══════════════════════════════════════════════╝",
            message.to_email,
            message.subject[:33],
            message.category,
            message.template_name or "(inline)",
            fake_id[:33],
            (message.text_body or message.html_body)[:44],
        )

        return fake_id

"""
AgriNova AI — Email Service (V5.2).

Orchestrates email delivery: checks preferences, renders templates,
dispatches through the configured provider, and logs every attempt.

This service is called BY the NotificationService when a notification
qualifies for email delivery — it does NOT replace the in-app flow.

Flow:
  Event → NotificationService
          ├── In-App (always, via NotificationRepository)
          └── EmailService.maybe_send_email() (only if applicable + enabled + opted in)
              ├── Check NotificationPreference
              ├── Render template via TemplateEngine
              ├── Dispatch via email provider
              └── Log to EmailLog (success or failure)
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.integrations.email import EmailMessage
from app.integrations.email.factory import get_email_provider
from app.integrations.email.template_engine import TemplateEngine
from app.models.email_log import EmailLog
from app.models.notification_preference import NotificationPreference
from app.models.user import User

logger = logging.getLogger(__name__)

# ── Notification type → email category/template mapping ──────────────
# Only notification types listed here are eligible for email.
# This is the gatekeeper: if a notification type is NOT in this map,
# no email is even attempted.

EMAIL_ELIGIBLE_TYPES: dict[str, dict] = {
    "weather_alert": {
        "category": "weather",
        "preference_key": "weather_alerts",
        "template": "weather_alert",
        "subject_prefix": "⚠️ Weather Alert",
    },
    "irrigation_reminder": {
        "category": "irrigation",
        "preference_key": "irrigation_reminders",
        "template": "irrigation_reminder",
        "subject_prefix": "💧 Irrigation Reminder",
    },
    "fertilizer_reminder": {
        "category": "fertilizer",
        "preference_key": "fertilizer_reminders",
        "template": "fertilizer_reminder",
        "subject_prefix": "🌿 Fertilizer Reminder",
    },
    "market_alert": {
        "category": "market",
        "preference_key": "market_alerts",
        "template": "market_alert",
        "subject_prefix": "📊 Market Price Alert",
    },
    "ai_recommendation": {
        "category": "ai",
        "preference_key": "ai_insights",
        "template": "ai_recommendation",
        "subject_prefix": "🤖 AI Recommendation",
    },
}


class EmailService:
    """Orchestrates email delivery with preference checking and audit logging.

    Usage::

        email_service = EmailService(db)
        await email_service.maybe_send_email(
            user_id="abc",
            notification_type="weather_alert",
            title="Extreme temperature",
            message="Temperature is 42°C at your farm",
            template_data={"farm_name": "My Farm", "temperature": 42, ...}
        )
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self._provider = get_email_provider()
        self._template_engine = TemplateEngine()

    async def maybe_send_email(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        template_data: dict | None = None,
    ) -> bool:
        """Conditionally send an email for a notification.

        Returns True if an email was sent, False if skipped or failed.
        This method NEVER raises — failures are logged and returned as False.
        """
        try:
            return await self._do_send(
                user_id, notification_type, title, message, template_data or {}
            )
        except Exception as exc:
            logger.error(
                "Unexpected error in EmailService.maybe_send_email for user %s: %s",
                user_id,
                exc,
                exc_info=True,
            )
            return False

    async def send_welcome_email(self, user_id: str, user_name: str, user_email: str) -> bool:
        """Send the welcome email to a newly registered user.

        Welcome emails bypass preference checks (the user just signed up).
        """
        try:
            html = self._template_engine.render_html(
                "welcome", user_name=user_name
            )
            text = self._template_engine.render_text(
                "welcome", user_name=user_name
            )

            msg = EmailMessage(
                to_email=user_email,
                to_name=user_name,
                subject=f"Welcome to {settings.APP_NAME}! 🌱",
                html_body=html,
                text_body=text,
                category="system",
                template_name="welcome",
            )

            result = await self._provider.execute_with_retry(message=msg)

            await self._log_email(
                user_id=user_id,
                recipient_email=user_email,
                subject=msg.subject,
                template_name="welcome",
                category="system",
                status="sent" if result.is_success else "failed",
                provider=self._provider.provider_name,
                provider_message_id=result.data.get("message_id") if result.is_success and result.data else None,
                error_message=result.error if not result.is_success else None,
            )

            return result.is_success

        except Exception as exc:
            logger.error("Failed to send welcome email to %s: %s", user_id, exc, exc_info=True)
            return False

    async def _do_send(
        self,
        user_id: str,
        notification_type: str,
        title: str,
        message: str,
        template_data: dict,
    ) -> bool:
        """Internal: the actual send logic with preference checking."""

        # 1. Is this notification type eligible for email at all?
        type_config = EMAIL_ELIGIBLE_TYPES.get(notification_type)
        if not type_config:
            logger.debug(
                "Notification type '%s' is not email-eligible, skipping",
                notification_type,
            )
            return False

        # 2. Get the user's email address
        user = await self._get_user(user_id)
        if not user or not user.email:
            logger.debug("No user or email for user_id=%s, skipping email", user_id)
            return False

        # 3. Check preferences — is email enabled AND is this category opted in?
        prefs = await self._get_preferences(user_id)

        # Master email toggle
        if prefs and not prefs.email_enabled:
            logger.debug("Email disabled for user %s, skipping", user_id)
            return False

        # Category-specific toggle
        preference_key = type_config["preference_key"]
        if prefs and not getattr(prefs, preference_key, True):
            logger.debug(
                "Category '%s' opted out by user %s, skipping email",
                preference_key,
                user_id,
            )
            return False

        # 4. Render template
        template_name = type_config["template"]
        template_data.setdefault("title", title)
        template_data.setdefault("message", message)

        html = self._template_engine.render_html(template_name, **template_data)
        text = self._template_engine.render_text(template_name, **template_data)

        # 5. Build subject
        subject = f"{type_config['subject_prefix']}: {title}"

        # 6. Send via provider
        msg = EmailMessage(
            to_email=user.email,
            to_name=user.full_name,
            subject=subject,
            html_body=html,
            text_body=text,
            category=type_config["category"],
            template_name=template_name,
        )

        result = await self._provider.execute_with_retry(message=msg)

        # 7. Audit log
        await self._log_email(
            user_id=user_id,
            recipient_email=user.email,
            subject=subject,
            template_name=template_name,
            category=type_config["category"],
            status="sent" if result.is_success else "failed",
            provider=self._provider.provider_name,
            provider_message_id=(
                result.data.get("message_id")
                if result.is_success and result.data
                else None
            ),
            error_message=result.error if not result.is_success else None,
        )

        if result.is_success:
            logger.info(
                "Email sent for '%s' to user %s (%s)",
                notification_type,
                user_id,
                user.email,
            )
        else:
            logger.warning(
                "Email delivery failed for '%s' to user %s: %s",
                notification_type,
                user_id,
                result.error,
            )

        return result.is_success

    async def _get_user(self, user_id: str) -> User | None:
        """Fetch user by ID."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def _get_preferences(self, user_id: str) -> NotificationPreference | None:
        """Fetch user notification preferences.

        Returns None if no preferences row exists, which means
        all defaults apply (everything enabled).
        """
        result = await self.db.execute(
            select(NotificationPreference).where(
                NotificationPreference.user_id == user_id
            )
        )
        return result.scalar_one_or_none()

    async def _log_email(self, **kwargs) -> None:
        """Create an EmailLog audit entry."""
        try:
            log = EmailLog(**kwargs)
            if kwargs.get("status") == "sent":
                log.sent_at = datetime.now(timezone.utc)
            self.db.add(log)
            await self.db.flush()  # flush not commit — let the caller commit
        except Exception as exc:
            logger.error("Failed to create EmailLog: %s", exc, exc_info=True)

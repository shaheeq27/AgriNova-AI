"""
AgriNova AI — V5.2 Step 2 Tests.

Tests for:
  1. Each email template renders correctly
  2. Preference enforcement (master toggle, per-category toggle)
  3. EmailService delivery flow
  4. EmailLog creation on success and failure
  5. Provider failure handling (no crash propagation)
  6. NotificationService → email integration
  7. Existing in-app notifications remain functional
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.database import Base

@pytest.fixture(autouse=True)
def force_console_email_provider(monkeypatch):
    """Ensure all email orchestration tests use the safe ConsoleEmailProvider."""
    monkeypatch.setattr("app.core.config.settings.EMAIL_PROVIDER", "console")

# Models
from app.models.user import User
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference
from app.models.email_log import EmailLog

# Services
from app.services.email_service import EmailService, EMAIL_ELIGIBLE_TYPES
from app.services.notification_service import NotificationService

# Email infrastructure
from app.integrations.email import EmailMessage
from app.integrations.email.console import ConsoleEmailProvider
from app.integrations.email.template_engine import TemplateEngine
from app.integrations.base import IntegrationResult, IntegrationStatus

pytestmark = pytest.mark.asyncio


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
async def db():
    """In-memory SQLite with all tables."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session


@pytest.fixture
async def user(db):
    """Create a test user."""
    u = User(
        email="farmer@example.com",
        full_name="Test Farmer",
        hashed_password="fakehash",
    )
    db.add(u)
    await db.commit()
    await db.refresh(u)
    return u


@pytest.fixture
async def user_with_email_disabled(db, user):
    """Create a user with email master toggle OFF."""
    pref = NotificationPreference(
        user_id=user.id,
        email_enabled=False,
    )
    db.add(pref)
    await db.commit()
    return user


@pytest.fixture
async def user_with_market_disabled(db, user):
    """Create a user with market_alerts specifically OFF."""
    pref = NotificationPreference(
        user_id=user.id,
        email_enabled=True,
        market_alerts=False,
    )
    db.add(pref)
    await db.commit()
    return user


@pytest.fixture
def template_engine():
    """TemplateEngine using the real templates directory."""
    return TemplateEngine()


# ═══════════════════════════════════════════════════════════════════════
# 1. Template Rendering Tests
# ═══════════════════════════════════════════════════════════════════════


class TestEmailTemplates:
    """Verify each email template renders with expected content."""

    def test_base_template_vars(self, template_engine):
        """Base template globals are available."""
        assert template_engine.env.globals["app_name"] == "AgriNova AI"

    def test_weather_alert_template(self, template_engine):
        html = template_engine.render_html(
            "weather_alert",
            farm_name="Green Acres",
            severity="critical",
            condition="Extreme Temperature",
            temperature=42,
            humidity=25,
        )
        assert "Weather Alert" in html
        assert "Green Acres" in html
        assert "42°C" in html
        assert "25%" in html
        assert "CRITICAL" in html

    def test_irrigation_reminder_template(self, template_engine):
        html = template_engine.render_html(
            "irrigation_reminder",
            task_title="Water wheat field",
            crop_name="Wheat",
            farm_name="Sunrise Farm",
        )
        assert "Irrigation Due" in html
        assert "Water wheat field" in html
        assert "Wheat" in html
        assert "Sunrise Farm" in html

    def test_fertilizer_reminder_template(self, template_engine):
        html = template_engine.render_html(
            "fertilizer_reminder",
            task_title="Apply DAP to rice",
            crop_name="Rice",
        )
        assert "Fertilizer" in html
        assert "Apply DAP to rice" in html
        assert "Rice" in html

    def test_market_alert_template(self, template_engine):
        html = template_engine.render_html(
            "market_alert",
            commodity="Tomato",
            market_name="Azadpur Mandi",
            modal_price=2500,
            price_change_pct=12.5,
            min_price=2000,
            max_price=3000,
        )
        assert "Market Price Alert" in html
        assert "Tomato" in html
        assert "Azadpur Mandi" in html
        assert "₹2500" in html
        assert "12.5%" in html
        assert "₹2000" in html
        assert "₹3000" in html

    def test_market_alert_negative_change(self, template_engine):
        html = template_engine.render_html(
            "market_alert",
            commodity="Rice",
            market_name="Vashi APMC",
            modal_price=1800,
            price_change_pct=-8.3,
        )
        assert "↓" in html
        assert "8.3%" in html

    def test_ai_recommendation_template(self, template_engine):
        html = template_engine.render_html(
            "ai_recommendation",
            recommendation_title="Pest Prevention",
            recommendation_text="Apply neem oil spray to prevent whitefly infestation.",
            crop_name="Cotton",
            farm_name="Valley Farm",
        )
        assert "AI Recommendation" in html
        assert "Pest Prevention" in html
        assert "neem oil" in html
        assert "Cotton" in html

    def test_welcome_template(self, template_engine):
        html = template_engine.render_html(
            "welcome",
            user_name="Ravi Kumar",
        )
        assert "Welcome" in html
        assert "Ravi Kumar" in html
        assert "Getting Started" in html
        assert "AI agronomist" in html

    def test_all_templates_extend_base(self, template_engine):
        """All templates should include the base footer."""
        for name in ["weather_alert", "irrigation_reminder", "fertilizer_reminder",
                      "market_alert", "ai_recommendation", "welcome"]:
            html = template_engine.render_html(name, **self._min_context(name))
            assert "AgriNova AI" in html
            assert "Manage notification preferences" in html

    @staticmethod
    def _min_context(template_name: str) -> dict:
        """Minimal template data for each template."""
        return {
            "weather_alert": {"farm_name": "F", "severity": "info", "condition": "C"},
            "irrigation_reminder": {"task_title": "T"},
            "fertilizer_reminder": {"task_title": "T"},
            "market_alert": {"commodity": "C", "market_name": "M", "modal_price": 0, "price_change_pct": 0},
            "ai_recommendation": {"recommendation_text": "R"},
            "welcome": {"user_name": "U"},
        }.get(template_name, {})


# ═══════════════════════════════════════════════════════════════════════
# 2. Preference Enforcement Tests
# ═══════════════════════════════════════════════════════════════════════


class TestPreferenceEnforcement:
    """Verify EmailService respects NotificationPreference."""

    async def test_email_skipped_when_master_toggle_off(self, db, user_with_email_disabled):
        """No email sent when email_enabled=False."""
        service = EmailService(db)
        result = await service.maybe_send_email(
            user_id=user_with_email_disabled.id,
            notification_type="weather_alert",
            title="Test",
            message="Test message",
            template_data={"farm_name": "F", "severity": "info", "condition": "C"},
        )
        assert result is False

        # Verify no EmailLog was created
        logs = await db.execute(
            select(EmailLog).where(EmailLog.user_id == user_with_email_disabled.id)
        )
        assert logs.scalars().first() is None

    async def test_email_skipped_when_category_off(self, db, user_with_market_disabled):
        """No email when the specific category is opted out."""
        service = EmailService(db)
        result = await service.maybe_send_email(
            user_id=user_with_market_disabled.id,
            notification_type="market_alert",
            title="Tomato up 15%",
            message="Price change",
            template_data={"commodity": "Tomato", "market_name": "M", "modal_price": 100},
        )
        assert result is False

    async def test_email_sent_when_all_enabled(self, db, user):
        """Email IS sent when no preference row exists (all defaults = on)."""
        service = EmailService(db)
        result = await service.maybe_send_email(
            user_id=user.id,
            notification_type="weather_alert",
            title="Extreme heat",
            message="42°C detected",
            template_data={"farm_name": "F", "severity": "critical", "condition": "Heat"},
        )
        assert result is True

    async def test_non_eligible_type_skipped(self, db, user):
        """Notification types NOT in EMAIL_ELIGIBLE_TYPES get no email."""
        service = EmailService(db)
        result = await service.maybe_send_email(
            user_id=user.id,
            notification_type="task_overdue",
            title="Overdue task",
            message="You have an overdue task",
        )
        assert result is False

    async def test_harvest_reminder_not_eligible(self, db, user):
        """harvest_reminder is NOT email-eligible."""
        service = EmailService(db)
        result = await service.maybe_send_email(
            user_id=user.id,
            notification_type="harvest_reminder",
            title="Harvest ready",
            message="Crop ready",
        )
        assert result is False


# ═══════════════════════════════════════════════════════════════════════
# 3. EmailService Delivery Tests
# ═══════════════════════════════════════════════════════════════════════


class TestEmailServiceDelivery:
    """Verify EmailService dispatches correctly."""

    async def test_send_weather_alert_email(self, db, user):
        """Full flow: weather alert → template → provider → log."""
        service = EmailService(db)
        result = await service.maybe_send_email(
            user_id=user.id,
            notification_type="weather_alert",
            title="Heat Wave",
            message="Temp above 40°C",
            template_data={
                "farm_name": "Valley Farm",
                "severity": "critical",
                "condition": "Extreme Heat",
                "temperature": 42,
            },
        )
        assert result is True

    async def test_send_market_alert_email(self, db, user):
        """Full flow: market alert → template → provider → log."""
        service = EmailService(db)
        result = await service.maybe_send_email(
            user_id=user.id,
            notification_type="market_alert",
            title="Tomato up 15%",
            message="Price change",
            template_data={
                "commodity": "Tomato",
                "market_name": "Azadpur Mandi",
                "modal_price": 2500,
                "price_change_pct": 15.0,
            },
        )
        assert result is True

    async def test_welcome_email(self, db, user):
        """Welcome email bypasses preference checks."""
        service = EmailService(db)
        result = await service.send_welcome_email(
            user_id=user.id,
            user_name="Test Farmer",
            user_email="farmer@example.com",
        )
        assert result is True


# ═══════════════════════════════════════════════════════════════════════
# 4. EmailLog Creation Tests
# ═══════════════════════════════════════════════════════════════════════


class TestEmailLogCreation:
    """Verify EmailLog entries are created for success and failure."""

    async def test_log_created_on_success(self, db, user):
        """Successful email creates a 'sent' log entry."""
        service = EmailService(db)
        await service.maybe_send_email(
            user_id=user.id,
            notification_type="weather_alert",
            title="Alert",
            message="Msg",
            template_data={"farm_name": "F", "severity": "info", "condition": "C"},
        )
        await db.commit()

        logs = await db.execute(
            select(EmailLog).where(EmailLog.user_id == user.id)
        )
        log = logs.scalars().first()
        assert log is not None
        assert log.status == "sent"
        assert log.provider == "console"
        assert log.template_name == "weather_alert"
        assert log.category == "weather"
        assert log.provider_message_id is not None
        assert log.provider_message_id.startswith("console-")
        assert log.sent_at is not None
        assert log.error_message is None

    async def test_log_created_on_failure(self, db, user):
        """Failed email creates a 'failed' log entry with error message."""
        service = EmailService(db)

        # Mock the provider to fail
        mock_provider = AsyncMock(spec=ConsoleEmailProvider)
        mock_provider.provider_name = "mock"
        mock_provider.execute_with_retry = AsyncMock(
            return_value=IntegrationResult(
                status=IntegrationStatus.FAILURE,
                error="Mock provider failure",
            )
        )
        service._provider = mock_provider

        await service.maybe_send_email(
            user_id=user.id,
            notification_type="irrigation_reminder",
            title="Irrigate",
            message="Task due",
            template_data={"task_title": "Water wheat"},
        )
        await db.commit()

        logs = await db.execute(
            select(EmailLog).where(EmailLog.user_id == user.id)
        )
        log = logs.scalars().first()
        assert log is not None
        assert log.status == "failed"
        assert log.error_message == "Mock provider failure"
        assert log.sent_at is None

    async def test_welcome_email_creates_log(self, db, user):
        """Welcome email also creates an audit log."""
        service = EmailService(db)
        await service.send_welcome_email(
            user_id=user.id,
            user_name="Test",
            user_email="farmer@example.com",
        )
        await db.commit()

        logs = await db.execute(
            select(EmailLog).where(
                EmailLog.user_id == user.id,
                EmailLog.template_name == "welcome",
            )
        )
        log = logs.scalars().first()
        assert log is not None
        assert log.status == "sent"
        assert log.category == "system"


# ═══════════════════════════════════════════════════════════════════════
# 5. Provider Failure Handling
# ═══════════════════════════════════════════════════════════════════════


class TestProviderFailureHandling:
    """Verify email failures never crash the notification flow."""

    async def test_provider_exception_returns_false(self, db, user):
        """Provider throwing an exception returns False, not a crash."""
        service = EmailService(db)

        mock_provider = AsyncMock(spec=ConsoleEmailProvider)
        mock_provider.provider_name = "crash_test"
        mock_provider.execute_with_retry = AsyncMock(
            side_effect=RuntimeError("Provider exploded")
        )
        service._provider = mock_provider

        result = await service.maybe_send_email(
            user_id=user.id,
            notification_type="weather_alert",
            title="Test",
            message="Test",
            template_data={"farm_name": "F", "severity": "info", "condition": "C"},
        )
        # Should return False, not raise
        assert result is False

    async def test_template_failure_uses_fallback(self, db, user):
        """Missing template still sends via fallback HTML."""
        service = EmailService(db)

        # Manually inject a fake eligible type pointing to a nonexistent template
        with patch.dict(EMAIL_ELIGIBLE_TYPES, {
            "test_type": {
                "category": "system",
                "preference_key": "weather_alerts",
                "template": "nonexistent_template_xyz",
                "subject_prefix": "Test",
            }
        }):
            result = await service.maybe_send_email(
                user_id=user.id,
                notification_type="test_type",
                title="Fallback test",
                message="Should use fallback HTML",
            )
            assert result is True  # Fallback HTML still gets sent

    async def test_nonexistent_user_returns_false(self, db):
        """Email for a nonexistent user_id returns False gracefully."""
        service = EmailService(db)
        result = await service.maybe_send_email(
            user_id="nonexistent-uuid-12345",
            notification_type="weather_alert",
            title="Test",
            message="Test",
        )
        assert result is False


# ═══════════════════════════════════════════════════════════════════════
# 6. NotificationService → Email Integration
# ═══════════════════════════════════════════════════════════════════════


class TestNotificationEmailIntegration:
    """Verify NotificationService calls EmailService correctly."""

    async def test_create_market_alert_creates_both(self, db, user):
        """create_market_alert creates in-app notification AND email log."""
        svc = NotificationService()
        result = await svc.create_market_alert(
            db=db,
            user_id=user.id,
            commodity="Tomato",
            market_name="Azadpur Mandi",
            modal_price=2500,
            price_change_pct=15.0,
            min_price=2000,
            max_price=3000,
        )

        # In-app notification created
        assert result is not None
        assert result["type"] == "market_alert"
        assert "Tomato" in result["title"]

        # Check the Notification model directly
        notifs = await db.execute(
            select(Notification).where(Notification.user_id == user.id)
        )
        notif = notifs.scalars().first()
        assert notif is not None
        assert notif.type == "market_alert"

        # Email log created
        await db.commit()
        logs = await db.execute(
            select(EmailLog).where(EmailLog.user_id == user.id)
        )
        log = logs.scalars().first()
        assert log is not None
        assert log.template_name == "market_alert"
        assert log.status == "sent"

    async def test_market_alert_dedup(self, db, user):
        """Duplicate market alerts for the same commodity+market+day are skipped."""
        svc = NotificationService()

        result1 = await svc.create_market_alert(
            db=db, user_id=user.id,
            commodity="Rice", market_name="Vashi",
            modal_price=1800, price_change_pct=12.0,
        )
        result2 = await svc.create_market_alert(
            db=db, user_id=user.id,
            commodity="Rice", market_name="Vashi",
            modal_price=1850, price_change_pct=14.0,
        )

        assert result1 is not None
        assert result2 is None  # Deduped

    async def test_market_alert_respects_email_prefs(self, db, user_with_market_disabled):
        """Market alert creates in-app but skips email when market_alerts=False."""
        svc = NotificationService()
        result = await svc.create_market_alert(
            db=db,
            user_id=user_with_market_disabled.id,
            commodity="Wheat",
            market_name="Indore Mandi",
            modal_price=2200,
            price_change_pct=11.0,
        )

        # In-app notification IS created
        assert result is not None
        assert result["type"] == "market_alert"

        # Email log should NOT be created (category opted out)
        await db.commit()
        logs = await db.execute(
            select(EmailLog).where(
                EmailLog.user_id == user_with_market_disabled.id
            )
        )
        assert logs.scalars().first() is None


# ═══════════════════════════════════════════════════════════════════════
# 7. Existing In-App Notifications Remain Functional
# ═══════════════════════════════════════════════════════════════════════


class TestInAppNotificationsUnchanged:
    """Verify existing in-app notification methods still work."""

    async def test_get_notifications_returns_list(self, db, user):
        svc = NotificationService()
        items = await svc.get_notifications(db, user.id)
        assert isinstance(items, list)

    async def test_get_unread_count_returns_int(self, db, user):
        svc = NotificationService()
        count = await svc.get_unread_count(db, user.id)
        assert isinstance(count, int)
        assert count == 0

    async def test_mark_read_nonexistent_returns_none(self, db, user):
        svc = NotificationService()
        result = await svc.mark_read(db, "nonexistent-id", user.id)
        assert result is None

    async def test_mark_all_read(self, db, user):
        svc = NotificationService()
        updated = await svc.mark_all_read(db, user.id)
        assert isinstance(updated, int)

    async def test_notification_types_map_is_selective(self):
        """EMAIL_ELIGIBLE_TYPES does NOT include task_overdue or harvest_reminder."""
        assert "task_overdue" not in EMAIL_ELIGIBLE_TYPES
        assert "harvest_reminder" not in EMAIL_ELIGIBLE_TYPES
        # These ARE eligible:
        assert "weather_alert" in EMAIL_ELIGIBLE_TYPES
        assert "irrigation_reminder" in EMAIL_ELIGIBLE_TYPES
        assert "fertilizer_reminder" in EMAIL_ELIGIBLE_TYPES
        assert "market_alert" in EMAIL_ELIGIBLE_TYPES
        assert "ai_recommendation" in EMAIL_ELIGIBLE_TYPES

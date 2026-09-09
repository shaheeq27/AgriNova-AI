"""
AgriNova AI — V5.2 Email Foundation Tests.

Tests for:
  1. NotificationPreference and EmailLog model creation/schema
  2. Email provider factory selection
  3. ConsoleEmailProvider behavior
  4. BrevoEmailProvider configuration validation and error handling
  5. TemplateEngine initialization, rendering, and fallback
"""

import pytest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import AsyncMock, patch, MagicMock

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, inspect

from app.core.database import Base

# Models
from app.models.notification_preference import NotificationPreference
from app.models.email_log import EmailLog

# Email providers
from app.integrations.email import BaseEmailProvider, EmailMessage
from app.integrations.email.console import ConsoleEmailProvider
from app.integrations.email.brevo import BrevoEmailProvider
from app.integrations.email.factory import get_email_provider
from app.integrations.email.template_engine import TemplateEngine

# Integration base
from app.integrations.base import IntegrationConfigError

pytestmark = pytest.mark.asyncio


# ── Fixtures ─────────────────────────────────────────────────────────────────


@pytest.fixture
async def db():
    """Create in-memory SQLite database with all models."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session, engine


@pytest.fixture
def tmp_templates(tmp_path):
    """Create a temporary templates directory with test templates."""
    templates_dir = tmp_path / "templates"
    templates_dir.mkdir()

    # Create a simple HTML template
    (templates_dir / "test_email.html").write_text(
        "<html><body><h1>Hello {{ name }}!</h1><p>{{ message }}</p></body></html>"
    )

    # Create a plain-text template
    (templates_dir / "test_email.txt").write_text(
        "Hello {{ name }}!\n\n{{ message }}"
    )

    # Create an HTML-only template (no .txt counterpart)
    (templates_dir / "html_only.html").write_text(
        "<html><body><p>{{ content }}</p></body></html>"
    )

    return templates_dir


# ═══════════════════════════════════════════════════════════════════════
# 1. Model Creation & Schema Tests
# ═══════════════════════════════════════════════════════════════════════


async def test_notification_preference_table_created(db):
    """NotificationPreference table is created via Base.metadata.create_all()."""
    session, engine = db
    async with engine.connect() as conn:
        table_names = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
    assert "notification_preferences" in table_names


async def test_email_log_table_created(db):
    """EmailLog table is created via Base.metadata.create_all()."""
    session, engine = db
    async with engine.connect() as conn:
        table_names = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_table_names()
        )
    assert "email_logs" in table_names


async def test_notification_preference_defaults(db):
    """All preference toggles default to True."""
    session, _ = db

    # Create a minimal user for FK
    from app.models.user import User
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="fakehash",
    )
    session.add(user)
    await session.flush()

    pref = NotificationPreference(user_id=user.id)
    session.add(pref)
    await session.commit()

    result = await session.execute(
        select(NotificationPreference).where(
            NotificationPreference.user_id == user.id
        )
    )
    loaded = result.scalar_one()

    assert loaded.email_enabled is True
    assert loaded.in_app_enabled is True
    assert loaded.weather_alerts is True
    assert loaded.irrigation_reminders is True
    assert loaded.fertilizer_reminders is True
    assert loaded.market_alerts is True
    assert loaded.ai_insights is True
    assert loaded.created_at is not None
    assert loaded.updated_at is not None


async def test_email_log_creation(db):
    """EmailLog can be created with all required fields."""
    session, _ = db

    from app.models.user import User
    user = User(
        email="farmer@example.com",
        full_name="Farmer",
        hashed_password="fakehash",
    )
    session.add(user)
    await session.flush()

    log = EmailLog(
        user_id=user.id,
        recipient_email="farmer@example.com",
        subject="Price Alert: Tomato",
        template_name="market_alert",
        category="market",
        status="sent",
        provider="console",
        provider_message_id="console-12345",
    )
    session.add(log)
    await session.commit()

    result = await session.execute(
        select(EmailLog).where(EmailLog.user_id == user.id)
    )
    loaded = result.scalar_one()

    assert loaded.recipient_email == "farmer@example.com"
    assert loaded.subject == "Price Alert: Tomato"
    assert loaded.template_name == "market_alert"
    assert loaded.category == "market"
    assert loaded.status == "sent"
    assert loaded.provider == "console"
    assert loaded.provider_message_id == "console-12345"
    assert loaded.error_message is None
    assert loaded.created_at is not None


async def test_email_log_defaults(db):
    """EmailLog defaults are applied correctly."""
    session, _ = db

    from app.models.user import User
    user = User(
        email="default@example.com",
        full_name="Default User",
        hashed_password="fakehash",
    )
    session.add(user)
    await session.flush()

    log = EmailLog(
        user_id=user.id,
        recipient_email="default@example.com",
        subject="Test",
    )
    session.add(log)
    await session.commit()

    result = await session.execute(
        select(EmailLog).where(EmailLog.user_id == user.id)
    )
    loaded = result.scalar_one()

    assert loaded.status == "pending"
    assert loaded.provider == "console"
    assert loaded.category == "system"
    assert loaded.sent_at is None


# ═══════════════════════════════════════════════════════════════════════
# 2. Provider Factory Tests
# ═══════════════════════════════════════════════════════════════════════


def test_factory_default_returns_console():
    """Default EMAIL_PROVIDER=console returns ConsoleEmailProvider."""
    with patch("app.integrations.email.factory.settings") as mock_settings:
        mock_settings.EMAIL_PROVIDER = "console"
        provider = get_email_provider()
        assert isinstance(provider, ConsoleEmailProvider)
        assert provider.provider_name == "console"


def test_factory_unknown_returns_console():
    """Unknown provider name falls back to ConsoleEmailProvider."""
    with patch("app.integrations.email.factory.settings") as mock_settings:
        mock_settings.EMAIL_PROVIDER = "unknown_provider"
        provider = get_email_provider()
        assert isinstance(provider, ConsoleEmailProvider)


def test_factory_brevo_without_key_falls_back():
    """Brevo without EMAIL_API_KEY falls back to ConsoleEmailProvider."""
    with patch("app.integrations.email.factory.settings") as mock_settings:
        mock_settings.EMAIL_PROVIDER = "brevo"
        mock_settings.EMAIL_API_KEY = ""
        mock_settings.EMAIL_FROM_ADDRESS = "test@test.com"
        mock_settings.EMAIL_FROM_NAME = "Test"
        provider = get_email_provider()
        assert isinstance(provider, ConsoleEmailProvider)


def test_factory_brevo_with_key_returns_brevo():
    """Brevo with valid config returns BrevoEmailProvider."""
    with patch("app.integrations.email.factory.settings") as mock_factory_settings, \
         patch("app.integrations.email.brevo.settings") as mock_brevo_settings:
        for mock_s in (mock_factory_settings, mock_brevo_settings):
            mock_s.EMAIL_PROVIDER = "brevo"
            mock_s.EMAIL_API_KEY = "xkeysib-test-key"
            mock_s.EMAIL_FROM_ADDRESS = "alerts@agrinova.ai"
            mock_s.EMAIL_FROM_NAME = "AgriNova AI"
        provider = get_email_provider()
        assert isinstance(provider, BrevoEmailProvider)
        assert provider.provider_name == "brevo"


# ═══════════════════════════════════════════════════════════════════════
# 3. ConsoleEmailProvider Tests
# ═══════════════════════════════════════════════════════════════════════


async def test_console_provider_returns_message_id():
    """ConsoleEmailProvider returns a fake message ID starting with 'console-'."""
    provider = ConsoleEmailProvider()
    msg = EmailMessage(
        to_email="farmer@example.com",
        subject="Test Subject",
        html_body="<p>Hello!</p>",
        category="market",
    )
    result = await provider.send_email(msg)
    assert result is not None
    assert result.startswith("console-")


async def test_console_provider_execute_with_retry():
    """ConsoleEmailProvider works through the execute_with_retry pipeline."""
    provider = ConsoleEmailProvider()
    msg = EmailMessage(
        to_email="farmer@example.com",
        subject="Retry Test",
        html_body="<p>Body</p>",
    )
    result = await provider.execute_with_retry(message=msg)
    assert result.is_success
    assert result.data["message_id"].startswith("console-")


async def test_console_provider_is_base_email_provider():
    """ConsoleEmailProvider inherits from BaseEmailProvider."""
    provider = ConsoleEmailProvider()
    assert isinstance(provider, BaseEmailProvider)


# ═══════════════════════════════════════════════════════════════════════
# 4. BrevoEmailProvider Tests
# ═══════════════════════════════════════════════════════════════════════


def test_brevo_requires_api_key():
    """BrevoEmailProvider raises IntegrationConfigError without an API key."""
    with patch("app.integrations.email.brevo.settings") as mock_settings:
        mock_settings.EMAIL_API_KEY = ""
        mock_settings.EMAIL_FROM_ADDRESS = "test@test.com"
        mock_settings.EMAIL_FROM_NAME = "Test"
        with pytest.raises(IntegrationConfigError, match="EMAIL_API_KEY"):
            BrevoEmailProvider()


def test_brevo_initializes_with_key():
    """BrevoEmailProvider initializes when EMAIL_API_KEY is set."""
    with patch("app.integrations.email.brevo.settings") as mock_settings:
        mock_settings.EMAIL_API_KEY = "xkeysib-valid-key"
        mock_settings.EMAIL_FROM_ADDRESS = "alerts@agrinova.ai"
        mock_settings.EMAIL_FROM_NAME = "AgriNova AI"
        provider = BrevoEmailProvider()
        assert provider.provider_name == "brevo"
        assert provider._api_key == "xkeysib-valid-key"


async def test_brevo_send_success():
    """BrevoEmailProvider returns messageId on 201 response."""
    with patch("app.integrations.email.brevo.settings") as mock_settings:
        mock_settings.EMAIL_API_KEY = "xkeysib-test"
        mock_settings.EMAIL_FROM_ADDRESS = "alerts@agrinova.ai"
        mock_settings.EMAIL_FROM_NAME = "AgriNova AI"
        provider = BrevoEmailProvider()

    mock_response = MagicMock()
    mock_response.status_code = 201
    mock_response.json.return_value = {"messageId": "<brevo-msg-123>"}

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client_instance

        msg = EmailMessage(
            to_email="farmer@example.com",
            subject="Price Alert",
            html_body="<p>Tomato prices up!</p>",
        )
        result = await provider.send_email(msg)
        assert result == "<brevo-msg-123>"


async def test_brevo_handles_401():
    """BrevoEmailProvider raises IntegrationConfigError on 401."""
    with patch("app.integrations.email.brevo.settings") as mock_settings:
        mock_settings.EMAIL_API_KEY = "xkeysib-bad-key"
        mock_settings.EMAIL_FROM_ADDRESS = "alerts@agrinova.ai"
        mock_settings.EMAIL_FROM_NAME = "AgriNova AI"
        provider = BrevoEmailProvider()

    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client_instance

        msg = EmailMessage(
            to_email="farmer@example.com",
            subject="Test",
            html_body="<p>Body</p>",
        )
        with pytest.raises(IntegrationConfigError, match="invalid or expired"):
            await provider.send_email(msg)


async def test_brevo_handles_429():
    """BrevoEmailProvider raises IntegrationRateLimitError on 429."""
    from app.integrations.base import IntegrationRateLimitError

    with patch("app.integrations.email.brevo.settings") as mock_settings:
        mock_settings.EMAIL_API_KEY = "xkeysib-key"
        mock_settings.EMAIL_FROM_ADDRESS = "alerts@agrinova.ai"
        mock_settings.EMAIL_FROM_NAME = "AgriNova AI"
        provider = BrevoEmailProvider()

    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Too Many Requests"

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.return_value = mock_response
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client_instance

        msg = EmailMessage(
            to_email="farmer@example.com",
            subject="Test",
            html_body="<p>Body</p>",
        )
        with pytest.raises(IntegrationRateLimitError):
            await provider.send_email(msg)


async def test_brevo_handles_timeout():
    """BrevoEmailProvider raises IntegrationTimeoutError on timeout."""
    import httpx
    from app.integrations.base import IntegrationTimeoutError

    with patch("app.integrations.email.brevo.settings") as mock_settings:
        mock_settings.EMAIL_API_KEY = "xkeysib-key"
        mock_settings.EMAIL_FROM_ADDRESS = "alerts@agrinova.ai"
        mock_settings.EMAIL_FROM_NAME = "AgriNova AI"
        provider = BrevoEmailProvider()

    with patch("httpx.AsyncClient") as MockClient:
        mock_client_instance = AsyncMock()
        mock_client_instance.post.side_effect = httpx.TimeoutException("timed out")
        mock_client_instance.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client_instance.__aexit__ = AsyncMock(return_value=False)
        MockClient.return_value = mock_client_instance

        msg = EmailMessage(
            to_email="farmer@example.com",
            subject="Test",
            html_body="<p>Body</p>",
        )
        with pytest.raises(IntegrationTimeoutError):
            await provider.send_email(msg)


# ═══════════════════════════════════════════════════════════════════════
# 5. TemplateEngine Tests
# ═══════════════════════════════════════════════════════════════════════


def test_template_engine_initializes(tmp_templates):
    """TemplateEngine initializes with a valid templates directory."""
    engine = TemplateEngine(templates_dir=tmp_templates)
    assert engine.env is not None


def test_template_engine_creates_missing_dir(tmp_path):
    """TemplateEngine creates the templates directory if it doesn't exist."""
    new_dir = tmp_path / "nonexistent" / "templates"
    assert not new_dir.exists()
    engine = TemplateEngine(templates_dir=new_dir)
    assert new_dir.exists()


def test_render_html(tmp_templates):
    """render_html produces correct output from a template."""
    engine = TemplateEngine(templates_dir=tmp_templates)
    html = engine.render_html("test_email", name="Farmer", message="Welcome!")
    assert "Hello Farmer!" in html
    assert "Welcome!" in html
    assert "<html>" in html


def test_render_text(tmp_templates):
    """render_text produces correct output from a .txt template."""
    engine = TemplateEngine(templates_dir=tmp_templates)
    text = engine.render_text("test_email", name="Farmer", message="Welcome!")
    assert text is not None
    assert "Hello Farmer!" in text
    assert "Welcome!" in text
    assert "<html>" not in text


def test_render_text_missing_returns_none(tmp_templates):
    """render_text returns None when no .txt template exists."""
    engine = TemplateEngine(templates_dir=tmp_templates)
    text = engine.render_text("html_only", content="test")
    assert text is None


def test_render_html_missing_returns_fallback(tmp_templates):
    """render_html returns inline fallback when template is missing."""
    engine = TemplateEngine(templates_dir=tmp_templates)
    html = engine.render_html(
        "nonexistent_template",
        title="Alert",
        message="Something happened",
    )
    assert "Alert" in html
    assert "Something happened" in html
    assert "template 'nonexistent_template' unavailable" in html


def test_template_exists(tmp_templates):
    """template_exists correctly reports template availability."""
    engine = TemplateEngine(templates_dir=tmp_templates)
    assert engine.template_exists("test_email") is True
    assert engine.template_exists("html_only") is True
    assert engine.template_exists("nonexistent") is False


def test_global_variables_available(tmp_templates):
    """Global template variables (app_name, etc.) are available."""
    # Create a template that uses a global
    (tmp_templates / "global_test.html").write_text(
        "<p>From: {{ app_name }}</p>"
    )
    engine = TemplateEngine(templates_dir=tmp_templates)
    html = engine.render_html("global_test")
    assert "AgriNova AI" in html


def test_html_auto_escaping(tmp_templates):
    """HTML auto-escaping prevents injection in .html templates."""
    (tmp_templates / "escape_test.html").write_text(
        "<p>{{ user_input }}</p>"
    )
    engine = TemplateEngine(templates_dir=tmp_templates)
    html = engine.render_html(
        "escape_test",
        user_input='<script>alert("xss")</script>',
    )
    assert "<script>" not in html
    assert "&lt;script&gt;" in html

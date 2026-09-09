"""
AgriNova AI — NotificationPreference model (V5.2).

Per-user notification preferences: which categories are enabled,
which channels (in-app, email) are active, and the master email toggle.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class NotificationPreference(Base):
    """User notification preferences.

    One row per user.  Created lazily on first access; if a row does
    not exist the service layer treats all categories as opted-in
    (sensible defaults).
    """

    __tablename__ = "notification_preferences"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        index=True,
        nullable=False,
    )

    # ── Master channel toggles ──
    email_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    in_app_enabled: Mapped[bool] = mapped_column(Boolean, default=True)

    # ── Per-category toggles (all default ON) ──
    weather_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    irrigation_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    fertilizer_reminders: Mapped[bool] = mapped_column(Boolean, default=True)
    market_alerts: Mapped[bool] = mapped_column(Boolean, default=True)
    ai_insights: Mapped[bool] = mapped_column(Boolean, default=True)
    # system notifications are always delivered — no toggle

    # ── Timestamps ──
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    user = relationship("User")

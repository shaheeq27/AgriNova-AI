"""
AgriNova AI — EmailLog model (V5.2).

Audit trail for every email dispatched by the platform.  Captures
recipient, template used, delivery status, and provider metadata
so we can debug delivery issues and track engagement.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class EmailLog(Base):
    """Immutable audit log of outbound email delivery attempts."""

    __tablename__ = "email_logs"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    recipient_email: Mapped[str] = mapped_column(
        String(255), nullable=False
    )

    # Content metadata
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    template_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, default="system"
    )

    # Delivery tracking
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending"
    )  # pending | sent | failed | bounced
    provider: Mapped[str] = mapped_column(
        String(50), nullable=False, default="console"
    )
    provider_message_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    sent_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user = relationship("User")

    # Composite index for common query: "show me recent emails for this user"
    __table_args__ = (
        Index("ix_email_logs_user_created", "user_id", "created_at"),
    )

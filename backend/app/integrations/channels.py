"""
AgriNova AI — Notification Channel Abstraction (V5).

Defines the abstract notification channel interface and dispatcher.
Channels: IN_APP (existing) and EMAIL (V5.2).  Extensible to SMS,
WhatsApp, or push notifications later without touching calling code.

Design:
  - ``NotificationChannel`` is the abstract interface each delivery
    mechanism implements.
  - ``NotificationDispatcher`` routes a notification to the correct
    channel(s) based on type and user preferences.
  - Business logic creates a notification payload and calls the
    dispatcher — it never talks to channels directly.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ── Channel Types ────────────────────────────────────────────────────────────


class ChannelType(str, Enum):
    """Supported notification delivery channels."""

    IN_APP = "in_app"
    EMAIL = "email"
    # Future: SMS = "sms", WHATSAPP = "whatsapp", PUSH = "push"


# ── Notification Categories ─────────────────────────────────────────────────


class NotificationCategory(str, Enum):
    """Categories that map to user preference toggles."""

    WEATHER = "weather"
    IRRIGATION = "irrigation"
    FERTILIZER = "fertilizer"
    MARKET = "market"
    AI = "ai"
    SYSTEM = "system"  # Always delivered, cannot be opted out


# ── Notification Payload ─────────────────────────────────────────────────────


@dataclass
class NotificationPayload:
    """Channel-agnostic notification payload.

    Created by business logic, consumed by channels.
    """

    user_id: str
    title: str
    message: str
    category: NotificationCategory
    severity: str = "info"  # "info" | "warning" | "critical"
    related_entity_type: str | None = None
    related_entity_id: str | None = None
    template_name: str | None = None  # For email: which template to use
    template_data: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )


# ── Channel Interface ────────────────────────────────────────────────────────


class NotificationChannel(ABC):
    """Abstract base for notification delivery channels.

    Each channel (in-app DB, email, future SMS) implements ``send()``.
    """

    channel_type: ChannelType

    @abstractmethod
    async def send(self, payload: NotificationPayload, recipient_info: dict[str, Any]) -> bool:
        """Deliver a notification through this channel.

        Args:
            payload: The notification content and metadata.
            recipient_info: Channel-specific recipient data
                (e.g., ``{"email": "farmer@example.com"}`` for email).

        Returns:
            ``True`` if delivery succeeded, ``False`` otherwise.
            Must NOT raise — failures are logged and returned as False.
        """
        ...


# ── Dispatcher ───────────────────────────────────────────────────────────────


class NotificationDispatcher:
    """Routes notifications to registered channels based on category
    and user preferences.

    Usage::

        dispatcher = NotificationDispatcher()
        dispatcher.register_channel(in_app_channel)
        dispatcher.register_channel(email_channel)

        results = await dispatcher.dispatch(payload, user_prefs, recipient_info)
    """

    def __init__(self) -> None:
        self._channels: dict[ChannelType, NotificationChannel] = {}

    def register_channel(self, channel: NotificationChannel) -> None:
        """Register a notification channel."""
        self._channels[channel.channel_type] = channel
        logger.info("Registered notification channel: %s", channel.channel_type.value)

    async def dispatch(
        self,
        payload: NotificationPayload,
        user_preferences: dict[str, bool] | None = None,
        recipient_info: dict[str, Any] | None = None,
    ) -> dict[ChannelType, bool]:
        """Dispatch a notification to all applicable channels.

        Args:
            payload: The notification to deliver.
            user_preferences: Per-category opt-in/out preferences.
                Keys match ``NotificationCategory`` values.
                If ``None``, all categories are treated as opted-in.
            recipient_info: Channel-specific recipient data.

        Returns:
            Dict mapping each attempted channel to its success/failure.
        """
        results: dict[ChannelType, bool] = {}
        recipient_info = recipient_info or {}

        # System notifications are always delivered
        if payload.category != NotificationCategory.SYSTEM:
            if user_preferences is not None:
                category_key = f"{payload.category.value}_alerts" if payload.category == NotificationCategory.WEATHER else f"{payload.category.value}_reminders" if payload.category in (NotificationCategory.IRRIGATION, NotificationCategory.FERTILIZER) else f"{payload.category.value}_alerts"
                
                # Check category-specific preference
                if not user_preferences.get(category_key, True):
                    logger.debug(
                        "Notification category '%s' opted out by user %s",
                        payload.category.value,
                        payload.user_id,
                    )
                    return results

        for channel_type, channel in self._channels.items():
            # For email channel, also check the master email toggle
            if channel_type == ChannelType.EMAIL:
                if user_preferences and not user_preferences.get("email_enabled", True):
                    logger.debug(
                        "Email disabled for user %s, skipping email channel",
                        payload.user_id,
                    )
                    continue

            try:
                success = await channel.send(payload, recipient_info)
                results[channel_type] = success
                if not success:
                    logger.warning(
                        "Channel %s failed for notification '%s' to user %s",
                        channel_type.value,
                        payload.title,
                        payload.user_id,
                    )
            except Exception as exc:
                logger.error(
                    "Unexpected error dispatching via %s: %s",
                    channel_type.value,
                    exc,
                    exc_info=True,
                )
                results[channel_type] = False

        return results

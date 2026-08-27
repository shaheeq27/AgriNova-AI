"""
AgriNova AI — Integration Base Classes (V5).

Abstract interface for all external integrations.  Any new provider
(market data source, email sender, SMS gateway) must implement this
contract so the rest of the platform stays provider-agnostic.

Design principles:
  - Shared retry, error handling, and result envelope live HERE.
  - Concrete providers (Market, Email) inherit and add domain methods.
  - Never hard-code secrets — all credentials come from Settings.
  - Failures must be explicit, not silent.

Follows the same provider abstraction pattern established in
``app.ai.providers.base`` for LLM providers.
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


# ── Result Envelope ──────────────────────────────────────────────────────────


class IntegrationStatus(str, Enum):
    """Outcome of an integration call."""

    SUCCESS = "success"
    FAILURE = "failure"
    UNAVAILABLE = "unavailable"


@dataclass
class IntegrationResult:
    """Typed result envelope for all external integration calls.

    Every integration method returns this instead of raising on failure,
    so callers can handle unavailable-state gracefully.
    """

    status: IntegrationStatus
    data: Any = None
    error: str | None = None
    timestamp: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    @classmethod
    def success(cls, data: Any = None) -> IntegrationResult:
        return cls(status=IntegrationStatus.SUCCESS, data=data)

    @classmethod
    def failure(cls, error: str) -> IntegrationResult:
        return cls(status=IntegrationStatus.FAILURE, error=error)

    @classmethod
    def unavailable(cls, reason: str = "Service unavailable") -> IntegrationResult:
        return cls(status=IntegrationStatus.UNAVAILABLE, error=reason)

    @property
    def is_success(self) -> bool:
        return self.status == IntegrationStatus.SUCCESS


# ── Retry Policy ─────────────────────────────────────────────────────────────


@dataclass
class RetryPolicy:
    """Configurable retry with exponential backoff.

    Defaults: max 3 attempts, 1s base delay, 2× multiplier → 1s, 2s, 4s.
    """

    max_attempts: int = 3
    base_delay_seconds: float = 1.0
    backoff_multiplier: float = 2.0
    max_delay_seconds: float = 10.0

    def delay_for_attempt(self, attempt: int) -> float:
        """Calculate delay for a given attempt number (0-indexed)."""
        delay = self.base_delay_seconds * (self.backoff_multiplier ** attempt)
        return min(delay, self.max_delay_seconds)


# ── Exceptions ───────────────────────────────────────────────────────────────


class IntegrationError(Exception):
    """Base exception for all integration failures."""

    def __init__(self, message: str, provider: str = "", retriable: bool = False):
        self.provider = provider
        self.retriable = retriable
        super().__init__(message)


class IntegrationConfigError(IntegrationError):
    """Integration is not configured correctly (missing API key, etc.)."""

    def __init__(self, message: str, provider: str = ""):
        super().__init__(message, provider=provider, retriable=False)


class IntegrationTimeoutError(IntegrationError):
    """External service did not respond in time."""

    def __init__(self, message: str = "Request timed out", provider: str = ""):
        super().__init__(message, provider=provider, retriable=True)


class IntegrationRateLimitError(IntegrationError):
    """External service rate limit was hit."""

    def __init__(self, message: str = "Rate limit exceeded", provider: str = ""):
        super().__init__(message, provider=provider, retriable=True)


# ── Base Provider ────────────────────────────────────────────────────────────


class BaseIntegrationProvider(ABC):
    """Abstract base class that every external integration provider
    must implement.

    Provides shared retry-with-backoff logic.  Concrete providers
    implement ``execute()`` with their domain-specific call.

    Usage::

        result = await provider.execute_with_retry(commodity="Tomato")
        if result.is_success:
            prices = result.data
    """

    provider_name: str = "base"
    retry_policy: RetryPolicy = RetryPolicy()

    def __init__(self, retry_policy: RetryPolicy | None = None) -> None:
        if retry_policy is not None:
            self.retry_policy = retry_policy

    @abstractmethod
    async def execute(self, **kwargs: Any) -> IntegrationResult:
        """Perform the integration call.

        Concrete providers implement this with their specific logic.
        Must return ``IntegrationResult``, not raise on expected failures.
        """
        ...

    async def health_check(self) -> bool:
        """Check if the external service is reachable.

        Default implementation calls ``execute()`` with no args and
        checks for non-failure.  Providers may override with a lighter
        ping endpoint.
        """
        try:
            result = await self.execute()
            return result.is_success
        except Exception:
            return False

    async def execute_with_retry(self, **kwargs: Any) -> IntegrationResult:
        """Wrap ``execute()`` with configurable retry + exponential backoff.

        Only retries on ``IntegrationError`` where ``retriable=True``.
        Non-retriable errors and unexpected exceptions are returned as
        failures immediately.
        """
        last_error: str = "Unknown error"

        for attempt in range(self.retry_policy.max_attempts):
            try:
                result = await self.execute(**kwargs)
                if result.is_success:
                    return result

                # Provider returned a failure result (not an exception).
                # Don't retry — the provider decided the call failed.
                return result

            except IntegrationError as exc:
                last_error = str(exc)
                if not exc.retriable:
                    logger.warning(
                        "[%s] Non-retriable error: %s",
                        self.provider_name,
                        exc,
                    )
                    return IntegrationResult.failure(last_error)

                if attempt < self.retry_policy.max_attempts - 1:
                    delay = self.retry_policy.delay_for_attempt(attempt)
                    logger.info(
                        "[%s] Retriable error (attempt %d/%d), "
                        "retrying in %.1fs: %s",
                        self.provider_name,
                        attempt + 1,
                        self.retry_policy.max_attempts,
                        delay,
                        exc,
                    )
                    await asyncio.sleep(delay)

            except Exception as exc:
                last_error = f"Unexpected error: {exc}"
                logger.error(
                    "[%s] Unexpected error on attempt %d: %s",
                    self.provider_name,
                    attempt + 1,
                    exc,
                    exc_info=True,
                )
                # Don't retry unexpected errors
                return IntegrationResult.failure(last_error)

        logger.warning(
            "[%s] All %d retry attempts exhausted. Last error: %s",
            self.provider_name,
            self.retry_policy.max_attempts,
            last_error,
        )
        return IntegrationResult.failure(
            f"All {self.retry_policy.max_attempts} attempts failed: {last_error}"
        )

"""
AgriNova AI — Base Market Provider (V5.1).

Abstract interface for market data sources.  Inherits shared retry/error
handling from ``BaseIntegrationProvider``.
"""

from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import date
from typing import Any

from app.integrations.base import BaseIntegrationProvider, IntegrationResult


@dataclass
class MarketPriceData:
    """Provider-agnostic market price record.

    All providers normalize their responses into this shape before
    returning.  ``MarketService`` then maps this to the ORM model.
    """

    commodity: str
    variety: str | None = None
    market_name: str = ""
    district: str = ""
    state: str = ""
    min_price: float = 0.0
    max_price: float = 0.0
    modal_price: float = 0.0
    price_date: date = field(default_factory=date.today)


class BaseMarketProvider(BaseIntegrationProvider):
    """Abstract base class for market data providers.

    Concrete implementations:
      - ``DemoProvider`` — realistic mock data for development
      - ``DataGovProvider`` — data.gov.in API

    The provider returns a list of ``MarketPriceData`` via
    ``fetch_prices()``.  The inherited ``execute()`` delegates to it
    for retry compatibility.
    """

    provider_name: str = "base_market"

    @abstractmethod
    async def fetch_prices(
        self,
        commodity: str | None = None,
        state: str | None = None,
        market: str | None = None,
    ) -> list[MarketPriceData]:
        """Fetch market prices from the external source.

        Args:
            commodity: Filter by commodity name (optional).
            state: Filter by state (optional).
            market: Filter by market/mandi name (optional).

        Returns:
            List of normalized price records.

        Raises:
            IntegrationError subclasses on failure.
        """
        ...

    async def execute(self, **kwargs: Any) -> IntegrationResult:
        """Bridge for ``execute_with_retry()`` compatibility.

        Delegates to ``fetch_prices()`` and wraps the result.
        """
        try:
            prices = await self.fetch_prices(
                commodity=kwargs.get("commodity"),
                state=kwargs.get("state"),
                market=kwargs.get("market"),
            )
            return IntegrationResult.success(data=prices)
        except Exception as exc:
            return IntegrationResult.failure(str(exc))

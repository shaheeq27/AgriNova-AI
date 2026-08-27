"""
AgriNova AI — data.gov.in Market Provider (V5.1).

Actual integration with the Indian government's Open Data portal.
Fetches daily mandi prices for agricultural commodities.
"""

from __future__ import annotations

from datetime import datetime, date
from typing import Any

import httpx

from app.core.config import settings
from app.integrations.base import IntegrationConfigError, IntegrationTimeoutError, IntegrationError
from app.integrations.market.base import BaseMarketProvider, MarketPriceData


class DataGovProvider(BaseMarketProvider):
    """Fetches market prices from data.gov.in."""

    provider_name: str = "data_gov_in"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.api_url = settings.MARKET_DATA_API_URL
        self.api_key = settings.MARKET_DATA_API_KEY
        self.resource_id = settings.MARKET_DATA_RESOURCE_ID
        
        if not self.api_key or not self.resource_id:
            raise IntegrationConfigError(
                "MARKET_DATA_API_KEY and MARKET_DATA_RESOURCE_ID must be set",
                provider=self.provider_name
            )

    async def fetch_prices(
        self,
        commodity: str | None = None,
        state: str | None = None,
        market: str | None = None,
    ) -> list[MarketPriceData]:
        """Fetch prices from the data.gov.in REST API."""
        
        # Build query parameters
        params: dict[str, Any] = {
            "api-key": self.api_key,
            "format": "json",
            "limit": "1000", # Max allowed usually
        }
        
        # data.gov.in allows filtering via filters[column]=value
        if commodity:
            params["filters[commodity]"] = commodity
        if state:
            params["filters[state]"] = state
        if market:
            params["filters[market]"] = market

        url = f"{self.api_url}/{self.resource_id}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=15.0)
                
                if response.status_code == 429:
                    raise IntegrationError("Rate limit exceeded", provider=self.provider_name, retriable=True)
                
                response.raise_for_status()
                data = response.json()
                
        except httpx.TimeoutException as exc:
            raise IntegrationTimeoutError(f"data.gov.in timed out: {exc}", provider=self.provider_name)
        except httpx.HTTPStatusError as exc:
            raise IntegrationError(f"HTTP error {exc.response.status_code}: {exc}", provider=self.provider_name, retriable=False)
        except Exception as exc:
            raise IntegrationError(f"Failed to fetch data: {exc}", provider=self.provider_name, retriable=False)

        records = data.get("records", [])
        prices: list[MarketPriceData] = []
        
        for record in records:
            try:
                # data.gov.in date format is usually DD/MM/YYYY
                raw_date = record.get("arrival_date", "")
                try:
                    price_date = datetime.strptime(raw_date, "%d/%m/%Y").date()
                except ValueError:
                    price_date = date.today()

                prices.append(MarketPriceData(
                    commodity=record.get("commodity", ""),
                    variety=record.get("variety"),
                    market_name=record.get("market", ""),
                    district=record.get("district", ""),
                    state=record.get("state", ""),
                    min_price=float(record.get("min_price", 0.0) or 0.0),
                    max_price=float(record.get("max_price", 0.0) or 0.0),
                    modal_price=float(record.get("modal_price", 0.0) or 0.0),
                    price_date=price_date
                ))
            except (ValueError, TypeError):
                # Skip malformed records
                continue

        return prices

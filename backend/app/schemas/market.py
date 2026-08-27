"""
AgriNova AI — Market Price Schemas (V5.1).

Pydantic validation and response models for market intelligence.
All responses include ``last_updated`` and ``data_status`` fields
so the farmer always sees how fresh the data is.
"""

from __future__ import annotations

from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field, ConfigDict

class DataStatus(str, Enum):
    """Freshness status of market price data."""

    LIVE = "live"
    CACHED = "cached"
    UNAVAILABLE = "unavailable"


# ── Response Models ──────────────────────────────────────────────────────────


class MarketPriceResponse(BaseModel):
    """A single market price record."""

    id: str
    commodity: str
    variety: str | None = None
    market_name: str
    district: str
    state: str
    min_price: float
    max_price: float
    modal_price: float
    price_date: date
    source: str
    fetched_at: datetime
    price_change_pct: float | None = None  # Computed vs previous day

    model_config = ConfigDict(from_attributes=True)


class MarketPriceListResponse(BaseModel):
    """List of market prices with freshness metadata."""

    items: list[MarketPriceResponse]
    total: int
    last_updated: datetime | None = None
    data_status: DataStatus = DataStatus.LIVE


class MarketComparisonItem(BaseModel):
    """A single market's price in a cross-market comparison."""

    market_name: str
    district: str
    state: str
    min_price: float
    max_price: float
    modal_price: float
    price_date: date


class MarketComparisonResponse(BaseModel):
    """Compare a commodity's price across multiple markets."""

    commodity: str
    markets: list[MarketComparisonItem]
    last_updated: datetime | None = None
    data_status: DataStatus = DataStatus.LIVE


class MarketSummaryItem(BaseModel):
    """Summary for one commodity (for dashboard card)."""

    commodity: str
    market_name: str
    modal_price: float
    price_date: date
    price_change_pct: float | None = None
    trend: str | None = None  # "up" | "down" | "stable" | None


class MarketSummaryResponse(BaseModel):
    """Dashboard-ready market summary for the farmer's crops."""

    items: list[MarketSummaryItem]
    last_updated: datetime | None = None
    data_status: DataStatus = DataStatus.LIVE


class MarketStatusResponse(BaseModel):
    """Health + freshness status for the market data integration."""

    provider: str
    is_healthy: bool
    last_updated: datetime | None = None
    total_records: int = 0
    data_status: DataStatus = DataStatus.LIVE

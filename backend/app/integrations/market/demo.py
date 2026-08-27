"""
AgriNova AI — Demo Market Provider (V5.1).

Generates realistic Indian mandi price data for development and testing.
No external credentials needed.  Covers the 30 crops in the AgriNova KB
across 5 major mandis.

``MARKET_DATA_PROVIDER=demo`` enables the entire market pipeline to be
built and tested without data.gov.in credentials.
"""

from __future__ import annotations

import random
from datetime import date, timedelta
from typing import Any

from app.integrations.base import IntegrationResult
from app.integrations.market.base import BaseMarketProvider, MarketPriceData


# ── Demo Data ────────────────────────────────────────────────────────────────

# Curated list of major Indian mandis
DEMO_MARKETS = [
    {"name": "Azadpur", "district": "New Delhi", "state": "Delhi"},
    {"name": "Vashi", "district": "Navi Mumbai", "state": "Maharashtra"},
    {"name": "Koyambedu", "district": "Chennai", "state": "Tamil Nadu"},
    {"name": "Yeshwanthpur", "district": "Bengaluru", "state": "Karnataka"},
    {"name": "Bowenpally", "district": "Hyderabad", "state": "Telangana"},
]

# Base modal prices (₹/quintal) for the 30 KB crops — realistic ranges
DEMO_CROP_PRICES: dict[str, tuple[float, float]] = {
    "Rice": (2200, 3500),
    "Wheat": (2100, 3200),
    "Maize": (1800, 2800),
    "Cotton": (5500, 7500),
    "Sugarcane": (300, 450),
    "Soybean": (3800, 5200),
    "Groundnut": (4500, 6500),
    "Mustard": (4800, 6200),
    "Sunflower": (5000, 6800),
    "Chickpea": (4200, 5800),
    "Pigeon Pea": (5500, 7200),
    "Lentil": (4800, 6500),
    "Green Gram": (6000, 8000),
    "Black Gram": (5500, 7500),
    "Tomato": (1500, 4500),
    "Onion": (1200, 3500),
    "Potato": (800, 2200),
    "Brinjal": (1500, 3000),
    "Cauliflower": (1200, 3000),
    "Cabbage": (800, 2000),
    "Chilli": (8000, 15000),
    "Turmeric": (7000, 12000),
    "Ginger": (6000, 10000),
    "Garlic": (5000, 12000),
    "Banana": (1500, 3500),
    "Mango": (3000, 8000),
    "Coconut": (2000, 4000),
    "Papaya": (1000, 2500),
    "Jute": (3500, 5000),
    "Tea": (15000, 25000),
}


class DemoMarketProvider(BaseMarketProvider):
    """Generates realistic demo market data.

    Prices are deterministically seeded by date so the same date
    always produces the same base prices — but with slight per-market
    variation to simulate real mandi differences.
    """

    provider_name: str = "demo"

    async def fetch_prices(
        self,
        commodity: str | None = None,
        state: str | None = None,
        market: str | None = None,
    ) -> list[MarketPriceData]:
        """Generate demo prices for today (or filtered subset)."""
        today = date.today()
        prices: list[MarketPriceData] = []

        crops = DEMO_CROP_PRICES
        if commodity:
            # Case-insensitive match
            crops = {
                k: v
                for k, v in crops.items()
                if k.lower() == commodity.lower()
            }

        markets = DEMO_MARKETS
        if state:
            markets = [
                m for m in markets if m["state"].lower() == state.lower()
            ]
        if market:
            markets = [
                m for m in markets if m["name"].lower() == market.lower()
            ]

        for crop_name, (low, high) in crops.items():
            for mkt in markets:
                # Deterministic seed: crop + market + date
                seed = hash(f"{crop_name}:{mkt['name']}:{today.isoformat()}")
                rng = random.Random(seed)

                # Generate modal price within the crop's range
                modal = round(rng.uniform(low, high), 2)
                # Min is 5-15% below modal, max is 5-15% above
                spread_low = rng.uniform(0.05, 0.15)
                spread_high = rng.uniform(0.05, 0.15)
                min_price = round(modal * (1 - spread_low), 2)
                max_price = round(modal * (1 + spread_high), 2)

                prices.append(
                    MarketPriceData(
                        commodity=crop_name,
                        variety=None,
                        market_name=mkt["name"],
                        district=mkt["district"],
                        state=mkt["state"],
                        min_price=min_price,
                        max_price=max_price,
                        modal_price=modal,
                        price_date=today,
                    )
                )

        return prices

    async def health_check(self) -> bool:
        """Demo provider is always healthy."""
        return True

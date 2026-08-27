"""
AgriNova AI — Market Price Repository (V5.1).

Data access layer for market price records.
"""

from __future__ import annotations

from datetime import date, datetime, timezone

from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.market_price import MarketPrice


class MarketPriceRepository:
    """Repository for market price CRUD and queries."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_latest_prices(
        self,
        commodity: str | None = None,
        state: str | None = None,
        market: str | None = None,
        limit: int = 50,
    ) -> list[MarketPrice]:
        """Get the most recent prices, optionally filtered.

        Returns the latest price_date records first.
        """
        query = select(MarketPrice).order_by(
            MarketPrice.price_date.desc(),
            MarketPrice.commodity.asc(),
        )

        if commodity:
            query = query.where(
                func.lower(MarketPrice.commodity) == commodity.lower()
            )
        if state:
            query = query.where(
                func.lower(MarketPrice.state) == state.lower()
            )
        if market:
            query = query.where(
                func.lower(MarketPrice.market_name) == market.lower()
            )

        query = query.limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_prices_by_market(
        self,
        market_name: str,
        price_date: date | None = None,
        limit: int = 50,
    ) -> list[MarketPrice]:
        """Get all commodity prices at a given market."""
        query = select(MarketPrice).where(
            func.lower(MarketPrice.market_name) == market_name.lower()
        )

        if price_date:
            query = query.where(MarketPrice.price_date == price_date)
        else:
            # Get latest date available for this market
            sub = (
                select(func.max(MarketPrice.price_date))
                .where(
                    func.lower(MarketPrice.market_name) == market_name.lower()
                )
                .scalar_subquery()
            )
            query = query.where(MarketPrice.price_date == sub)

        query = query.order_by(MarketPrice.commodity.asc()).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_price_comparison(
        self,
        commodity: str,
        markets: list[str],
    ) -> list[MarketPrice]:
        """Compare a single commodity's latest price across markets."""
        lower_markets = [m.lower() for m in markets]

        # Get latest date per market for this commodity
        query = (
            select(MarketPrice)
            .where(
                and_(
                    func.lower(MarketPrice.commodity) == commodity.lower(),
                    func.lower(MarketPrice.market_name).in_(lower_markets),
                )
            )
            .order_by(
                MarketPrice.price_date.desc(),
                MarketPrice.market_name.asc(),
            )
        )

        result = await self.db.execute(query)
        all_prices = list(result.scalars().all())

        # Keep only the latest entry per market
        seen_markets: set[str] = set()
        comparison: list[MarketPrice] = []
        for price in all_prices:
            market_key = price.market_name.lower()
            if market_key not in seen_markets:
                seen_markets.add(market_key)
                comparison.append(price)

        return comparison

    async def bulk_upsert(self, prices: list[MarketPrice]) -> int:
        """Insert or update prices in bulk.

        Uses a delete-then-insert strategy per commodity+market+date
        to avoid complex upsert logic across SQLite and PostgreSQL.

        Returns the number of records persisted.
        """
        if not prices:
            return 0

        # Group by (commodity, market, date) to delete stale entries
        keys: set[tuple[str, str, date]] = set()
        for p in prices:
            keys.add((p.commodity.lower(), p.market_name.lower(), p.price_date))

        for commodity, market, price_date in keys:
            await self.db.execute(
                delete(MarketPrice).where(
                    and_(
                        func.lower(MarketPrice.commodity) == commodity,
                        func.lower(MarketPrice.market_name) == market,
                        MarketPrice.price_date == price_date,
                    )
                )
            )

        for p in prices:
            self.db.add(p)

        await self.db.flush()
        return len(prices)

    async def get_last_updated(self) -> datetime | None:
        """Get the timestamp of the most recently fetched record."""
        query = select(func.max(MarketPrice.fetched_at))
        result = await self.db.execute(query)
        return result.scalar()

    async def get_previous_prices(
        self,
        commodity: str,
        market_name: str,
        before_date: date,
        limit: int = 1,
    ) -> list[MarketPrice]:
        """Get the most recent price(s) before a given date.

        Used for computing day-over-day price changes.
        """
        query = (
            select(MarketPrice)
            .where(
                and_(
                    func.lower(MarketPrice.commodity) == commodity.lower(),
                    func.lower(MarketPrice.market_name) == market_name.lower(),
                    MarketPrice.price_date < before_date,
                )
            )
            .order_by(MarketPrice.price_date.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

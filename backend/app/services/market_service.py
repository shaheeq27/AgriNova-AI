"""
AgriNova AI — Market Service (V5.1).

Business logic for fetching, caching, and serving market intelligence.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.integrations.market.factory import get_market_provider
from app.models.market_price import MarketPrice
from app.repositories.market_price_repo import MarketPriceRepository
from app.schemas.market import (
    DataStatus,
    MarketComparisonItem,
    MarketComparisonResponse,
    MarketPriceListResponse,
    MarketPriceResponse,
    MarketStatusResponse,
    MarketSummaryItem,
    MarketSummaryResponse,
)

logger = logging.getLogger(__name__)


class MarketService:
    """Service for market price intelligence."""

    def __init__(self, db: AsyncSession) -> None:
        self.repo = MarketPriceRepository(db)
        self.provider = get_market_provider()

    async def _compute_price_change(self, price: MarketPrice) -> float | None:
        """Compute % change against the previous available date."""
        previous = await self.repo.get_previous_prices(
            commodity=price.commodity,
            market_name=price.market_name,
            before_date=price.price_date,
            limit=1
        )
        if not previous or previous[0].modal_price == 0:
            return None
            
        change = ((price.modal_price - previous[0].modal_price) / previous[0].modal_price) * 100.0
        return round(change, 1)

    def _map_to_response(self, price: MarketPrice, change: float | None = None) -> MarketPriceResponse:
        return MarketPriceResponse(
            id=price.id,
            commodity=price.commodity.title(),
            variety=price.variety,
            market_name=price.market_name,
            district=price.district,
            state=price.state,
            min_price=price.min_price,
            max_price=price.max_price,
            modal_price=price.modal_price,
            price_date=price.price_date,
            source=price.source,
            fetched_at=price.fetched_at,
            price_change_pct=change
        )

    async def get_crop_prices(self, commodity: str, state: str | None = None) -> MarketPriceListResponse:
        """Get latest prices for a crop, optionally filtered by state."""
        prices = await self.repo.get_latest_prices(commodity=commodity, state=state)
        last_updated = await self.repo.get_last_updated()
        
        items = []
        for p in prices:
            change = await self._compute_price_change(p)
            items.append(self._map_to_response(p, change))
            
        status = DataStatus.LIVE if prices else DataStatus.UNAVAILABLE
            
        return MarketPriceListResponse(
            items=items,
            total=len(items),
            last_updated=last_updated,
            data_status=status
        )

    async def get_market_prices(self, market_name: str) -> MarketPriceListResponse:
        """Get all crop prices at a specific market."""
        prices = await self.repo.get_prices_by_market(market_name=market_name)
        last_updated = await self.repo.get_last_updated()
        
        items = []
        for p in prices:
            change = await self._compute_price_change(p)
            items.append(self._map_to_response(p, change))
            
        status = DataStatus.LIVE if prices else DataStatus.UNAVAILABLE

        return MarketPriceListResponse(
            items=items,
            total=len(items),
            last_updated=last_updated,
            data_status=status
        )

    async def compare_prices(self, commodity: str, markets: list[str]) -> MarketComparisonResponse:
        """Compare a crop's price across multiple markets."""
        prices = await self.repo.get_price_comparison(commodity=commodity, markets=markets)
        last_updated = await self.repo.get_last_updated()
        
        items = [
            MarketComparisonItem(
                market_name=p.market_name,
                district=p.district,
                state=p.state,
                min_price=p.min_price,
                max_price=p.max_price,
                modal_price=p.modal_price,
                price_date=p.price_date
            )
            for p in prices
        ]
        
        status = DataStatus.LIVE if items else DataStatus.UNAVAILABLE
        
        return MarketComparisonResponse(
            commodity=commodity.title(),
            markets=items,
            last_updated=last_updated,
            data_status=status
        )

    async def get_dashboard_summary(self, commodities: list[str]) -> MarketSummaryResponse:
        """Get curated top-line summary for farmer's active crops."""
        summary_items = []
        
        for crop in commodities:
            prices = await self.repo.get_latest_prices(commodity=crop, limit=1)
            if not prices:
                continue
                
            p = prices[0]
            change = await self._compute_price_change(p)
            
            trend = "stable"
            if change is not None:
                if change > 2.0:
                    trend = "up"
                elif change < -2.0:
                    trend = "down"
                    
            summary_items.append(
                MarketSummaryItem(
                    commodity=p.commodity.title(),
                    market_name=p.market_name,
                    modal_price=p.modal_price,
                    price_date=p.price_date,
                    price_change_pct=change,
                    trend=trend
                )
            )
            
        last_updated = await self.repo.get_last_updated()
        status = DataStatus.LIVE if summary_items else DataStatus.UNAVAILABLE
        
        return MarketSummaryResponse(
            items=summary_items,
            last_updated=last_updated,
            data_status=status
        )

    async def refresh_prices(self) -> int:
        """Fetch fresh data from provider and upsert to database.
        
        Returns the number of records fetched and stored.
        """
        logger.info("Refreshing market prices via %s", self.provider.provider_name)
        result = await self.provider.execute_with_retry()
        
        if not result.is_success:
            logger.error("Failed to fetch market prices: %s", result.error)
            return 0
            
        provider_data = result.data
        if not provider_data:
            return 0
            
        now = datetime.now(timezone.utc)
        
        # Map to ORM models
        db_prices = []
        for d in provider_data:
            db_prices.append(
                MarketPrice(
                    commodity=d.commodity,
                    variety=d.variety,
                    market_name=d.market_name,
                    district=d.district,
                    state=d.state,
                    min_price=d.min_price,
                    max_price=d.max_price,
                    modal_price=d.modal_price,
                    price_date=d.price_date,
                    source=self.provider.provider_name,
                    fetched_at=now
                )
            )
            
        inserted_count = await self.repo.bulk_upsert(db_prices)
        logger.info("Refreshed %d market prices", inserted_count)
        return inserted_count
        
    async def get_status(self) -> MarketStatusResponse:
        """Get health and data freshness status."""
        is_healthy = await self.provider.health_check()
        last_updated = await self.repo.get_last_updated()
        
        # Quick count for sanity check
        from sqlalchemy import select, func
        count_query = select(func.count(MarketPrice.id))
        count_res = await self.repo.db.execute(count_query)
        total = count_res.scalar() or 0
        
        status = DataStatus.LIVE
        if not is_healthy:
            status = DataStatus.CACHED if total > 0 else DataStatus.UNAVAILABLE
            
        return MarketStatusResponse(
            provider=self.provider.provider_name,
            is_healthy=is_healthy,
            last_updated=last_updated,
            total_records=total,
            data_status=status
        )

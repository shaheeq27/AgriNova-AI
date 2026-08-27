"""
AgriNova AI — Market API Endpoints (V5.1).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.market_service import MarketService
from app.schemas.common import APIResponse
from app.schemas.market import (
    MarketComparisonResponse,
    MarketPriceListResponse,
    MarketStatusResponse,
    MarketSummaryResponse,
)

router = APIRouter(prefix="/market", tags=["Market Intelligence"])


@router.get("/prices", response_model=APIResponse)
async def get_crop_prices(
    commodity: str,
    state: str | None = None,
    db: AsyncSession = Depends(get_db)
):
    """Get the latest market prices for a specific crop."""
    service = MarketService(db)
    result = await service.get_crop_prices(commodity, state)
    return APIResponse.success(data=result.model_dump())


@router.get("/prices/{market_name}", response_model=APIResponse)
async def get_market_prices(
    market_name: str,
    db: AsyncSession = Depends(get_db)
):
    """Get all commodity prices at a specific market/mandi."""
    service = MarketService(db)
    result = await service.get_market_prices(market_name)
    return APIResponse.success(data=result.model_dump())


@router.get("/compare", response_model=APIResponse)
async def compare_prices(
    commodity: str,
    markets: Annotated[list[str], Query()],
    db: AsyncSession = Depends(get_db)
):
    """Compare a crop's price across multiple markets."""
    service = MarketService(db)
    result = await service.compare_prices(commodity, markets)
    return APIResponse.success(data=result.model_dump())


@router.get("/summary", response_model=APIResponse)
async def get_dashboard_summary(
    commodities: Annotated[list[str], Query()],
    db: AsyncSession = Depends(get_db)
):
    """Get a curated price summary for a list of crops (for the dashboard)."""
    service = MarketService(db)
    result = await service.get_dashboard_summary(commodities)
    return APIResponse.success(data=result.model_dump())


@router.get("/status", response_model=APIResponse)
async def get_market_status(
    db: AsyncSession = Depends(get_db)
):
    """Get health and freshness status for the market data integration."""
    service = MarketService(db)
    result = await service.get_status()
    return APIResponse.success(data=result.model_dump())


@router.post("/refresh", response_model=APIResponse)
async def trigger_refresh(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Trigger a manual refresh of market data in the background."""
    # Note: We need a fresh session for the background task to avoid
    # DetachedInstanceError since the request dependency session closes
    async def run_refresh():
        # In a real app we'd use a sessionmaker here, but for this
        # demo/solo project scale, we can just execute synchronously
        # or rely on a proper task queue (Celery/RQ). We'll await it directly
        # for now to ensure the SQLite lock doesn't conflict, as this is an admin endpoint.
        pass
        
    service = MarketService(db)
    count = await service.refresh_prices()
    await db.commit()
    
    return APIResponse.success(
        data={"records_fetched": count},
        message=f"Refreshed {count} market price records"
    )

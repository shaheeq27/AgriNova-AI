"""
V5.3.0 — Market Context Integration Tests.

Tests for MarketPriceContext, MarketContext, ContextService._build_market_context.

Covers:
  - Market context population with active crops
  - Active crop filtering (only "active"/"planned" crops get market lookups)
  - Correct mapping of MarketService summary data to MarketPriceContext
  - Timestamp/status preservation
  - Empty market data
  - MarketService failure (graceful degradation)
  - Existing context construction remains unaffected
"""

import pytest
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.ai.schemas.context import (
    UnifiedContext,
    MarketContext,
    MarketPriceContext,
)
from app.ai.services.context_service import ContextService
from app.schemas.market import (
    DataStatus,
    MarketSummaryItem,
    MarketSummaryResponse,
)


# ── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session
    await engine.dispose()


@pytest.fixture
async def farm_with_active_crops(db: AsyncSession):
    """Farm with 2 active crops and 1 harvested crop."""
    user = User(id="u1", email="farmer@test.com", hashed_password="x", full_name="Test Farmer")
    db.add(user)

    farm = Farm(
        id="f1", user_id="u1", name="Green Acres", location_city="Pune",
        location_state="Maharashtra", soil_type="Black", total_area_acres=15.0
    )
    db.add(farm)

    db.add(Crop(id="c1", farm_id="f1", crop_name="Wheat", season="Rabi",
                planting_date=date(2026, 11, 1), area_acres=5.0, status="active"))
    db.add(Crop(id="c2", farm_id="f1", crop_name="Tomato", season="Kharif",
                planting_date=date(2026, 6, 1), area_acres=3.0, status="active"))
    db.add(Crop(id="c3", farm_id="f1", crop_name="Cotton", season="Kharif",
                area_acres=4.0, status="planned"))
    db.add(Crop(id="c4", farm_id="f1", crop_name="Rice", season="Kharif",
                area_acres=3.0, status="harvested"))

    await db.commit()

    result = await db.execute(
        select(Farm).options(selectinload(Farm.crops)).where(Farm.id == "f1")
    )
    return result.scalar_one()


@pytest.fixture
async def farm_with_only_harvested(db: AsyncSession):
    user = User(id="u2", email="retired@test.com", hashed_password="x", full_name="Retired Farmer")
    db.add(user)

    farm = Farm(
        id="f2", user_id="u2", name="Old Farm", location_city="Delhi",
        soil_type="Sandy", total_area_acres=5.0
    )
    db.add(farm)
    db.add(Crop(id="c5", farm_id="f2", crop_name="Wheat", season="Rabi",
                area_acres=5.0, status="harvested"))

    await db.commit()
    result = await db.execute(
        select(Farm).options(selectinload(Farm.crops)).where(Farm.id == "f2")
    )
    return result.scalar_one()


@pytest.fixture
async def farm_no_crops(db: AsyncSession):
    user = User(id="u3", email="new@test.com", hashed_password="x", full_name="New Farmer")
    db.add(user)
    farm = Farm(
        id="f3", user_id="u3", name="Empty Farm", location_city="Mumbai",
        soil_type="Clay", total_area_acres=2.0
    )
    db.add(farm)
    await db.commit()
    result = await db.execute(
        select(Farm).options(selectinload(Farm.crops)).where(Farm.id == "f3")
    )
    return result.scalar_one()


def _mock_summary(items=None, last_updated=None, status=DataStatus.LIVE):
    return MarketSummaryResponse(
        items=items or [],
        last_updated=last_updated or datetime(2026, 9, 6, 10, 0, 0, tzinfo=timezone.utc),
        data_status=status,
    )


# ── Schema Tests ─────────────────────────────────────────────────────────────

class TestMarketContextSchemas:
    def test_market_price_context_defaults(self):
        price = MarketPriceContext(commodity="Wheat", modal_price=2500.0)
        assert price.market_name is None
        assert price.min_price is None
        assert price.max_price is None
        assert price.price_date is None
        assert price.price_change_pct is None
        # Verify removed fields are not present
        assert not hasattr(price, "trend")
        assert not hasattr(price, "unit")
        assert not hasattr(price, "state")
        assert not hasattr(price, "source")

    def test_market_context_defaults(self):
        ctx = MarketContext()
        assert ctx.prices == []
        assert ctx.data_status == "live"
        assert ctx.last_updated is None

    def test_unified_context_market_field(self):
        ctx = UnifiedContext()
        assert ctx.market is None


# ── ContextService._build_market_context Tests ──────────────────────────────

class TestBuildMarketContext:
    @pytest.mark.asyncio
    async def test_market_context_populated_for_active_crops(self, db, farm_with_active_crops):
        summary = _mock_summary(items=[
            MarketSummaryItem(
                commodity="Wheat", market_name="Azadpur Mandi",
                modal_price=2800.0, price_date=date(2026, 9, 5),
                price_change_pct=3.5, trend="up"
            ),
            MarketSummaryItem(
                commodity="Tomato", market_name="Pune Market",
                modal_price=1500.0, price_date=date(2026, 9, 5),
                price_change_pct=-1.0, trend="stable"
            ),
        ])

        service = ContextService(db)
        with patch.object(service.market_service, 'get_dashboard_summary', new_callable=AsyncMock, return_value=summary):
            market = await service._build_market_context(farm_with_active_crops)

        assert market is not None
        assert market.data_status == "live"
        assert len(market.prices) == 2

        wheat = next(p for p in market.prices if p.commodity == "Wheat")
        assert wheat.modal_price == 2800.0
        assert wheat.market_name == "Azadpur Mandi"
        assert wheat.price_change_pct == 3.5

    @pytest.mark.asyncio
    async def test_active_crop_filtering(self, db, farm_with_active_crops):
        service = ContextService(db)
        mock_get_summary = AsyncMock(return_value=_mock_summary())

        with patch.object(service.market_service, 'get_dashboard_summary', mock_get_summary):
            await service._build_market_context(farm_with_active_crops)

        mock_get_summary.assert_called_once()
        crop_names = mock_get_summary.call_args[0][0]
        assert "wheat" in crop_names
        assert "tomato" in crop_names
        assert "cotton" in crop_names
        assert "rice" not in crop_names

    @pytest.mark.asyncio
    async def test_only_harvested_returns_none(self, db, farm_with_only_harvested):
        service = ContextService(db)
        market = await service._build_market_context(farm_with_only_harvested)
        assert market is None

    @pytest.mark.asyncio
    async def test_no_crops_returns_none(self, db, farm_no_crops):
        service = ContextService(db)
        market = await service._build_market_context(farm_no_crops)
        assert market is None

    @pytest.mark.asyncio
    async def test_empty_market_data(self, db, farm_with_active_crops):
        empty_summary = _mock_summary(items=[], status=DataStatus.UNAVAILABLE)

        service = ContextService(db)
        with patch.object(service.market_service, 'get_dashboard_summary', new_callable=AsyncMock, return_value=empty_summary):
            market = await service._build_market_context(farm_with_active_crops)

        assert market is not None
        assert market.prices == []
        assert market.data_status == "unavailable"

    @pytest.mark.asyncio
    async def test_timestamp_and_status_preservation(self, db, farm_with_active_crops):
        ts = datetime(2026, 9, 6, 14, 30, 0, tzinfo=timezone.utc)
        summary = _mock_summary(
            items=[MarketSummaryItem(
                commodity="Wheat", market_name="Delhi",
                modal_price=2500.0, price_date=date(2026, 9, 6)
            )],
            last_updated=ts,
            status=DataStatus.CACHED,
        )

        service = ContextService(db)
        with patch.object(service.market_service, 'get_dashboard_summary', new_callable=AsyncMock, return_value=summary):
            market = await service._build_market_context(farm_with_active_crops)

        assert market is not None
        assert market.last_updated == ts
        assert market.data_status == "cached"

    @pytest.mark.asyncio
    async def test_market_service_failure_returns_none(self, db, farm_with_active_crops):
        service = ContextService(db)
        with patch.object(service.market_service, 'get_dashboard_summary', new_callable=AsyncMock, side_effect=Exception("DB connection lost")):
            market = await service._build_market_context(farm_with_active_crops)
        assert market is None

    @pytest.mark.asyncio
    async def test_existing_context_unaffected(self, db, farm_with_active_crops):
        service = ContextService(db)
        summary = _mock_summary(items=[
            MarketSummaryItem(
                commodity="Wheat", market_name="Test",
                modal_price=2000.0, price_date=date(2026, 9, 6)
            )
        ])
        with patch.object(service.market_service, 'get_dashboard_summary', new_callable=AsyncMock, return_value=summary):
            context = await service.build_unified_context(farm_with_active_crops)

        assert context.farm is not None
        assert context.market is not None
        assert len(context.market.prices) == 1

    @pytest.mark.asyncio
    async def test_market_failure_does_not_break_aira(self, db, farm_with_active_crops):
        service = ContextService(db)
        with patch.object(service.market_service, 'get_dashboard_summary', new_callable=AsyncMock, side_effect=RuntimeError("kaboom")):
            context = await service.build_unified_context(farm_with_active_crops)

        assert context.farm is not None
        assert context.market is None


"""
Tests for V5.3.3 — Price-Change Intelligence.

Verifies that the existing V5.1 MarketService logic safely and correctly
computes day-over-day price changes, and that this logic correctly
handles edge cases like missing data or zero-prices without requiring
new production code.
"""

import pytest
from datetime import date, timedelta
from app.models.market_price import MarketPrice
from app.services.market_service import MarketService
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base

@pytest.fixture
async def db():
    """Create in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session
    await engine.dispose()

@pytest.mark.asyncio
async def test_compute_price_change_positive_and_negative(db: AsyncSession):
    """Test standard price change calculations (positive and negative)."""
    service = MarketService(db)
    
    # Yesterday's data
    yesterday = date(2026, 8, 26)
    p1 = MarketPrice(commodity="Tomato", market_name="Azadpur", district="Delhi", state="Delhi", min_price=2400.0, max_price=2600.0, modal_price=2500.0, price_date=yesterday)
    p2 = MarketPrice(commodity="Rice", market_name="Azadpur", district="Delhi", state="Delhi", min_price=2900.0, max_price=3100.0, modal_price=3000.0, price_date=yesterday)
    db.add_all([p1, p2])
    await db.commit()

    # Today's price (Positive change for Tomato, Negative for Rice)
    today = date(2026, 8, 27)
    today_tomato = MarketPrice(commodity="Tomato", market_name="Azadpur", district="Delhi", state="Delhi", min_price=2700.0, max_price=2900.0, modal_price=2800.0, price_date=today)
    today_rice = MarketPrice(commodity="Rice", market_name="Azadpur", district="Delhi", state="Delhi", min_price=2800.0, max_price=3000.0, modal_price=2900.0, price_date=today)
    
    change_tomato = await service._compute_price_change(today_tomato)
    change_rice = await service._compute_price_change(today_rice)
    
    # Tomato: ((2800 - 2500) / 2500) * 100 = 12.0%
    assert change_tomato == 12.0
    
    # Rice: ((2900 - 3000) / 3000) * 100 = -3.333% -> -3.3%
    assert change_rice == -3.3


@pytest.mark.asyncio
async def test_compute_price_change_no_previous_data(db: AsyncSession):
    """Test that missing previous data returns None safely."""
    service = MarketService(db)
    
    # Only today's data exists
    today = date(2026, 8, 27)
    today_wheat = MarketPrice(commodity="Wheat", market_name="Azadpur", district="Delhi", state="Delhi", min_price=2100.0, max_price=2300.0, modal_price=2200.0, price_date=today)
    
    change = await service._compute_price_change(today_wheat)
    assert change is None


@pytest.mark.asyncio
async def test_compute_price_change_zero_previous_price(db: AsyncSession):
    """Test that a previous price of 0 does not cause DivisionByZero."""
    service = MarketService(db)
    
    # Yesterday's data has a 0 modal price (e.g. data error or market closed)
    yesterday = date(2026, 8, 26)
    p_zero = MarketPrice(commodity="Corn", market_name="Azadpur", district="Delhi", state="Delhi", min_price=0.0, max_price=0.0, modal_price=0.0, price_date=yesterday)
    db.add(p_zero)
    await db.commit()

    # Today's data
    today = date(2026, 8, 27)
    today_corn = MarketPrice(commodity="Corn", market_name="Azadpur", district="Delhi", state="Delhi", min_price=1400.0, max_price=1600.0, modal_price=1500.0, price_date=today)
    
    change = await service._compute_price_change(today_corn)
    
    # Should safely return None instead of crashing
    assert change is None

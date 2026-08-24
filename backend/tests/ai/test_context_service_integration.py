"""
Integration tests for ContextService and V4 Phase 1 Step 6.
"""

import pytest
from datetime import date, datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select

from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.fertilizer import FertilizerLog
from app.ai.services.context_service import ContextService


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
async def seeded(db: AsyncSession):
    now = datetime.now(timezone.utc)

    user = User(id="u1", email="a@b.com", hashed_password="x", full_name="A")
    db.add(user)

    farm_a = Farm(id="fA", user_id="u1", name="Farm A", location_city="Delhi", soil_type="Loamy", total_area_acres=10.0)
    db.add(farm_a)

    crop_a1 = Crop(
        id="cA1", farm_id="fA", crop_name="Wheat", season="Rabi",
        planting_date=date(2025, 11, 1), actual_harvest_date=date(2026, 3, 15),
        area_acres=5.0, status="harvested", variety="HD-2967",
        yield_amount=200.0, yield_unit="kg",
    )
    db.add(crop_a1)
    
    # Add a fertilizer record so history is not completely empty but has counts
    db.add(FertilizerLog(
        id="fl_1", crop_id="cA1", date=date(2025, 12, 1),
        fertilizer_type="Urea", quantity=10.0, unit="kg",
    ))

    await db.commit()
    
    # We must load the farm exactly as ContextService expects (with crops eager loaded)
    result = await db.execute(select(Farm).options(selectinload(Farm.crops)).where(Farm.id == "fA"))
    farm = result.scalar_one()
    
    return farm


@pytest.mark.asyncio
async def test_context_service_includes_history_for_valid_farm(db, seeded):
    service = ContextService(db)
    
    context = await service.build_unified_context(farm=seeded)
    
    # Verify history was populated
    assert context.history is not None
    assert len(context.history.past_crops) == 1
    assert context.history.past_crops[0].crop_name == "Wheat"
    assert context.history.past_crops[0].fertilizer_applications == 1
    
    # Verify existing context remains intact
    assert context.farm is not None
    assert context.farm.name == "Farm A"
    assert len(context.farm.crops) == 1
    
    # Because we mocked nothing for weather/knowledge, they might be empty/None, which is expected.
    assert context.weather is None or isinstance(context.weather, object)


@pytest.mark.asyncio
async def test_context_service_empty_farm_history(db):
    # Farm without any crops or history
    user = User(id="u2", email="b@b.com", hashed_password="y", full_name="B")
    farm_empty = Farm(id="fEmpty", user_id="u2", name="Empty Farm", location_city="Mumbai", soil_type="Clay", total_area_acres=5.0)
    db.add_all([user, farm_empty])
    await db.commit()
    
    result = await db.execute(select(Farm).options(selectinload(Farm.crops)).where(Farm.id == "fEmpty"))
    farm = result.scalar_one()

    service = ContextService(db)
    context = await service.build_unified_context(farm=farm)
    
    # History should be a valid FarmHistoryContext but empty
    assert context.history is not None
    assert context.history.past_crops == []
    assert context.history.performance_summary is None


@pytest.mark.asyncio
async def test_context_service_invalid_farm(db):
    service = ContextService(db)
    # Pass a Farm with no ID
    farm_invalid = Farm(name="No ID Farm", location_city="Nowhere", soil_type="None", total_area_acres=0)
    
    context = await service.build_unified_context(farm=farm_invalid)
    
    # History should gracefully be None, falling back safely
    assert context.history is None
    # And farm context still gets built!
    assert context.farm is not None
    assert context.farm.name == "No ID Farm"

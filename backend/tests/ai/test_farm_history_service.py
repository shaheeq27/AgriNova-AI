"""
Tests for V4 Phase 1 Step 5 — FarmHistoryService.
"""

from datetime import date, datetime, timezone, timedelta
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.fertilizer import FertilizerLog
from app.models.irrigation import IrrigationLog
from app.models.disease import DiseaseRecord

from app.ai.services.farm_history_service import FarmHistoryService


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
    farm_b = Farm(id="fB", user_id="u1", name="Farm B", location_city="Mumbai", soil_type="Clay", total_area_acres=5.0)
    db.add_all([farm_a, farm_b])

    # Crops — Farm A
    crop_a1 = Crop(
        id="cA1", farm_id="fA", crop_name="Wheat", season="Rabi",
        planting_date=date(2025, 11, 1), actual_harvest_date=date(2026, 3, 15),
        area_acres=5.0, status="harvested", variety="HD-2967",
        yield_amount=200.0, yield_unit="kg",
    )
    crop_a2 = Crop(
        id="cA2", farm_id="fA", crop_name="Maize", season="Rabi",
        planting_date=date(2026, 11, 1), area_acres=3.0, status="active",
        yield_amount=1.5, yield_unit="tons",
    )
    
    # Crops — Farm B
    crop_b1 = Crop(
        id="cB1", farm_id="fB", crop_name="Cotton", season="Kharif",
        area_acres=5.0, status="active",
    )
    db.add_all([crop_a1, crop_a2, crop_b1])
    await db.flush()

    # Fertilizer — Farm A
    for i in range(5):
        db.add(FertilizerLog(
            id=f"fl_a_{i}", crop_id="cA1", date=date(2025, 12, 1 + i),
            fertilizer_type="Urea", quantity=10.0, unit="kg",
        ))
        
    # Irrigation — Farm A
    for i in range(5):
        db.add(IrrigationLog(
            id=f"il_a_{i}", crop_id="cA1", date=date(2025, 12, 10 + i),
        ))
        
    # Disease — Farm A
    db.add(DiseaseRecord(
        id="dr_a_0", crop_id="cA1", disease_name="Rust",
        severity="high", treatment_applied="Fungicide X", outcome="resolved successfully",
        status="resolved", detected_at=now - timedelta(days=60),
    ))
    db.add(DiseaseRecord(
        id="dr_a_1", crop_id="cA2", disease_name="Blight",
        severity="medium", status="active",
        detected_at=now - timedelta(days=5),
    ))

    # Disease — Farm B (decoy)
    db.add(DiseaseRecord(
        id="dr_b_0", crop_id="cB1", disease_name="Wilt",
        status="active", detected_at=now,
    ))

    await db.commit()
    return {"farm_a": "fA", "farm_b": "fB"}


@pytest.mark.asyncio
async def test_complete_history(db, seeded):
    service = FarmHistoryService(db)
    ctx = await service.build_history_context(seeded["farm_a"])

    assert len(ctx.past_crops) == 2
    wheat = next(c for c in ctx.past_crops if c.crop_name == "Wheat")
    assert wheat.fertilizer_applications == 5
    assert wheat.irrigation_applications == 5
    assert wheat.disease_count == 1
    
    assert len(ctx.recent_diseases) == 2
    assert "Rust" in ctx.recent_diseases[1]
    assert "Fungicide X" in ctx.recent_diseases[1]
    
    assert ctx.performance_summary is not None
    assert "2 recorded crops; 1 harvested and 0 abandoned." in ctx.performance_summary
    assert "2 crops have recorded yields." in ctx.performance_summary
    assert "5 fertilizer applications and 5 irrigation events recorded." in ctx.performance_summary
    assert "2 disease records: 1 resolved, 1 active." in ctx.performance_summary


@pytest.mark.asyncio
async def test_farm_isolation(db, seeded):
    service = FarmHistoryService(db)
    ctx = await service.build_history_context(seeded["farm_a"])
    
    for c in ctx.past_crops:
        assert c.crop_name != "Cotton"
        
    for d in ctx.recent_diseases:
        assert "Wilt" not in d


@pytest.mark.asyncio
async def test_empty_farm(db, seeded):
    service = FarmHistoryService(db)
    ctx = await service.build_history_context("nonexistent")
    
    assert ctx.past_crops == []
    assert ctx.recent_diseases == []
    assert ctx.seasonal_patterns == []
    assert ctx.performance_summary is None


@pytest.mark.asyncio
async def test_optional_values_handled(db, seeded):
    service = FarmHistoryService(db)
    ctx = await service.build_history_context(seeded["farm_b"])
    
    assert len(ctx.past_crops) == 1
    cotton = ctx.past_crops[0]
    assert cotton.yield_amount is None
    assert cotton.variety is None
    
    assert len(ctx.recent_diseases) == 1
    assert "Wilt" in ctx.recent_diseases[0]


@pytest.mark.asyncio
async def test_mixed_yield_units(db, seeded):
    service = FarmHistoryService(db)
    ctx = await service.build_history_context(seeded["farm_a"])
    
    assert "200.0 kg across 1 crop and 1.5 tons across 1 crop" in ctx.performance_summary


@pytest.mark.asyncio
async def test_seasonal_patterns(db, seeded):
    service = FarmHistoryService(db)
    ctx = await service.build_history_context(seeded["farm_a"])
    
    assert len(ctx.seasonal_patterns) == 1
    assert ctx.seasonal_patterns[0] == "Rabi: Maize, Wheat"


@pytest.mark.asyncio
async def test_limits(db, seeded):
    service = FarmHistoryService(db)
    ctx = await service.build_history_context(seeded["farm_a"], limit=1)
    
    assert len(ctx.past_crops) == 1
    assert len(ctx.recent_diseases) == 1


@pytest.mark.asyncio
async def test_serialization(db, seeded):
    service = FarmHistoryService(db)
    ctx = await service.build_history_context(seeded["farm_a"])
    
    dump = ctx.model_dump()
    assert len(dump["past_crops"]) == 2
    assert "seasonal_patterns" in dump

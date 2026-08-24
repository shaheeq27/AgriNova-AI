"""
Tests for V4 Phase 1 Step 3 — HistoryRepository.

Covers farm isolation, cross-entity queries, limits, ordering,
empty-farm safety, performance summary, and mixed yield-unit handling.
"""

import json
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
from app.models.activity_log import ActivityLog

from app.repositories.history_repo import HistoryRepository


# ── Fixtures ──────────────────────────────────────────────────────────

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
    """Seed two farms with varied data for isolation and coverage tests."""
    now = datetime.now(timezone.utc)

    # Users
    user = User(id="u1", email="a@b.com", hashed_password="x", full_name="A")
    db.add(user)

    # Farm A (target)
    farm_a = Farm(
        id="fA", user_id="u1", name="Farm A",
        location_city="Delhi", soil_type="Loamy", total_area_acres=10.0,
    )
    # Farm B (isolation decoy)
    farm_b = Farm(
        id="fB", user_id="u1", name="Farm B",
        location_city="Mumbai", soil_type="Clay", total_area_acres=5.0,
    )
    db.add_all([farm_a, farm_b])

    # Crops — Farm A
    crop_a1 = Crop(
        id="cA1", farm_id="fA", crop_name="Wheat", season="Rabi",
        planting_date=date(2025, 11, 1), actual_harvest_date=date(2026, 3, 15),
        area_acres=5.0, status="harvested", variety="HD-2967",
        yield_amount=200.0, yield_unit="kg",
    )
    crop_a2 = Crop(
        id="cA2", farm_id="fA", crop_name="Rice", season="Kharif",
        planting_date=date(2026, 6, 1), area_acres=3.0, status="active",
        variety="Basmati-1121", yield_amount=1.5, yield_unit="tons",
    )
    crop_a3 = Crop(
        id="cA3", farm_id="fA", crop_name="Maize", season="Rabi",
        planting_date=date(2024, 11, 1), area_acres=2.0, status="abandoned",
    )

    # Crops — Farm B (decoy)
    crop_b1 = Crop(
        id="cB1", farm_id="fB", crop_name="Cotton", season="Kharif",
        planting_date=date(2026, 7, 1), area_acres=5.0, status="active",
    )
    db.add_all([crop_a1, crop_a2, crop_a3, crop_b1])
    await db.flush()

    # Fertilizer logs — Farm A
    for i in range(5):
        db.add(FertilizerLog(
            id=f"fl_a_{i}", crop_id="cA1", date=date(2025, 12, 1 + i),
            fertilizer_type="Urea", quantity=10.0 + i, unit="kg",
            application_method="Broadcasting", growth_stage="Vegetative",
        ))
    # Fertilizer log — Farm B (decoy)
    db.add(FertilizerLog(
        id="fl_b_0", crop_id="cB1", date=date(2026, 8, 1),
        fertilizer_type="DAP", quantity=20.0, unit="kg",
    ))

    # Irrigation logs — Farm A (across two crops)
    for i in range(4):
        db.add(IrrigationLog(
            id=f"il_a_{i}", crop_id="cA1", date=date(2025, 12, 10 + i),
            water_amount_liters=500.0, duration_minutes=30.0,
            method="Drip", growth_stage="Vegetative",
        ))
    db.add(IrrigationLog(
        id="il_a_4", crop_id="cA2", date=date(2026, 7, 1),
        water_amount_liters=800.0, method="Flood",
    ))
    # Irrigation — Farm B (decoy)
    db.add(IrrigationLog(
        id="il_b_0", crop_id="cB1", date=date(2026, 8, 5),
        water_amount_liters=100.0,
    ))

    # Disease records — Farm A
    db.add(DiseaseRecord(
        id="dr_a_0", crop_id="cA1", disease_name="Rust",
        severity="high", symptoms_observed="yellow spots",
        treatment_applied="Fungicide X", outcome="resolved successfully",
        status="resolved", detected_at=now - timedelta(days=60),
        resolved_at=now - timedelta(days=30),
    ))
    db.add(DiseaseRecord(
        id="dr_a_1", crop_id="cA2", disease_name="Blight",
        severity="medium", status="active",
        detected_at=now - timedelta(days=5),
    ))
    # Disease — Farm B (decoy)
    db.add(DiseaseRecord(
        id="dr_b_0", crop_id="cB1", disease_name="Wilt",
        severity="low", status="active",
        detected_at=now - timedelta(days=2),
    ))

    # Activity logs — Farm A
    db.add(ActivityLog(
        id="al_a_0", user_id="u1", farm_id="fA", crop_id="cA1",
        action="crop_harvested", entity_type="crop", entity_id="cA1",
        description="Harvested Wheat", metadata_json=json.dumps({"yield_amount": 200}),
        created_at=now - timedelta(days=10),
    ))
    db.add(ActivityLog(
        id="al_a_1", user_id="u1", farm_id="fA", crop_id="cA1",
        action="fertilizer_applied", entity_type="fertilizer", entity_id="fl_a_0",
        description="Applied Urea",
        created_at=now - timedelta(days=20),
    ))
    db.add(ActivityLog(
        id="al_a_2", user_id="u1", farm_id="fA", crop_id="cA2",
        action="irrigation_performed", entity_type="irrigation", entity_id="il_a_4",
        description="Irrigated Rice",
        created_at=now - timedelta(days=1),
    ))
    # Activity — Farm B (decoy)
    db.add(ActivityLog(
        id="al_b_0", user_id="u1", farm_id="fB", crop_id="cB1",
        action="crop_planted", entity_type="crop", entity_id="cB1",
        description="Planted Cotton",
    ))

    await db.commit()
    return {"farm_a": "fA", "farm_b": "fB"}


# ── Test A: Crop history returns only requested farm ──────────────────

@pytest.mark.asyncio
async def test_crop_history_farm_isolation(db, seeded):
    repo = HistoryRepository(db)
    crops = await repo.get_crop_history(seeded["farm_a"])
    crop_ids = [c.id for c in crops]

    assert "cA1" in crop_ids
    assert "cA2" in crop_ids
    assert "cA3" in crop_ids
    assert "cB1" not in crop_ids  # Farm B crop excluded


# ── Test B: Crop history includes V4 fields ───────────────────────────

@pytest.mark.asyncio
async def test_crop_history_includes_v4_fields(db, seeded):
    repo = HistoryRepository(db)
    crops = await repo.get_crop_history(seeded["farm_a"])
    wheat = next(c for c in crops if c.crop_name == "Wheat")

    assert wheat.variety == "HD-2967"
    assert wheat.yield_amount == 200.0
    assert wheat.yield_unit == "kg"


# ── Test C: Fertilizer history spans multiple crops ───────────────────

@pytest.mark.asyncio
async def test_fertilizer_history_cross_crop(db, seeded):
    repo = HistoryRepository(db)
    ferts = await repo.get_fertilizer_history(seeded["farm_a"])

    assert len(ferts) == 5
    assert all(f["crop_name"] == "Wheat" for f in ferts)
    # Verify dict keys
    assert "fertilizer_type" in ferts[0]
    assert "crop_name" in ferts[0]


# ── Test D: Fertilizer isolation — no other farm's records ────────────

@pytest.mark.asyncio
async def test_fertilizer_history_farm_isolation(db, seeded):
    repo = HistoryRepository(db)
    ferts = await repo.get_fertilizer_history(seeded["farm_a"])
    assert all(f["crop_id"] != "cB1" for f in ferts)

    ferts_b = await repo.get_fertilizer_history(seeded["farm_b"])
    assert len(ferts_b) == 1
    assert ferts_b[0]["fertilizer_type"] == "DAP"


# ── Test E: Irrigation history spans multiple crops ───────────────────

@pytest.mark.asyncio
async def test_irrigation_history_cross_crop(db, seeded):
    repo = HistoryRepository(db)
    irrs = await repo.get_irrigation_history(seeded["farm_a"])

    assert len(irrs) == 5
    crop_names = {i["crop_name"] for i in irrs}
    assert "Wheat" in crop_names
    assert "Rice" in crop_names


# ── Test F: Disease history includes treatment/outcome ────────────────

@pytest.mark.asyncio
async def test_disease_history_treatment_outcome(db, seeded):
    repo = HistoryRepository(db)
    diseases = await repo.get_disease_history(seeded["farm_a"])

    assert len(diseases) == 2
    rust = next(d for d in diseases if d["disease_name"] == "Rust")
    assert rust["treatment_applied"] == "Fungicide X"
    assert rust["outcome"] == "resolved successfully"
    assert rust["status"] == "resolved"


# ── Test G: Activity history returns V4 events ────────────────────────

@pytest.mark.asyncio
async def test_activity_history_v4_events(db, seeded):
    repo = HistoryRepository(db)
    activities = await repo.get_activity_history(seeded["farm_a"])

    actions = [a["action"] for a in activities]
    assert "crop_harvested" in actions
    assert "fertilizer_applied" in actions
    assert "irrigation_performed" in actions
    # Farm B activity excluded
    assert all(a["action"] != "crop_planted" or a["crop_id"] != "cB1" for a in activities)


# ── Test H: Limits are respected ─────────────────────────────────────

@pytest.mark.asyncio
async def test_limits_respected(db, seeded):
    repo = HistoryRepository(db)

    ferts = await repo.get_fertilizer_history(seeded["farm_a"], limit=2)
    assert len(ferts) == 2

    irrs = await repo.get_irrigation_history(seeded["farm_a"], limit=3)
    assert len(irrs) == 3

    diseases = await repo.get_disease_history(seeded["farm_a"], limit=1)
    assert len(diseases) == 1

    activities = await repo.get_activity_history(seeded["farm_a"], limit=1)
    assert len(activities) == 1


# ── Test I: Results ordered newest first ──────────────────────────────

@pytest.mark.asyncio
async def test_ordering_newest_first(db, seeded):
    repo = HistoryRepository(db)

    ferts = await repo.get_fertilizer_history(seeded["farm_a"])
    dates = [f["date"] for f in ferts]
    assert dates == sorted(dates, reverse=True)

    activities = await repo.get_activity_history(seeded["farm_a"])
    timestamps = [a["created_at"] for a in activities]
    assert timestamps == sorted(timestamps, reverse=True)


# ── Test J: Empty farm returns empty results ──────────────────────────

@pytest.mark.asyncio
async def test_empty_farm(db, seeded):
    repo = HistoryRepository(db)

    assert await repo.get_crop_history("nonexistent") == []
    assert await repo.get_fertilizer_history("nonexistent") == []
    assert await repo.get_irrigation_history("nonexistent") == []
    assert await repo.get_disease_history("nonexistent") == []
    assert await repo.get_activity_history("nonexistent") == []

    summary = await repo.get_farm_performance_summary("nonexistent")
    assert summary["total_crops"] == 0
    assert summary["yield_by_unit"] == []


# ── Test K: Performance summary calculations ─────────────────────────

@pytest.mark.asyncio
async def test_performance_summary(db, seeded):
    repo = HistoryRepository(db)
    summary = await repo.get_farm_performance_summary(seeded["farm_a"])

    assert summary["total_crops"] == 3
    assert summary["harvested_crops"] == 1
    assert summary["abandoned_crops"] == 1
    assert summary["crops_with_yield"] == 2
    assert summary["total_fertilizer_applications"] == 5
    assert summary["total_irrigation_events"] == 5
    assert summary["total_disease_records"] == 2
    assert summary["resolved_disease_count"] == 1
    assert summary["active_disease_count"] == 1


# ── Test L: Mixed yield units do not produce invalid average ──────────

@pytest.mark.asyncio
async def test_mixed_yield_units_safe(db, seeded):
    repo = HistoryRepository(db)
    summary = await repo.get_farm_performance_summary(seeded["farm_a"])

    # yield_by_unit must separate kg and tons — never a single blended avg
    units = {entry["unit"] for entry in summary["yield_by_unit"]}
    assert "kg" in units
    assert "tons" in units
    assert len(summary["yield_by_unit"]) == 2

    kg_entry = next(e for e in summary["yield_by_unit"] if e["unit"] == "kg")
    assert kg_entry["avg_yield"] == 200.0
    assert kg_entry["count"] == 1

    tons_entry = next(e for e in summary["yield_by_unit"] if e["unit"] == "tons")
    assert tons_entry["avg_yield"] == 1.5
    assert tons_entry["count"] == 1


# ── Test M: Existing repository functionality unaffected ──────────────

@pytest.mark.asyncio
async def test_existing_repos_unaffected(db, seeded):
    """Verify that importing HistoryRepository does not break other repos."""
    from app.repositories.crop_repo import CropRepository
    from app.repositories.farm_repo import FarmRepository
    from app.repositories.activity_repo import ActivityRepository

    crop_repo = CropRepository(db)
    crops = await crop_repo.get_by_farm_id("fA")
    assert len(crops) == 3

    farm_repo = FarmRepository(db)
    farm = await farm_repo.get_by_id("fA")
    assert farm is not None
    assert farm.name == "Farm A"

    act_repo = ActivityRepository(db)
    feed = await act_repo.get_feed("u1", farm_id="fA")
    assert len(feed) == 3

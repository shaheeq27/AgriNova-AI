"""
Tests for HistoricalInsightsService and deterministic insight extraction.
"""

import pytest
from datetime import date
from app.ai.schemas.context import (
    FarmHistoryContext,
    CropHistoryEntry,
    UnifiedContext,
)
from app.ai.services.historical_insights_service import HistoricalInsightsService


def test_generate_insights_empty_history():
    service = HistoricalInsightsService()
    history = FarmHistoryContext()

    insights = service.generate_insights(history)

    assert not insights.successful_crops
    assert not insights.recurring_diseases
    assert not insights.seasonal_crop_patterns
    assert not insights.historical_yield_observations


def test_generate_insights_successful_crops():
    service = HistoricalInsightsService()
    history = FarmHistoryContext(
        past_crops=[
            # Harvested with yield -> successful
            CropHistoryEntry(crop_name="Wheat", variety="A", season="Rabi", status="harvested", yield_amount=100.0, yield_unit="kg"),
            # Active -> not successful
            CropHistoryEntry(crop_name="Rice", season="Kharif", status="active", yield_amount=0.0),
            # Harvested but no yield -> not successful
            CropHistoryEntry(crop_name="Maize", season="Kharif", status="harvested", yield_amount=None),
        ]
    )

    insights = service.generate_insights(history)

    assert insights.successful_crops == ["Wheat (A)"]


def test_generate_insights_recurring_diseases():
    service = HistoricalInsightsService()
    history = FarmHistoryContext(
        recent_diseases=[
            "Rust — high severity — resolved",
            "Blight — moderate severity",
            "Rust — low severity",
        ]
    )

    insights = service.generate_insights(history)

    # Rust appears twice, Blight appears once
    assert "Rust" in insights.recurring_diseases
    assert "Blight" not in insights.recurring_diseases


def test_generate_insights_yield_units_separated():
    service = HistoricalInsightsService()
    history = FarmHistoryContext(
        past_crops=[
            CropHistoryEntry(crop_name="Wheat", season="Rabi", status="harvested", yield_amount=200.0, yield_unit="kg"),
            CropHistoryEntry(crop_name="Wheat", season="Rabi", status="harvested", yield_amount=1.5, yield_unit="tons"),
            CropHistoryEntry(crop_name="Maize", season="Rabi", status="harvested", yield_amount=300.0, yield_unit="kg"),
        ]
    )

    insights = service.generate_insights(history)

    assert "Wheat: 200.0 kg, 1.5 tons" in insights.historical_yield_observations
    assert "Maize: 300.0 kg" in insights.historical_yield_observations


def test_generate_insights_seasonal_patterns():
    service = HistoricalInsightsService()
    history = FarmHistoryContext(
        seasonal_patterns=["Kharif: Rice", "Rabi: Wheat"]
    )

    insights = service.generate_insights(history)
    assert insights.seasonal_crop_patterns == ["Kharif: Rice", "Rabi: Wheat"]



# -----------------------------------------------------------------------------
# RECONSTRUCTED PHASE 2 STEP 2 TESTS
# -----------------------------------------------------------------------------
import pytest
from datetime import date, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.disease import DiseaseRecord
from app.models.fertilizer import FertilizerLog
from app.models.irrigation import IrrigationLog
from app.ai.schemas.historical_analysis import HistoricalInsightsContext
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.database import Base
from app.ai.services.historical_insights_service import HistoricalInsightsService

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session

@pytest.mark.asyncio
async def test_compute_insights_context_empty(db_session: AsyncSession):
    service = HistoricalInsightsService()
    ctx = await service.compute_insights_context(db_session, "fake_farm")
    assert isinstance(ctx, HistoricalInsightsContext)
    assert len(ctx.crop_performance) == 0

@pytest.mark.asyncio
async def test_compute_insights_context_comprehensive(db_session: AsyncSession):
    u = User(id="u1", email="a@a.com", hashed_password="x", full_name="A")
    f = Farm(id="farm1", user_id="u1", name="F1", location_city="C", soil_type="S", total_area_acres=10.0)

    c1 = Crop(id="c1", farm_id="farm1", crop_name="Wheat", variety="Alpha", season="Rabi",
              planting_date=date(2020, 1, 1), status="harvested", yield_amount=100.0, yield_unit="kg", area_acres=1.0)
    c2 = Crop(id="c2", farm_id="farm1", crop_name="Wheat", variety="Alpha", season="Rabi",
              planting_date=date(2021, 1, 1), status="harvested", yield_amount=110.0, yield_unit="kg", area_acres=1.0)
    c3 = Crop(id="c3", farm_id="farm1", crop_name="Wheat", variety="Alpha", season="Kharif",
              planting_date=date(2022, 1, 1), status="active", yield_amount=None, yield_unit="kg", area_acres=1.0)

    c4 = Crop(id="c4", farm_id="farm1", crop_name="Rice", variety="Beta", season="Kharif",
              planting_date=date(2021, 5, 1), status="harvested", yield_amount=2.0, yield_unit="tons", area_acres=2.0)

    m1 = Crop(id="m1", farm_id="farm1", crop_name="Maize", season="Zaid", planting_date=date(2020, 1, 1), status="harvested", yield_amount=100.0, yield_unit="kg", area_acres=1.0)
    m2 = Crop(id="m2", farm_id="farm1", crop_name="Maize", season="Zaid", planting_date=date(2021, 1, 1), status="harvested", yield_amount=100.0, yield_unit="kg", area_acres=1.0)
    m3 = Crop(id="m3", farm_id="farm1", crop_name="Maize", season="Zaid", planting_date=date(2022, 1, 1), status="harvested", yield_amount=120.0, yield_unit="kg", area_acres=1.0)
    m4 = Crop(id="m4", farm_id="farm1", crop_name="Maize", season="Zaid", planting_date=date(2023, 1, 1), status="harvested", yield_amount=120.0, yield_unit="kg", area_acres=1.0)

    s1 = Crop(id="s1", farm_id="farm1", crop_name="Soy", season="Kharif", planting_date=date(2020, 1, 1), status="harvested", yield_amount=100.0, yield_unit="kg", area_acres=1.0)
    s2 = Crop(id="s2", farm_id="farm1", crop_name="Soy", season="Kharif", planting_date=date(2021, 1, 1), status="harvested", yield_amount=80.0, yield_unit="kg", area_acres=1.0)

    d1 = DiseaseRecord(id="d1", crop_id="c1", disease_name="Rust", status="resolved", severity="high", treatment_applied="Fungicide A")
    d2 = DiseaseRecord(id="d2", crop_id="c1", disease_name="Rust", status="active", severity="medium", treatment_applied="Fungicide B")
    d3 = DiseaseRecord(id="d3", crop_id="c4", disease_name="Blight", status="active", severity="low", treatment_applied="None")

    f1 = FertilizerLog(id="f1", crop_id="c1", date=date(2020, 2, 1), fertilizer_type="Urea", quantity=50, unit="kg", application_method="Broadcast")
    f2 = FertilizerLog(id="f2", crop_id="c1", date=date(2020, 3, 1), fertilizer_type="DAP", quantity=30, unit="kg", application_method="Drip")

    i1 = IrrigationLog(id="i1", crop_id="c1", date=date(2020, 2, 15), water_amount_liters=1000, method="Drip")

    db_session.add_all([u, f, c1, c2, c3, c4, m1, m2, m3, m4, s1, s2, d1, d2, d3, f1, f2, i1])
    await db_session.commit()

    service = HistoricalInsightsService()
    ctx = await service.compute_insights_context(db_session, "farm1")

    wheat_perf = next(p for p in ctx.crop_performance if p.crop_name == "Wheat")
    assert wheat_perf.crops_observed == 3
    assert wheat_perf.harvested_count == 2
    assert set(wheat_perf.seasons_observed) == {"Rabi", "Kharif"}
    assert wheat_perf.average_yield == 105.0
    assert wheat_perf.best_yield == 110.0
    assert wheat_perf.worst_yield == 100.0
    assert wheat_perf.confidence == 0.8
    assert wheat_perf.disease_records == 2
    assert wheat_perf.fertilizer_applications == 2
    assert wheat_perf.irrigation_applications == 1

    maize_perf = next(p for p in ctx.crop_performance if p.crop_name == "Maize")
    assert maize_perf.confidence == 0.95

    wheat_trend = next(t for t in ctx.yield_trends if t.crop_name == "Wheat")
    assert wheat_trend.trend_direction == "increasing"

    maize_trend = next(t for t in ctx.yield_trends if t.crop_name == "Maize")
    assert maize_trend.trend_direction == "increasing"

    soy_trend = next(t for t in ctx.yield_trends if t.crop_name == "Soy")
    assert soy_trend.trend_direction == "decreasing"

    rice_trend = next(t for t in ctx.yield_trends if t.crop_name == "Rice")
    assert rice_trend.trend_direction is None

    rust = next(d for d in ctx.disease_patterns if d.disease_name == "Rust")
    assert rust.affected_crop == "Wheat"
    assert rust.occurrence_count == 2
    assert rust.resolved_count == 1
    assert rust.active_count == 1

    urea = next(f for f in ctx.input_usage if f.input_type == "Urea")
    assert urea.total_quantity == 50.0
    assert urea.quantity_unit == "kg"

    dap = next(f for f in ctx.input_usage if f.input_type == "DAP")
    assert dap.total_quantity == 30.0

    irr = next(i for i in ctx.input_usage if i.input_type == "Irrigation")
    assert irr.total_quantity == 1000.0
    assert irr.quantity_unit == "liters"
    assert irr.common_application_method == "Drip"

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.schemas.context import UnifiedContext, FarmHistoryContext
from app.ai.schemas.historical_analysis import HistoricalInsightsContext
from app.ai.services.context_service import ContextService
from app.ai.services.historical_insights_service import HistoricalInsightsService
from app.ai.services.context_formatter import format_context
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.database import Base
from app.repositories.farm_repo import FarmRepository

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session

@pytest.mark.asyncio
async def test_valid_farm_receives_historical_insights(db: AsyncSession):
    user = User(id="u1", email="a@a.com", hashed_password="x", full_name="A")
    farm = Farm(id="f1", user_id="u1", name="Farm", location_city="Pune", soil_type="Black", total_area_acres=10.0)
    crop = Crop(id="c1", farm_id="f1", crop_name="Wheat", season="Rabi", 
                actual_harvest_date=date(2025, 1, 1), status="harvested", yield_amount=500.0, yield_unit="kg", area_acres=5.0)
    db.add_all([user, farm, crop])
    await db.commit()
    
    farm_loaded = await FarmRepository(db).get_by_id("f1")

    service = ContextService(db)
    ctx = await service.build_unified_context(farm_loaded, "hello")
    
    assert ctx.historical_insights is not None
    assert isinstance(ctx.historical_insights, HistoricalInsightsContext)
    assert ctx.history is not None
    assert isinstance(ctx.history, FarmHistoryContext)
    assert ctx.farm is not None
    assert len(ctx.historical_insights.crop_performance) == 1
    assert len(ctx.historical_insights.yield_trends) == 1

@pytest.mark.asyncio
async def test_empty_farm_receives_empty_insights(db: AsyncSession):
    user = User(id="u2", email="b@b.com", hashed_password="x", full_name="B")
    farm = Farm(id="f2", user_id="u2", name="Farm 2", location_city="Pune", soil_type="Black", total_area_acres=10.0)
    db.add_all([user, farm])
    await db.commit()
    
    farm_loaded = await FarmRepository(db).get_by_id("f2")
    service = ContextService(db)
    ctx = await service.build_unified_context(farm_loaded, "hello")
    
    assert ctx.historical_insights is not None
    assert isinstance(ctx.historical_insights, HistoricalInsightsContext)
    assert len(ctx.historical_insights.crop_performance) == 0

@pytest.mark.asyncio
async def test_invalid_farm_receives_none(db: AsyncSession):
    service = ContextService(db)
    farm_invalid = Farm(name="No ID Farm", location_city="Nowhere", soil_type="None", total_area_acres=0)
    farm_invalid.crops = []
    ctx = await service.build_unified_context(farm_invalid, "hello")
    assert ctx.historical_insights is None

@pytest.mark.asyncio
async def test_service_exception_is_gracefully_isolated(db: AsyncSession, monkeypatch):
    user = User(id="u3", email="c@c.com", hashed_password="x", full_name="C")
    farm = Farm(id="f3", user_id="u3", name="Farm 3", location_city="Pune", soil_type="Black", total_area_acres=10.0)
    db.add_all([user, farm])
    await db.commit()

    farm_loaded = await FarmRepository(db).get_by_id("f3")
    service = ContextService(db)
    
    async def mock_compute(*args, **kwargs):
        raise ValueError("Simulated computation failure")
        
    monkeypatch.setattr(service.insights_service, "compute_insights_context", mock_compute)
    
    ctx = await service.build_unified_context(farm_loaded, "hello")
    
    assert ctx.historical_insights is None
    assert ctx.farm is not None
    assert ctx.history is not None

def test_unified_context_serializes_insights():
    from app.ai.schemas.historical_analysis import CropPerformanceInsight
    insight = HistoricalInsightsContext(
        crop_performance=[CropPerformanceInsight(
            crop_name="Wheat", variety="A", seasons_observed=["Rabi"],
            crops_observed=1, harvested_count=1, average_yield=100.0,
            yield_unit="kg", best_yield=100.0, worst_yield=100.0,
            disease_records=0, fertilizer_applications=0, irrigation_applications=0,
            confidence=0.5
        )]
    )
    ctx = UnifiedContext(historical_insights=insight)
    dump = ctx.model_dump()
    assert dump["historical_insights"]["crop_performance"][0]["crop_name"] == "Wheat"

def test_formatter_does_not_render_historical_insights():
    ctx = UnifiedContext(
        farm=None, weather=None, knowledge=None, intelligence=None, history=None,
        historical_insights=HistoricalInsightsContext()
    )
    
    formatted = format_context(ctx)
    assert "[HISTORICAL INSIGHTS]" not in formatted

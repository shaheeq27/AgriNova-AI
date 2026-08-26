import pytest
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from datetime import date

from app.ai.services.context_service import ContextService
from app.ai.schemas.historical_analysis import HistoricalInsightsContext
from app.ai.services.historical_insights_service import HistoricalInsightsService

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session
    await engine.dispose()


@pytest.mark.asyncio
async def test_context_service_wires_historical_insights_to_engines(db: AsyncSession, monkeypatch):
    user = User(id="u1", email="a@b.com", hashed_password="x", full_name="A")
    farm = Farm(id="f1", user_id="u1", name="Farm 1", location_city="Pune", soil_type="Black", total_area_acres=10.0)
    crop = Crop(id="c1", farm_id="f1", crop_name="Wheat", season="Rabi", status="active", area_acres=5.0)
    
    db.add_all([user, farm, crop])
    await db.commit()
    
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    farm_q = await db.execute(select(Farm).options(selectinload(Farm.crops)).filter_by(id="f1"))
    farm_loaded = farm_q.scalar_one()

    dummy_insights = HistoricalInsightsContext(crop_performance=[])
    
    async def mock_compute_insights(*args, **kwargs):
        return dummy_insights
    
    monkeypatch.setattr(HistoricalInsightsService, "compute_insights_context", mock_compute_insights)
    
    service = ContextService(db)
    async def mock_get_current_stage(*args, **kwargs):
        return "Vegetative"
    monkeypatch.setattr(service.intelligence_service, "_get_current_stage", mock_get_current_stage)

    captured_insights = None
    
    async def mock_get_recommendation(*args, **kwargs):
        nonlocal captured_insights
        print(f'MOCK GET REC CALLED! kwargs: {kwargs}')
        if "historical_insights" in kwargs:
            captured_insights = kwargs["historical_insights"]
        elif len(args) >= 5:
            captured_insights = args[4]
        else:
            captured_insights = None

        return {"fertilizer_type": "Mock", "quantity_per_acre": 10.0, "unit": "kg", "timing": "", "application_method": "", "explanation": ""}

    monkeypatch.setattr(
        service.intelligence_service.fertilizer_engine, 
        "get_recommendation", 
        mock_get_recommendation
    )
    
    ctx = await service.build_unified_context(farm_loaded, "What fertilizer should I use for Wheat?")
    
    assert captured_insights is not None
    assert captured_insights is dummy_insights, "The exact HistoricalInsightsContext instance must be passed to the engine"


@pytest.mark.asyncio
async def test_historical_insights_none_behaves_safely(db: AsyncSession, monkeypatch):
    user = User(id="u2", email="b@b.com", hashed_password="x", full_name="B")
    farm = Farm(id="f2", user_id="u2", name="Farm 2", location_city="Pune", soil_type="Black", total_area_acres=10.0)
    crop = Crop(id="c2", farm_id="f2", crop_name="Rice", season="Kharif", status="active", area_acres=5.0)
    
    db.add_all([user, farm, crop])
    await db.commit()
    
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    farm_q = await db.execute(select(Farm).options(selectinload(Farm.crops)).filter_by(id="f2"))
    farm_loaded = farm_q.scalar_one()

    async def mock_compute_insights_none(*args, **kwargs):
        return None
        
    monkeypatch.setattr(HistoricalInsightsService, "compute_insights_context", mock_compute_insights_none)

    service = ContextService(db)
    async def mock_get_current_stage(*args, **kwargs):
        return "Vegetative"
    monkeypatch.setattr(service.intelligence_service, "_get_current_stage", mock_get_current_stage)

    captured_insights = "NOTHING"
    
    async def mock_get_recommendation_none(*args, **kwargs):
        nonlocal captured_insights
        if "historical_insights" in kwargs:
            captured_insights = kwargs["historical_insights"]
        elif len(args) >= 5:
            captured_insights = args[4]
        else:
            captured_insights = None

        return {"fertilizer_type": "Mock", "quantity_per_acre": 10.0, "unit": "kg", "timing": "", "application_method": "", "explanation": ""}

    monkeypatch.setattr(
        service.intelligence_service.fertilizer_engine, 
        "get_recommendation", 
        mock_get_recommendation_none
    )
    
    ctx = await service.build_unified_context(farm_loaded, "What fertilizer should I use for Rice?")
    
    assert captured_insights is None

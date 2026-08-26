import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select
from app.core.database import Base
from sqlalchemy.orm import selectinload

from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.timeline import CropTimeline
from app.models.knowledge import DiseaseLibrary, CropProfile
from app.models.disease import DiseaseRecord
from app.models.fertilizer import FertilizerLog
from app.models.irrigation import IrrigationLog

from app.ai.services.context_service import ContextService
from app.api.v1.crops import recommend_crops
import app.services.crop_recommendation_service as crs
from app.schemas.crop import CropRecommendationRequest
from app.schemas.common import APIResponse

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
async def test_e2e_pipeline_applies_historical_adjustments(db: AsyncSession, monkeypatch):
    pass
    monkeypatch.setattr(crs, "_load_model", lambda: None)

    # Setup Farm with heavy history to trigger personalization
    user = User(id="u1_e2e_p3", email="e2ep3@test.com", hashed_password="x", full_name="User")
    farm = Farm(id="f1_e2e_p3", user_id="u1_e2e_p3", name="E2E Farm", location_city="Pune", soil_type="Loam", total_area_acres=10.0)
    
    # Active crop for intelligence engines
    crop_active = Crop(id="c1_e2e_p3", farm_id="f1_e2e_p3", crop_name="Wheat", variety="A", season="Rabi",
                       planting_date=date(2025, 1, 1), status="active", area_acres=5.0)

    # 5 previous crops (triggers yield trends)
    prev_crops = []
    for i in range(5):
        prev_crops.append(
            Crop(id=f"prev_{i}", farm_id="f1_e2e_p3", crop_name="Wheat", variety="A", season="Rabi",
                 planting_date=date(2020+i, 1, 1), actual_harvest_date=date(2020+i, 4, 1),
                 status="harvested", area_acres=5.0, yield_amount=2000.0 + i*100, yield_unit="kg") # Increasing trend
        )

    # 4 Fertilizer applications on Wheat (triggers >= 3 fertilizer personalization)
    ferts = []
    for i in range(4):
        ferts.append(
            FertilizerLog(id=f"flog_{i}", crop_id=prev_crops[0].id, fertilizer_type="Urea",
                          quantity=50.0, unit="kg", date=date(2024, 2, i+1))
        )

    # 6 Irrigation applications on Wheat (triggers >= 5 irrigation personalization)
    irrs = []
    for i in range(6):
        irrs.append(
            IrrigationLog(id=f"ilog_{i}", crop_id=prev_crops[0].id, water_amount_liters=20.0,
                          date=date(2024, 1, i+1), growth_stage="Seedling")
        )
        
    # 3 Disease Records (triggers recurrence personalization)
    dis = []
    for i in range(3):
        dis.append(
            DiseaseRecord(id=f"dlog_{i}", crop_id=prev_crops[0].id, disease_name="Rust",
                          severity="high", status="resolved", outcome="Treated")
        )

    # Add timeline so it knows current_stage
    event = CropTimeline(id="te1", crop_id="c1_e2e_p3", stage_name="Seedling", stage_order=1, start_date=date.today().replace(month=1, day=1), end_date=date.today().replace(month=12, day=31), status="in_progress")
    
    # Add knowledge base entries so DiseaseService and CropRecommendationService don't return empty
    dl = DiseaseLibrary(disease_name="Rust", affected_crops="Wheat", symptoms="yellow spots, brown spots", treatment="Fungicide", prevention="Spacing", severity="high")
    cp = CropProfile(crop_name="Wheat", temp_min=10, temp_max=25, humidity_min=40, humidity_max=60, rain_min=200, rain_max=500, ideal_soil_types="Loam, Clay", growing_season="Rabi")

    db.add_all([user, farm, crop_active, event, dl, cp] + prev_crops + ferts + irrs + dis)
    await db.commit()

    farm_q = await db.execute(select(Farm).options(selectinload(Farm.crops)).filter_by(id="f1_e2e_p3"))
    farm_loaded = farm_q.scalar_one()

    # --- 1. Test the AI Context Service (Fertilizer, Irrigation, Disease) ---
    context_service = ContextService(db)
    
    # "What fertilizer and irrigation for Wheat? Also I see yellow spots (Rust symptom)."
    msg = "I need fertilizer and irrigation advice for my Wheat. I also see yellow spots and brown spots."
    
    # The IntentRouter should catch: fertilizer, irrigation, disease, and symptoms.
    unified_ctx = await context_service.build_unified_context(farm_loaded, user_message=msg)

    assert unified_ctx.historical_insights is not None
    assert unified_ctx.intelligence is not None
    assert len(unified_ctx.intelligence.crop_outputs) == 1
    
    crop_out = unified_ctx.intelligence.crop_outputs[0]
    
    # Fertilizer
    assert crop_out.fertilizer is not None
    assert crop_out.fertilizer.historically_adjusted is True
    assert "reduced" in crop_out.fertilizer.personalization_rationale.lower()
    
    # Irrigation
    assert crop_out.irrigation is not None
    assert crop_out.irrigation.historically_adjusted is True
    assert "reduced" in crop_out.irrigation.personalization_rationale.lower()
    
    # Disease
    assert len(crop_out.diseases) > 0
    rust_match = next((d for d in crop_out.diseases if d.disease_name == "Rust"), None)
    if rust_match:
        assert rust_match.historically_adjusted is True
        assert "increased" in rust_match.personalization_rationale.lower()

    # --- 2. Test the API crop recommendation endpoint ---
    request = CropRecommendationRequest(
        temperature=20.0,
        humidity=50.0,
        rainfall=300.0,
        soil_type="Loam",
        farm_id="f1_e2e_p3" # Passing the farm_id
    )
    response = await recommend_crops(data=request, db=db)
    assert isinstance(response, APIResponse)
    recs = response.data["recommendations"]
    
    # Check if Wheat was historically adjusted (increased due to trend)
    wheat_rec = next((r for r in recs if r["crop_name"] == "Wheat"), None)
    if wheat_rec:
        assert wheat_rec["historically_adjusted"] is True
        assert "increased" in wheat_rec["personalization_rationale"].lower()


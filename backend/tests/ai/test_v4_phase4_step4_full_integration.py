import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base

from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.timeline import CropTimeline
from app.models.knowledge import DiseaseLibrary, CropProfile
from app.models.disease import DiseaseRecord
from app.models.fertilizer import FertilizerLog
from app.models.irrigation import IrrigationLog

from app.ai.services.ai_service import AIService
from app.ai.schemas.chat import ChatRequest
from app.models.conversation import Conversation

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session
    await engine.dispose()


class DummyManager:
    async def generate_response(self, msgs):
        return "Hello"


@pytest.mark.asyncio
async def test_full_v4_personalization_integration(db: AsyncSession, monkeypatch):
    """Test the full V4 integration pipeline from DB to AI prompt."""
    
    # --- 1. SETUP DATABASE ---
    
    # User
    user = User(id="u_full", email="full@test.com", hashed_password="x", full_name="Full")
    db.add(user)
    
    # Knowledge
    dl = DiseaseLibrary(disease_name="Rust", affected_crops="Wheat", symptoms="yellow spots, brown spots", treatment="Fungicide", prevention="Spacing", severity="high")
    cp = CropProfile(crop_name="Wheat", temp_min=10, temp_max=25, humidity_min=40, humidity_max=60, rain_min=200, rain_max=500, ideal_soil_types="Loam, Clay", growing_season="Rabi")
    db.add_all([dl, cp])
    
    # Farm A (Normal History)
    farm_a = Farm(id="farm_a", user_id="u_full", name="Farm A", location_city="Pune", soil_type="Loam", total_area_acres=10.0)
    db.add(farm_a)
    
    crop_a_active = Crop(id="c_a_active", farm_id="farm_a", crop_name="Wheat", variety="A", season="Rabi",
                         planting_date=date(2025, 1, 1), status="active", area_acres=5.0)
    db.add(crop_a_active)
    
    tl_a = CropTimeline(id="tl_a", crop_id="c_a_active", stage_name="Seedling", stage_order=1, start_date=date.today().replace(month=1, day=1), end_date=date.today().replace(month=12, day=31), status="in_progress")
    db.add(tl_a)
    
    crop_a_past = Crop(id="c_a_past", farm_id="farm_a", crop_name="Wheat", variety="A", season="Rabi",
                       planting_date=date(2024, 1, 1), actual_harvest_date=date(2024, 4, 1), status="harvested", area_acres=5.0)
    db.add(crop_a_past)
    
    # 1 fertilizer log, 2 irrigation logs for A (insufficient to trigger personalization)
    db.add(FertilizerLog(id="f_a_1", crop_id="c_a_past", fertilizer_type="Urea", quantity=50.0, unit="kg", date=date(2024, 2, 1)))
    db.add(IrrigationLog(id="i_a_1", crop_id="c_a_past", water_amount_liters=20.0, date=date(2024, 1, 1), growth_stage="Seedling"))
    db.add(IrrigationLog(id="i_a_2", crop_id="c_a_past", water_amount_liters=20.0, date=date(2024, 1, 15), growth_stage="Seedling"))
    
    # Farm B (Heavy History)
    farm_b = Farm(id="farm_b", user_id="u_full", name="Farm B", location_city="Pune", soil_type="Loam", total_area_acres=10.0)
    db.add(farm_b)
    
    crop_b_active = Crop(id="c_b_active", farm_id="farm_b", crop_name="Wheat", variety="A", season="Rabi",
                         planting_date=date(2025, 1, 1), status="active", area_acres=5.0)
    db.add(crop_b_active)
    
    tl_b = CropTimeline(id="tl_b", crop_id="c_b_active", stage_name="Seedling", stage_order=1, start_date=date.today().replace(month=1, day=1), end_date=date.today().replace(month=12, day=31), status="in_progress")
    db.add(tl_b)
    
    crop_b_past = Crop(id="c_b_past", farm_id="farm_b", crop_name="Wheat", variety="A", season="Rabi",
                       planting_date=date(2024, 1, 1), actual_harvest_date=date(2024, 4, 1), status="harvested", area_acres=5.0)
    db.add(crop_b_past)
    
    # 4 fertilizer logs, 6 irrigation logs, 3 disease logs for B (triggers personalization)
    for i in range(4):
        db.add(FertilizerLog(id=f"f_b_{i}", crop_id="c_b_past", fertilizer_type="Urea", quantity=50.0, unit="kg", date=date(2024, 2, i+1)))
    for i in range(6):
        db.add(IrrigationLog(id=f"i_b_{i}", crop_id="c_b_past", water_amount_liters=20.0, date=date(2024, 1, i+1), growth_stage="Seedling"))
    for i in range(3):
        db.add(DiseaseRecord(id=f"d_b_{i}", crop_id="c_b_past", disease_name="Rust", severity="high", status="resolved", outcome="Treated"))

    await db.commit()
    
    # --- 2. SETUP AISERVICE ---
    
    service = AIService(db)
    
    # We will let AIService resolve farms naturally. We just mock ProviderManager to intercept the message list.
    original_build = service._build_messages
    
    monkeypatch.setattr(service, "_get_provider_manager", lambda: DummyManager())
    
    # Bypass user-auth resolve for conversation/farm
    async def mock_resolve_conv(user_id, conv_id):
        conv = Conversation(id=f"conv_{conv_id}", user_id=user_id)
        db.add(conv)
        await db.commit()
        return conv
        
    monkeypatch.setattr(service, "_resolve_conversation", mock_resolve_conv)
    
    # We must NOT mock _resolve_farm completely, because we want it to fetch the actual farm from DB.
    # We just mock the auth wrapper to fetch by ID directly.
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    async def mock_resolve_f(user_id, conv, farm_id):
        q = await db.execute(select(Farm).options(selectinload(Farm.crops)).filter_by(id=farm_id))
        return q.scalar_one()
        
    monkeypatch.setattr(service, "_resolve_farm", mock_resolve_f)
    
    # Override build messages to capture output
    msgs_a = []
    msgs_b = []
    
    def capture_a(existing, new_msg, ctx_str):
        res = original_build(existing, new_msg, ctx_str)
        msgs_a.extend(res)
        return res
        
    def capture_b(existing, new_msg, ctx_str):
        res = original_build(existing, new_msg, ctx_str)
        msgs_b.extend(res)
        return res
        
    # --- 3. TEST FARM A (BASELINE) ---
    monkeypatch.setattr(service, "_build_messages", capture_a)
    msg_text = "I need fertilizer and irrigation advice. I see yellow spots on leaves."
    await service.chat("u_full", ChatRequest(message=msg_text, farm_id="farm_a", conversation_id="1"))
    
    prompt_a = msgs_a[0].content
    
    assert "[INTELLIGENCE]" in prompt_a
    assert "Personalization: Adjusted based on farm history -" not in prompt_a
    
    # Check baseline numbers (e.g. 50 kg Urea)
    assert "50.0 kg/acre" in prompt_a
    assert "Rust" in prompt_a
    
    # --- 4. TEST FARM B (PERSONALIZED) ---
    monkeypatch.setattr(service, "_build_messages", capture_b)
    await service.chat("u_full", ChatRequest(message=msg_text, farm_id="farm_b", conversation_id="2"))
    
    prompt_b = msgs_b[0].content
    
    assert "[INTELLIGENCE]" in prompt_b
    assert "Personalization: Adjusted based on farm history -" in prompt_b
    
    # Baseline was 50.0. Heavy usage reduces it (e.g., to 45.0)
    assert "45.0 kg/acre" in prompt_b
    
    # Ensure rust is there, and its confidence was boosted
    assert "Rust" in prompt_b
    assert "Confidence increased" in prompt_b


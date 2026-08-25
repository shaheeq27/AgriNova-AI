"""
V4 Phase 1 Step 9 — End-to-End History Pipeline Validation.

Validates the complete historical-context pipeline:
Database → HistoryRepository → FarmHistoryService → ContextService →
UnifiedContext.history → ContextFormatter → [FARM HISTORY] →
AIRA_SYSTEM_PROMPT → AIService → AI provider request
"""

import pytest
from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base

from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.disease import DiseaseRecord
from app.models.irrigation import IrrigationLog
from app.models.fertilizer import FertilizerLog
from app.models.activity_log import ActivityLog
from app.models.conversation import Conversation

from app.ai.services.context_service import ContextService
from app.ai.services.context_formatter import format_context
from app.ai.services.ai_service import AIService
from app.ai.schemas.chat import ChatRequest
from app.ai.providers.base import BaseAIProvider, AIMessage


class DummyE2EProvider(BaseAIProvider):
    async def generate_response(self, messages: list[AIMessage]) -> str:
        self.last_messages = messages
        return "End-to-End Mock Response"

    async def generate_response_stream(self, messages: list[AIMessage]):
        self.last_messages = messages
        yield "End-to-End "
        yield "Mock Response"


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
async def test_e2e_history_pipeline_full_data(db: AsyncSession):
    # 1. Realistic test data
    user = User(id="u1", email="farmer@example.com", hashed_password="x", full_name="Farmer")
    farm = Farm(id="f1", user_id="u1", name="Green Farm", location_city="Pune", soil_type="Black", total_area_acres=10.0)

    # Crop
    crop = Crop(id="c1", farm_id="f1", crop_name="Wheat", variety="Sharbati", season="Rabi",
                planting_date=date(2025, 1, 1), actual_harvest_date=date(2025, 4, 1),
                status="harvested", area_acres=5.0, yield_amount=2000.0, yield_unit="kg")

    # Disease
    disease = DiseaseRecord(id="d1", crop_id="c1", disease_name="Rust",
                            severity="high", status="resolved", outcome="Yield loss 10%",
                            treatment_applied="Fungicide X")

    # Fertilizer
    fert1 = FertilizerLog(id="fe1", crop_id="c1", fertilizer_type="Urea",
                          quantity=50.0, unit="kg", date=date(2025, 2, 1))
    fert2 = FertilizerLog(id="fe2", crop_id="c1", fertilizer_type="DAP",
                          quantity=25.0, unit="kg", date=date(2025, 3, 1))

    # Irrigation
    irr1 = IrrigationLog(id="i1", crop_id="c1", water_amount_liters=20.0,
                         date=date(2025, 1, 15), growth_stage="Seedling")

    # Activities
    act1 = ActivityLog(id="a1", farm_id="f1", user_id="u1", crop_id="c1",
                       action="disease_treated", entity_type="disease", entity_id="d1", description="Treated rust")
    act2 = ActivityLog(id="a2", farm_id="f1", user_id="u1", crop_id="c1",
                       action="fertilizer_applied", entity_type="fertilizer", entity_id="fe1", description="Applied urea")

    db.add_all([user, farm, crop, disease, fert1, fert2, irr1, act1, act2])
    await db.commit()

    # Must re-load farm with crops eagerly to avoid DetachedInstanceError or MissingGreenlet
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    farm_q = await db.execute(select(Farm).options(selectinload(Farm.crops)).filter_by(id="f1"))
    farm_loaded = farm_q.scalar_one()

    # 3. Verify ContextService produces UnifiedContext.history != None
    context_service = ContextService(db)
    unified_ctx = await context_service.build_unified_context(farm_loaded, user_message="What next?")

    assert unified_ctx.history is not None

    # 4. Verify the history contains expected properties
    history = unified_ctx.history
    assert len(history.past_crops) == 1
    assert len(history.recent_diseases) == 1
    assert len(history.seasonal_patterns) > 0
    assert history.performance_summary is not None

    # 5 & 6. Verify ContextFormatter includes real data
    formatted = format_context(unified_ctx)
    assert "[FARM HISTORY]" in formatted
    assert "[/FARM HISTORY]" in formatted

    assert "Wheat" in formatted
    assert "Sharbati" in formatted
    assert "Yield: 2000.0 kg" in formatted
    assert "Rust" in formatted
    assert "resolved" in formatted
    assert "Fertilizer applications: 2" in formatted
    assert "Irrigation applications: 1" in formatted

    # 7. Verify AIService system prompt integration
    ai_service = AIService(db)
    dummy_provider = DummyE2EProvider()
    ai_service._provider = dummy_provider

    req = ChatRequest(message="What should I plant next?", farm_id="f1")
    await ai_service.chat(user_id="u1", request=req)

    # 9. Verify AIService receives system message with [FARM HISTORY]
    assert hasattr(dummy_provider, "last_messages")
    system_msg = dummy_provider.last_messages[0].content

    assert "[FARM HISTORY]" in system_msg
    assert "Yield: 2000.0 kg" in system_msg
    assert "Rust — high severity — resolved" in system_msg

    # NEW: Verify [HISTORICAL INSIGHTS]
    assert "[HISTORICAL INSIGHTS]" in system_msg
    assert "[/HISTORICAL INSIGHTS]" in system_msg

    # Verify values from the database
    # Crop Performance
    assert "Wheat" in system_msg
    assert "Avg Yield: 2000.0 kg" in system_msg

    # Disease Patterns
    assert "Rust (on Wheat)" in system_msg
    assert "Common Treatment: Fungicide X" in system_msg

    # Input Usage
    assert "Urea on Wheat" in system_msg
    assert "DAP on Wheat" in system_msg
    assert "Total Quantity: 50.0 kg" in system_msg

    # Yield Trends
    assert "Yield Trends:" in system_msg
    assert "Avg: 2000.0" in system_msg

    # Coexistence
    assert system_msg.count("[FARM HISTORY]") > 0
    assert system_msg.count("[HISTORICAL INSIGHTS]") > 0



@pytest.mark.asyncio
async def test_e2e_farm_isolation(db: AsyncSession):
    # Farm A Setup
    user_a = User(id="ua", email="a@a.com", hashed_password="x", full_name="A")
    farm_a = Farm(id="fa", user_id="ua", name="Farm A", location_city="Pune", soil_type="Black", total_area_acres=10.0)
    crop_a = Crop(id="ca", farm_id="fa", crop_name="TomatoTestCrop", season="Kharif",
                  status="harvested", area_acres=5.0, yield_amount=100.0, yield_unit="kg")

    # Farm B Setup
    user_b = User(id="ub", email="b@b.com", hashed_password="x", full_name="B")
    farm_b = Farm(id="fb", user_id="ub", name="Farm B", location_city="Mumbai", soil_type="Red", total_area_acres=5.0)
    crop_b = Crop(id="cb", farm_id="fb", crop_name="PotatoTestCrop", season="Rabi",
                  status="harvested", area_acres=2.0, yield_amount=50.0, yield_unit="kg")

    db.add_all([user_a, farm_a, crop_a, user_b, farm_b, crop_b])
    await db.commit()

    ai_service = AIService(db)
    dummy = DummyE2EProvider()
    ai_service._provider = dummy

    # Chat as User A, Farm A
    req = ChatRequest(message="Test", farm_id="fa")
    await ai_service.chat(user_id="ua", request=req)

    system_msg_a = dummy.last_messages[0].content
    assert "TomatoTestCrop" in system_msg_a
    assert "PotatoTestCrop" not in system_msg_a
    assert "[HISTORICAL INSIGHTS]" in system_msg_a
    # We should have TomatoTestCrop in insights
    assert "TomatoTestCrop" in system_msg_a[system_msg_a.find("[HISTORICAL INSIGHTS]"):]
    assert "PotatoTestCrop" not in system_msg_a[system_msg_a.find("[HISTORICAL INSIGHTS]"):]

    # Chat as User B, Farm B
    req = ChatRequest(message="Test", farm_id="fb")
    await ai_service.chat(user_id="ub", request=req)

    system_msg_b = dummy.last_messages[0].content
    assert "PotatoTestCrop" in system_msg_b
    assert "TomatoTestCrop" not in system_msg_b
    assert "[HISTORICAL INSIGHTS]" in system_msg_b
    assert "PotatoTestCrop" in system_msg_b[system_msg_b.find("[HISTORICAL INSIGHTS]"):]
    assert "TomatoTestCrop" not in system_msg_b[system_msg_b.find("[HISTORICAL INSIGHTS]"):]


@pytest.mark.asyncio
async def test_e2e_empty_farm_behavior(db: AsyncSession):
    user = User(id="u_empty", email="empty@a.com", hashed_password="x", full_name="Empty")
    farm = Farm(id="f_empty", user_id="u_empty", name="Empty Farm", location_city="Pune", soil_type="Black", total_area_acres=10.0)
    db.add_all([user, farm])
    await db.commit()

    ai_service = AIService(db)
    dummy = DummyE2EProvider()
    ai_service._provider = dummy

    req = ChatRequest(message="Test", farm_id="f_empty")
    await ai_service.chat(user_id="u_empty", request=req)

    system_msg = dummy.last_messages[0].content
    assert "[FARM HISTORY]" in system_msg
    assert "No historical data available." in system_msg
    assert "Yield:" not in system_msg

    # Verify NO [HISTORICAL INSIGHTS] block
    assert "\n[HISTORICAL INSIGHTS]\n" not in system_msg


@pytest.mark.asyncio
async def test_e2e_no_farm_behavior(db: AsyncSession):
    user = User(id="u_nofarm", email="nofarm@a.com", hashed_password="x", full_name="NoFarm")
    db.add(user)
    await db.commit()

    ai_service = AIService(db)
    dummy = DummyE2EProvider()
    ai_service._provider = dummy

    req = ChatRequest(message="Test", farm_id=None)
    await ai_service.chat(user_id="u_nofarm", request=req)

    system_msg = dummy.last_messages[0].content
    # Depending on how the formatter works, without a farm_id, the entire
    # [FARM HISTORY] section isn't appended at all because ContextService.history is None.
    # The instructional text says "When [FARM HISTORY] is available" so the literal
    # string "[FARM HISTORY]" appears in the instructional part of the prompt,
    # but the formatted data block `\n[FARM HISTORY]\n` must not appear.
    assert "\n[FARM HISTORY]\n" not in system_msg

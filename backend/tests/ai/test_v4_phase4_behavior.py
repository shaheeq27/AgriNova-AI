import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core.database import Base

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session
        

from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.schemas.context import (
    UnifiedContext,
    EngineContext,
    CropEngineOutput,
    FertilizerResult,
    IrrigationResult,
    DiseaseResult,
    FarmHistoryContext,
)
from app.ai.services.context_formatter import format_context
from app.ai.services.ai_service import AIService
from app.ai.schemas.chat import ChatRequest
from app.models.conversation import Conversation
from app.models.farm import Farm

# Reusable mock helpers
async def mock_resolve_conversation(self, user_id, conv_id):
    return Conversation(id="c1", user_id="u1")

async def mock_resolve_farm(self, user_id, conv, farm_id):
    return Farm(id="f1", user_id="u1")

async def mock_get_messages(self, conv_id):
    return []

async def mock_add_message(self, msg):
    pass

async def mock_update_title(self, conv, title):
    pass

async def mock_commit(self):
    pass

class DummyManager:
    async def generate_response(self, msgs):
        return "Hello"

def setup_mock_ai_service(monkeypatch, db: AsyncSession, mock_context: UnifiedContext):
    service = AIService(db)
    monkeypatch.setattr(service, "_resolve_conversation", mock_resolve_conversation.__get__(service))
    monkeypatch.setattr(service, "_resolve_farm", mock_resolve_farm.__get__(service))
    monkeypatch.setattr(service.repo, "get_messages", mock_get_messages.__get__(service.repo))
    monkeypatch.setattr(service.repo, "add_message", mock_add_message.__get__(service.repo))
    monkeypatch.setattr(service.repo, "update_title", mock_update_title.__get__(service.repo))
    monkeypatch.setattr(service.db, "commit", mock_commit.__get__(service.db))
    monkeypatch.setattr(service, "_get_provider_manager", lambda: DummyManager())
    
    from app.ai.services.context_service import ContextService
    async def mock_build(*args, **kwargs):
        return mock_context
    monkeypatch.setattr(ContextService, "build_unified_context", mock_build)
    
    # Intercept _build_messages
    intercepted_messages = []
    original_build_messages = service._build_messages
    
    def mock_build_messages(existing, new_msg, context_string):
        msgs = original_build_messages(existing, new_msg, context_string)
        intercepted_messages.extend(msgs)
        return msgs
        
    monkeypatch.setattr(service, "_build_messages", mock_build_messages)
    
    return service, intercepted_messages

@pytest.mark.asyncio
async def test_scenario_1_personalized_fertilizer(db: AsyncSession, monkeypatch):
    """1. PERSONALIZED FERTILIZER"""
    fr = FertilizerResult(
        fertilizer_type="Urea",
        quantity_per_acre=45.0,
        unit="kg",
        timing="Morning",
        application_method="Broadcast",
        explanation="Needs nitrogen",
        historically_adjusted=True,
        personalization_rationale="Recommendation conservatively reduced by 10% based on repeated historical fertilizer usage."
    )
    ctx = UnifiedContext(intelligence=EngineContext(crop_outputs=[CropEngineOutput(crop_name="Wheat", fertilizer=fr)]))
    
    service, intercepted = setup_mock_ai_service(monkeypatch, db, ctx)
    await service.chat("u1", ChatRequest(message="Fertilizer advice", farm_id="f1"))
    
    system_prompt = intercepted[0].content
    
    # Verify exact numerical authority and rationale preservation
    assert "45.0 kg/acre" in system_prompt
    assert "Personalization: Adjusted based on farm history - Recommendation conservatively reduced by 10% based on repeated historical fertilizer usage." in system_prompt
    
    # Verify instruction text guarantees LLM acts as narrator, not calculator
    assert "Some engine recommendations may contain a historical personalization rationale" in system_prompt
    assert "You MUST NOT calculate another adjustment, override the deterministic engine's value" in system_prompt


@pytest.mark.asyncio
async def test_scenario_2_personalized_irrigation(db: AsyncSession, monkeypatch):
    """2. PERSONALIZED IRRIGATION"""
    ir = IrrigationResult(
        water_requirement_mm=19.0,
        method="Drip",
        frequency="Daily",
        weather_adjusted=False,
        explanation="Dry soil",
        historically_adjusted=True,
        personalization_rationale="Recommendation conservatively reduced by 5% based on repeated historical irrigation usage."
    )
    ctx = UnifiedContext(intelligence=EngineContext(crop_outputs=[CropEngineOutput(crop_name="Wheat", irrigation=ir)]))
    
    service, intercepted = setup_mock_ai_service(monkeypatch, db, ctx)
    await service.chat("u1", ChatRequest(message="Irrigation advice", farm_id="f1"))
    
    system_prompt = intercepted[0].content
    
    assert "19.0mm via Drip" in system_prompt
    assert "Personalization: Adjusted based on farm history - Recommendation conservatively reduced by 5% based on repeated historical irrigation usage." in system_prompt


@pytest.mark.asyncio
async def test_scenario_3_personalized_disease(db: AsyncSession, monkeypatch):
    """3. PERSONALIZED DISEASE"""
    dr = DiseaseResult(
        disease_name="Rust",
        confidence=0.92,
        symptoms=["spots"],
        treatment="Fungicide",
        prevention="Spacing",
        severity="High",
        historically_adjusted=True,
        personalization_rationale="Confidence increased due to historical recurrence."
    )
    ctx = UnifiedContext(intelligence=EngineContext(crop_outputs=[CropEngineOutput(crop_name="Wheat", diseases=[dr])]))
    
    service, intercepted = setup_mock_ai_service(monkeypatch, db, ctx)
    await service.chat("u1", ChatRequest(message="Disease advice", farm_id="f1"))
    
    system_prompt = intercepted[0].content
    
    assert "Rust (confidence: 92%" in system_prompt
    assert "Personalization: Adjusted based on farm history - Confidence increased due to historical recurrence." in system_prompt


@pytest.mark.asyncio
async def test_scenario_4_no_personalization(db: AsyncSession, monkeypatch):
    """4. NO PERSONALIZATION"""
    fr = FertilizerResult(
        fertilizer_type="Urea",
        quantity_per_acre=50.0,
        unit="kg",
        timing="Morning",
        application_method="Broadcast",
        explanation="Needs nitrogen",
        historically_adjusted=False,
        personalization_rationale=None
    )
    ctx = UnifiedContext(intelligence=EngineContext(crop_outputs=[CropEngineOutput(crop_name="Wheat", fertilizer=fr)]))
    
    service, intercepted = setup_mock_ai_service(monkeypatch, db, ctx)
    await service.chat("u1", ChatRequest(message="Fertilizer advice", farm_id="f1"))
    
    system_prompt = intercepted[0].content
    
    assert "50.0 kg/acre" in system_prompt
    assert "Personalization: Adjusted based on farm history -" not in system_prompt


@pytest.mark.asyncio
async def test_scenario_5_low_confidence_irrelevant_history(db: AsyncSession, monkeypatch):
    """5. LOW-CONFIDENCE / IRRELEVANT HISTORY"""
    # The history context contains data, but engine determines no personalization applies
    fr = FertilizerResult(
        fertilizer_type="Urea",
        quantity_per_acre=50.0,
        unit="kg",
        timing="Morning",
        application_method="Broadcast",
        explanation="Needs nitrogen",
        historically_adjusted=False,
        personalization_rationale=None
    )
    ctx = UnifiedContext(
        history=FarmHistoryContext(performance_summary="3 recorded crops."),
        intelligence=EngineContext(crop_outputs=[CropEngineOutput(crop_name="Wheat", fertilizer=fr)])
    )
    
    service, intercepted = setup_mock_ai_service(monkeypatch, db, ctx)
    await service.chat("u1", ChatRequest(message="Fertilizer advice", farm_id="f1"))
    
    system_prompt = intercepted[0].content
    
    # History exists in context
    assert "3 recorded crops." in system_prompt
    # But personalization text MUST NOT exist
    assert "Personalization: Adjusted based on farm history -" not in system_prompt
    # Recommendation remains standard
    assert "50.0 kg/acre" in system_prompt


@pytest.mark.asyncio
async def test_scenario_6_deterministic_value_authority(db: AsyncSession, monkeypatch):
    """6. DETERMINISTIC VALUE AUTHORITY"""
    fr = FertilizerResult(
        fertilizer_type="DAP",
        quantity_per_acre=33.33,
        unit="kg",
        timing="Pre-planting",
        application_method="Broadcast",
        explanation="Base",
        historically_adjusted=True,
        personalization_rationale="Custom boundary applied."
    )
    ctx = UnifiedContext(intelligence=EngineContext(crop_outputs=[CropEngineOutput(crop_name="Wheat", fertilizer=fr)]))
    
    # The test verifies the boundary exactly: engine output -> Formatter -> Prompt -> Provider
    service, intercepted = setup_mock_ai_service(monkeypatch, db, ctx)
    await service.chat("u1", ChatRequest(message="Test", farm_id="f1"))
    
    system_prompt = intercepted[0].content
    
    assert "33.33 kg/acre" in system_prompt
    assert "Custom boundary applied." in system_prompt

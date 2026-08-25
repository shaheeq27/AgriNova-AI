"""
Tests for V4 Phase 1 Step 8 — AI History Integration.
"""

import pytest
from app.ai.prompts.system import AIRA_SYSTEM_PROMPT


def test_system_prompt_includes_farm_history_instructions():
    """Verify that the system prompt natively includes instructions for FARM HISTORY."""
    assert "[FARM HISTORY]" in AIRA_SYSTEM_PROMPT
    
    # Check knowledge grounding instructions
    assert "When [FARM HISTORY] is available:" in AIRA_SYSTEM_PROMPT
    assert "supporting evidence" in AIRA_SYSTEM_PROMPT
    assert "historical context, not an absolute guarantee" in AIRA_SYSTEM_PROMPT
    
    # Check context format instructions
    assert "Data between [FARM HISTORY] and [/FARM HISTORY] contains historical" in AIRA_SYSTEM_PROMPT
    assert "rely on current data for immediate operational decisions" in AIRA_SYSTEM_PROMPT


def test_existing_context_blocks_preserved():
    """Verify that instructions for existing blocks are not mangled."""
    assert "[FARM CONTEXT]" in AIRA_SYSTEM_PROMPT
    assert "[KNOWLEDGE]" in AIRA_SYSTEM_PROMPT
    assert "[INTELLIGENCE]" in AIRA_SYSTEM_PROMPT
    
    assert "ground truth for this farmer" in AIRA_SYSTEM_PROMPT
    assert "authoritative reference material" in AIRA_SYSTEM_PROMPT

from datetime import date
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.conversation import Conversation
from app.ai.services.ai_service import AIService
from app.ai.schemas.chat import ChatRequest
from app.ai.providers.base import BaseAIProvider, AIMessage

class DummyProvider(BaseAIProvider):
    async def generate_response(self, messages: list[AIMessage]) -> str:
        # We capture the messages in self so tests can assert against them
        self.last_messages = messages
        return "I am a mock response"

    async def generate_response_stream(self, messages: list[AIMessage]):
        self.last_messages = messages
        yield "I am "
        yield "a mock response"


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
async def test_ai_service_sends_history_to_llm(db: AsyncSession):
    # Setup Data
    user = User(id="u1", email="a@b.com", hashed_password="x", full_name="A")
    farm = Farm(id="f1", user_id="u1", name="Farm 1", location_city="Pune", soil_type="Black", total_area_acres=10.0)
    crop = Crop(id="c1", farm_id="f1", crop_name="Rice", season="Kharif", 
                actual_harvest_date=date(2025, 1, 1), status="harvested", 
                yield_amount=500.0, yield_unit="kg", area_acres=5.0)
    
    db.add_all([user, farm, crop])
    await db.commit()

    service = AIService(db)
    # Inject dummy provider
    dummy = DummyProvider()
    service._provider = dummy

    # Act
    req = ChatRequest(message="What should I plant?", farm_id="f1")
    resp = await service.chat(user_id="u1", request=req)

    # Assert
    assert resp.response == "I am a mock response"
    assert hasattr(dummy, "last_messages")
    system_msg = dummy.last_messages[0].content
    
    # Check the data block, not just the instructions
    assert "\n[FARM HISTORY]\n" in system_msg
    assert "Past Crops:" in system_msg
    assert "Rice | Season: Kharif" in system_msg
    assert "Yield: 500.0 kg" in system_msg



@pytest.mark.asyncio
async def test_ai_service_without_farm_id(db: AsyncSession):
    user = User(id="u2", email="b@b.com", hashed_password="x", full_name="B")
    db.add(user)
    await db.commit()

    service = AIService(db)
    dummy = DummyProvider()
    service._provider = dummy

    req = ChatRequest(message="General agriculture question")
    resp = await service.chat(user_id="u2", request=req)

    assert resp.response == "I am a mock response"
    system_msg = dummy.last_messages[0].content
    # The instructions will have "[FARM HISTORY]" but the data block won't be appended at the end
    assert "\n[FARM HISTORY]\n" not in system_msg
    assert "\n[FARM CONTEXT]\n" not in system_msg
    assert "\n[HISTORICAL INSIGHTS]\n" not in system_msg


@pytest.mark.asyncio
async def test_ai_service_with_empty_history(db: AsyncSession):
    user = User(id="u3", email="c@b.com", hashed_password="x", full_name="C")
    farm = Farm(id="f3", user_id="u3", name="Farm 3", location_city="Pune", soil_type="Black", total_area_acres=10.0)
    
    db.add_all([user, farm])
    await db.commit()

    service = AIService(db)
    dummy = DummyProvider()
    service._provider = dummy

    req = ChatRequest(message="What should I plant?", farm_id="f3")
    resp = await service.chat(user_id="u3", request=req)

    system_msg = dummy.last_messages[0].content
    assert "\n[FARM HISTORY]\n" in system_msg
    assert "No historical data available." in system_msg

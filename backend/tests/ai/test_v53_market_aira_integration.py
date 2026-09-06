"""
AgriNova AI — V5.3.5 Market Context Verification Tests.
Verifies the end-to-end injection of market data into the Aira LLM prompt.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import date

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.ai.schemas.chat import ChatRequest
from app.ai.services.ai_service import AIService
from app.schemas.market import MarketSummaryResponse, MarketSummaryItem, DataStatus
from app.ai.providers.base import AIMessage
from app.ai.prompts.system import AIRA_SYSTEM_PROMPT


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
async def setup_data(db: AsyncSession):
    u1 = User(id="u1", email="a@b.com", hashed_password="x", full_name="A")
    f1 = Farm(id="f1", user_id="u1", name="Farm1", location_city="Pune", soil_type="Black", total_area_acres=10)
    c1 = Crop(id="c1", farm_id="f1", crop_name="Tomato", season="Kharif", area_acres=5, status="active")
    
    db.add_all([u1, f1, c1])
    await db.commit()
    return {"u1": u1, "f1": f1}


class MockProviderManager:
    def __init__(self):
        self.captured_messages = []
        
    async def generate_response_stream(self, llm_messages: list[AIMessage]):
        self.captured_messages = llm_messages
        yield "Hello"
        yield " World"


def mock_summary(items, status=DataStatus.LIVE):
    from datetime import datetime, timezone
    return MarketSummaryResponse(
        items=items,
        last_updated=datetime.now(timezone.utc),
        data_status=status
    )


@pytest.mark.asyncio
async def test_aira_market_integration_path(db: AsyncSession, setup_data):
    """
    Verify that market context is fetched, formatted, and injected into
    the LLM system prompt when a farm has active crops.
    """
    service = AIService(db)
    
    # Mock MarketService dashboard summary
    summary = mock_summary([
        MarketSummaryItem(commodity="Tomato", market_name="M2", modal_price=2800, price_date=date.today(), price_change_pct=12.5)
    ])
    
    mock_pm = MockProviderManager()
    
    with patch.object(service.context_service.market_service, "get_dashboard_summary", new_callable=AsyncMock, return_value=summary):
        with patch.object(service, "_get_provider_manager", return_value=mock_pm):
            
            # Send chat request
            req = ChatRequest(message="What is the price of tomato?", farm_id="f1")
            
            # We consume the generator
            chunks = []
            async for chunk in service.chat_stream("u1", req):
                chunks.append(chunk)
                
            # Verify the response flowed correctly
            assert chunks[-1]["type"] == "done"
            
            # Extract the system prompt
            system_prompt = mock_pm.captured_messages[0].content
            
            # 1. Market context is present
            assert "[MARKET DATA]" in system_prompt
            assert "[/MARKET DATA]" in system_prompt
            
            # 2. Information is available
            assert "Tomato:" in system_prompt
            assert "M2" in system_prompt
            assert "₹2,800/quintal" in system_prompt
            assert "+12.5%" in system_prompt
            
            # 3. Anti-fabrication verification
            assert "NEVER invent or estimate market prices" in system_prompt
            assert "prioritize farm/weather context over market prices" in system_prompt
            assert "do NOT fabricate one" in system_prompt


@pytest.mark.asyncio
async def test_aira_unrelated_question_still_receives_context(db: AsyncSession, setup_data):
    """
    Verify that an unrelated question (e.g. soil health) still receives
    the UnifiedContext (including Market Data) but relies on Aira's rules
    to prioritize relevant information.
    """
    service = AIService(db)
    
    summary = mock_summary([
        MarketSummaryItem(commodity="Tomato", market_name="M2", modal_price=2800, price_date=date.today(), price_change_pct=12.5)
    ])
    
    mock_pm = MockProviderManager()
    
    with patch.object(service.context_service.market_service, "get_dashboard_summary", new_callable=AsyncMock, return_value=summary):
        with patch.object(service, "_get_provider_manager", return_value=mock_pm):
            req = ChatRequest(message="How do I improve black soil?", farm_id="f1")
            
            async for chunk in service.chat_stream("u1", req):
                pass
                
            system_prompt = mock_pm.captured_messages[0].content
            
            # Market data is appended to system prompt regardless of user message intent
            assert "[MARKET DATA]" in system_prompt
            
            # The prompt relies on instructions to filter relevance:
            assert "Mention market information only when it genuinely helps" in system_prompt


@pytest.mark.asyncio
async def test_aira_missing_market_data(db: AsyncSession, setup_data):
    """
    Verify that when market data is empty, [MARKET DATA] is omitted.
    """
    service = AIService(db)
    
    # Return empty summary (DataStatus.UNAVAILABLE)
    summary = mock_summary([], status=DataStatus.UNAVAILABLE)
    
    mock_pm = MockProviderManager()
    
    with patch.object(service.context_service.market_service, "get_dashboard_summary", new_callable=AsyncMock, return_value=summary):
        with patch.object(service, "_get_provider_manager", return_value=mock_pm):
            req = ChatRequest(message="What is the price of tomato?", farm_id="f1")
            
            async for chunk in service.chat_stream("u1", req):
                pass
                
            system_prompt = mock_pm.captured_messages[0].content
            
            # The injected data block should NOT be present if DataStatus is UNAVAILABLE
            assert "Last Updated:" not in system_prompt
            assert "Data Status:" not in system_prompt
            
            # But the anti-fabrication rules in AIRA_SYSTEM_PROMPT ARE STILL PRESENT
            assert "NEVER invent or estimate market prices" in system_prompt


@pytest.mark.asyncio
async def test_aira_stale_data_preserves_status(db: AsyncSession, setup_data):
    """
    Verify that DataStatus.CACHED is passed to Aira so it can acknowledge staleness.
    """
    service = AIService(db)
    
    # Return CACHED summary
    summary = mock_summary([
        MarketSummaryItem(commodity="Tomato", market_name="M2", modal_price=2800, price_date=date.today())
    ], status=DataStatus.CACHED)
    
    mock_pm = MockProviderManager()
    
    with patch.object(service.context_service.market_service, "get_dashboard_summary", new_callable=AsyncMock, return_value=summary):
        with patch.object(service, "_get_provider_manager", return_value=mock_pm):
            req = ChatRequest(message="What is the price of tomato?", farm_id="f1")
            
            async for chunk in service.chat_stream("u1", req):
                pass
                
            system_prompt = mock_pm.captured_messages[0].content
            
            assert "[MARKET DATA]" in system_prompt
            assert "Data Status: Cached" in system_prompt
            assert "When [MARKET DATA] is stale, cached, or unavailable" in system_prompt

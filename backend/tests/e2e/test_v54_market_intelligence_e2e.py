"""
AgriNova AI — V5.4 Market Intelligence End-to-End Tests.
Verifies the complete unmocked pipeline from database -> MarketService -> Downstream Consumers.
"""

import pytest
from unittest.mock import AsyncMock, patch
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.market_price import MarketPrice
from app.models.notification import Notification

from app.ai.schemas.chat import ChatRequest
from app.ai.services.ai_service import AIService
from app.services.market_alert_service import MarketAlertService
from app.integrations.base import IntegrationResult


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
async def setup_e2e_data(db: AsyncSession):
    # 1. Setup User and Farm
    u = User(id="e2e_user", email="e2e@agrinova.in", hashed_password="x", full_name="E2E Farmer")
    f = Farm(id="e2e_farm", user_id="e2e_user", name="E2E Farm", location_city="Pune", soil_type="Black", total_area_acres=10)
    
    # 2. Setup Active Crop (Tomato)
    c = Crop(id="c1", farm_id="e2e_farm", crop_name="Tomato", season="Kharif", area_acres=5, status="active")
    
    db.add_all([u, f, c])
    await db.commit()
    
    # 3. Setup real MarketPrice records
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Yesterday: Modal 1000
    mp_yesterday = MarketPrice(
        commodity="Tomato", 
        market_name="Azadpur", 
        district="Delhi", 
        state="Delhi", 
        min_price=900.0, 
        max_price=1100.0, 
        modal_price=1000.0, 
        price_date=yesterday
    )
    
    # Today: Modal 1200 (a +20% spike!)
    mp_today = MarketPrice(
        commodity="Tomato", 
        market_name="Azadpur", 
        district="Delhi", 
        state="Delhi", 
        min_price=1100.0, 
        max_price=1300.0, 
        modal_price=1200.0, 
        price_date=today
    )
    
    db.add_all([mp_yesterday, mp_today])
    await db.commit()
    
    return {"u": u, "f": f, "c": c}


class MockProviderManager:
    """Mocks only the final LLM network boundary."""
    def __init__(self):
        self.captured_messages = []
        
    async def generate_response_stream(self, llm_messages):
        self.captured_messages = llm_messages
        yield "This is an E2E test response."


@pytest.mark.asyncio
async def test_e2e_path_a_aira_market_awareness(db: AsyncSession, setup_e2e_data):
    """
    E2E Path A — Real DB -> MarketService -> Context -> Aira.
    Proves the full stack builds the prompt correctly without mocking MarketService.
    """
    ai_service = AIService(db)
    
    mock_pm = MockProviderManager()
    
    with patch.object(ai_service, "_get_provider_manager", return_value=mock_pm):
        # Trigger real pipeline
        req = ChatRequest(message="What is the price of tomato today?", farm_id="e2e_farm")
        
        async for chunk in ai_service.chat_stream("e2e_user", req):
            pass
            
        system_prompt = mock_pm.captured_messages[0].content
        
        # Verify the DB rows flowed entirely through the app layers and were formatted
        assert "[MARKET DATA]" in system_prompt
        assert "Tomato:" in system_prompt
        assert "Azadpur" in system_prompt
        assert "₹1,200/quintal" in system_prompt  # Formatting verifies it
        assert "+20.0%" in system_prompt          # Intelligence logic verifies it
        assert "Data Status: Live" in system_prompt


@pytest.mark.asyncio
async def test_e2e_path_b_market_alert_and_email(db: AsyncSession, setup_e2e_data):
    """
    E2E Path B — Real DB -> MarketService -> MarketAlertService -> Notification + Email.
    Proves the background alert system processes raw DB metrics into dispatchable alerts.
    """
    alert_service = MarketAlertService(db)
    
    # Mock ONLY the external email provider boundary
    with patch("app.services.email_service.get_email_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "e2e_email_provider"
        mock_provider.execute_with_retry.return_value = IntegrationResult.success(data={"message_id": "e2e_msg"})
        mock_get_provider.return_value = mock_provider
        
        # Run real pipeline
        alerts_created = await alert_service.check_alerts_for_user("e2e_user")
        
        # Exactly 1 alert (Tomato went up 20% > 10% threshold)
        assert alerts_created == 1
        
        # Verify Notification record actually exists in DB
        n = (await db.execute(
            select(Notification).where(Notification.user_id == "e2e_user")
        )).scalars().first()
        
        assert n is not None
        assert n.type == "market_alert"
        assert "Tomato" in n.title
        assert "20.0%" in n.title
        
        # Verify Email sidecar received the payload
        assert mock_provider.execute_with_retry.call_count == 1
        email_message = mock_provider.execute_with_retry.call_args.kwargs.get("message")
        
        assert email_message.to_email == "e2e@agrinova.in"
        assert "Tomato" in email_message.subject
        assert "20.0%" in email_message.subject


"""
AgriNova AI — Market Alert Service Tests (V5.3.4).
"""
import pytest
from unittest.mock import AsyncMock, patch
from datetime import date, datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference
from app.services.market_alert_service import MarketAlertService
from app.schemas.market import MarketSummaryResponse, MarketSummaryItem, DataStatus
from app.services.email_service import EmailService

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
    # Setup users, farms, crops, preferences
    u1 = User(id="u1", email="a@b.com", hashed_password="x", full_name="A")
    f1 = Farm(id="f1", user_id="u1", name="Farm1", location_city="Pune", soil_type="Black", total_area_acres=10)
    c1 = Crop(id="c1", farm_id="f1", crop_name="Tomato", season="Kharif", area_acres=5, status="active")
    c2 = Crop(id="c2", farm_id="f1", crop_name="Wheat", season="Rabi", area_acres=5, status="harvested") # inactive
    
    pref1 = NotificationPreference(user_id="u1", email_enabled=True, market_alerts=True)
    
    # User 2: Email disabled
    u2 = User(id="u2", email="b@b.com", hashed_password="x", full_name="B")
    f2 = Farm(id="f2", user_id="u2", name="Farm2", location_city="Delhi", soil_type="Loam", total_area_acres=10)
    c3 = Crop(id="c3", farm_id="f2", crop_name="Rice", season="Kharif", area_acres=10, status="planned") # active
    
    pref2 = NotificationPreference(user_id="u2", email_enabled=True, market_alerts=False)

    db.add_all([u1, f1, c1, c2, pref1, u2, f2, c3, pref2])
    await db.commit()
    
    return {"u1": u1, "u2": u2}

def mock_summary(items):
    return MarketSummaryResponse(
        items=items,
        last_updated=datetime.now(timezone.utc),
        data_status=DataStatus.LIVE
    )

@pytest.mark.asyncio
async def test_thresholds_and_active_filtering(db: AsyncSession, setup_data):
    """
    Cover triggers across various thresholds, active vs inactive crops, and None.
    """
    service = MarketAlertService(db)
    
    summary = mock_summary([
        # Tomato is active for u1
        MarketSummaryItem(commodity="Tomato", market_name="M1", modal_price=1000, price_date=date.today(), price_change_pct=10.0), # exactly +10 (trigger)
        MarketSummaryItem(commodity="Tomato", market_name="M2", modal_price=1000, price_date=date.today(), price_change_pct=15.5), # > 10 (trigger)
        MarketSummaryItem(commodity="Tomato", market_name="M3", modal_price=1000, price_date=date.today(), price_change_pct=-10.0), # exactly -10 (trigger)
        MarketSummaryItem(commodity="Tomato", market_name="M4", modal_price=1000, price_date=date.today(), price_change_pct=-10.1), # < -10 (trigger)
        MarketSummaryItem(commodity="Tomato", market_name="M5", modal_price=1000, price_date=date.today(), price_change_pct=9.9), # below threshold (ignore)
        MarketSummaryItem(commodity="Tomato", market_name="M6", modal_price=1000, price_date=date.today(), price_change_pct=None), # None (ignore)
    ])

    with patch.object(service.market_service, "get_dashboard_summary", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = summary
        alerts_created = await service.check_alerts_for_user("u1")
    
    # 4 alerts triggered for Tomato
    assert alerts_created == 4
    
    # Check Notification table
    nots = (await db.execute(select(Notification).where(Notification.user_id == "u1"))).scalars().all()
    assert len(nots) == 4
    for n in nots:
        assert n.type == "market_alert" # 9
        assert n.related_entity_type == "Tomato"
        
    # Verify only 'tomato' was requested from summary (wheat ignored)
    mock_get.assert_called_once()
    requested_crops = mock_get.call_args[0][0]
    assert "tomato" in requested_crops
    assert "wheat" not in requested_crops


@pytest.mark.asyncio
async def test_email_preferences_and_resilience(db: AsyncSession, setup_data):
    """
    Test preference mapping and in-app vs email isolation.
    """
    service = MarketAlertService(db)
    from app.integrations.base import IntegrationResult
    
    with patch("app.services.email_service.get_email_provider") as mock_get_provider:
        mock_provider = AsyncMock()
        mock_provider.provider_name = "test_provider"
        mock_provider.execute_with_retry.return_value = IntegrationResult.success(data={"message_id": "mock_id"})
        mock_get_provider.return_value = mock_provider
        
        # Delete existing notifications to test isolated run
        await db.execute(Notification.__table__.delete())
        await db.commit()
        
        with patch.object(service.market_service, "get_dashboard_summary", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_summary([
                MarketSummaryItem(commodity="Tomato", market_name="M2", modal_price=1000, price_date=date.today(), price_change_pct=20.0)
            ])
            await service.check_alerts_for_user("u1")
            await service.check_alerts_for_user("u2")
            
        # u1 gets email, u2 does not (preference disabled)
        assert mock_provider.execute_with_retry.call_count == 1
        
        # Both get in-app notifications
        n1 = (await db.execute(select(Notification).where(Notification.user_id == "u1"))).scalars().all()
        n2 = (await db.execute(select(Notification).where(Notification.user_id == "u2"))).scalars().all()
        assert len(n1) == 1
        assert len(n2) == 1


@pytest.mark.asyncio
async def test_email_failure_does_not_prevent_in_app(db: AsyncSession, setup_data):
    """email failure does not prevent in-app notification"""
    service = MarketAlertService(db)
    
    with patch.object(service.market_service, "get_dashboard_summary", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = mock_summary([
            MarketSummaryItem(commodity="Tomato", market_name="M3", modal_price=1000, price_date=date.today(), price_change_pct=10.0)
        ])
        
        with patch("app.services.email_service.get_email_provider") as mock_get_provider:
            mock_provider = AsyncMock()
            mock_provider.provider_name = "test_provider"
            # Simulate a failure in execute_with_retry
            mock_provider.execute_with_retry.side_effect = Exception("SMTP down")
            mock_get_provider.return_value = mock_provider
            
            alerts = await service.check_alerts_for_user("u1")
            
    assert alerts == 1
    n = (await db.execute(select(Notification).where(Notification.user_id == "u1"))).scalars().first()
    assert n is not None


@pytest.mark.asyncio
async def test_market_service_failure_is_safe(db: AsyncSession, setup_data):
    """market-service/data failure fails safely"""
    service = MarketAlertService(db)
    
    with patch.object(service.market_service, "get_dashboard_summary", new_callable=AsyncMock, side_effect=Exception("DB Error")):
        alerts = await service.check_alerts_for_user("u1")
        
    assert alerts == 0

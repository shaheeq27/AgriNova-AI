import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI
from datetime import datetime, timezone, timedelta

from app.models.notification import Notification
from app.models.notification_preference import NotificationPreference
from app.models.user import User
from app.core.database import Base
from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token
from main import app as original_app

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session

@pytest.fixture
def app(db_session):
    original_app.dependency_overrides[get_db] = lambda: db_session
    yield original_app
    original_app.dependency_overrides.clear()

@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.fixture
async def test_user(db_session):
    u = User(
        email="farmer@example.com",
        full_name="Test Farmer",
        hashed_password="fakehash",
    )
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u

@pytest.fixture
def test_user_token_headers(test_user):
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
async def other_user(db_session):
    u = User(
        email="other@example.com",
        full_name="Other Farmer",
        hashed_password="fakehash",
    )
    db_session.add(u)
    await db_session.commit()
    await db_session.refresh(u)
    return u

@pytest.fixture
def other_user_token_headers(other_user):
    token = create_access_token(other_user.id)
    return {"Authorization": f"Bearer {token}"}

async def test_get_preferences_default(client: AsyncClient, test_user, test_user_token_headers):
    # Should return defaults if none exist in DB
    response = await client.get("/api/v1/preferences/notifications", headers=test_user_token_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email_enabled"] is True
    assert data["weather_alerts"] is True
    assert data["market_alerts"] is True
    
async def test_update_preferences(client: AsyncClient, test_user, test_user_token_headers):
    update_payload = {
        "email_enabled": False,
        "market_alerts": False
    }
    response = await client.put(
        "/api/v1/preferences/notifications", 
        json=update_payload, 
        headers=test_user_token_headers
    )
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email_enabled"] is False
    assert data["market_alerts"] is False
    assert data["weather_alerts"] is True  # Unchanged
    
    # Verify in DB
    response = await client.get("/api/v1/preferences/notifications", headers=test_user_token_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["email_enabled"] is False
    
async def test_update_preferences_invalid_fields(client: AsyncClient, test_user_token_headers):
    update_payload = {
        "invalid_field": False
    }
    # Extra fields might be ignored by pydantic or return 422 depending on config,
    # but the valid ones should work, or it should 422.
    response = await client.put(
        "/api/v1/preferences/notifications", 
        json=update_payload, 
        headers=test_user_token_headers
    )
    assert response.status_code in (200, 422)

async def test_cross_user_preferences_protection(client: AsyncClient, other_user, other_user_token_headers, test_user_token_headers):
    # other_user has email_enabled=False
    update_payload = {"email_enabled": False}
    await client.put("/api/v1/preferences/notifications", json=update_payload, headers=other_user_token_headers)
    
    # test_user still has True
    response = await client.get("/api/v1/preferences/notifications", headers=test_user_token_headers)
    assert response.json()["data"]["email_enabled"] is True

async def test_get_notifications_pagination_and_category(client: AsyncClient, db_session, test_user, test_user_token_headers):
    # Create some notifications
    for i in range(15):
        n = Notification(
            user_id=test_user.id,
            title=f"Weather {i}",
            message="Test",
            type="weather_alert"
        )
        db_session.add(n)
        
    for i in range(5):
        n = Notification(
            user_id=test_user.id,
            title=f"Market {i}",
            message="Test",
            type="market_alert"
        )
        db_session.add(n)
        
    await db_session.commit()
    
    # Test pagination
    response = await client.get("/api/v1/notifications?limit=10&skip=0", headers=test_user_token_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == 10
    
    # Test category filter
    response = await client.get("/api/v1/notifications?category=market", headers=test_user_token_headers)
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data["items"]) == 5
    for item in data["items"]:
        assert item["type"] == "market_alert"
        
    # Test invalid category
    response = await client.get("/api/v1/notifications?category=invalid", headers=test_user_token_headers)
    assert response.status_code == 422

async def test_mark_read_cross_user_protection(client: AsyncClient, db_session, test_user, other_user, other_user_token_headers):
    n = Notification(
        user_id=test_user.id,
        title="Test",
        message="Test",
        type="weather_alert"
    )
    db_session.add(n)
    await db_session.commit()
    
    # other_user tries to mark test_user's notification as read
    response = await client.put(f"/api/v1/notifications/{n.id}/read", headers=other_user_token_headers)
    assert response.status_code == 404

async def test_mark_read_success(client: AsyncClient, db_session, test_user, test_user_token_headers):
    n = Notification(
        user_id=test_user.id,
        title="Test",
        message="Test",
        type="weather_alert"
    )
    db_session.add(n)
    await db_session.commit()
    
    response = await client.put(f"/api/v1/notifications/{n.id}/read", headers=test_user_token_headers)
    assert response.status_code == 200
    assert response.json()["data"]["is_read"] is True

async def test_mark_all_read(client: AsyncClient, db_session, test_user, test_user_token_headers):
    for i in range(3):
        n = Notification(
            user_id=test_user.id,
            title="Test",
            message="Test",
            type="weather_alert"
        )
        db_session.add(n)
    await db_session.commit()
    
    response = await client.put("/api/v1/notifications/read-all", headers=test_user_token_headers)
    assert response.status_code == 200
    assert response.json()["data"]["updated_count"] == 3

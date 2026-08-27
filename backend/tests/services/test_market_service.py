import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI

from app.core.database import Base
from app.api.v1.market import router as market_router
from app.models.market_price import MarketPrice

# Mock app setup for integration tests
app = FastAPI()
app.include_router(market_router, prefix="/api/v1")

@pytest.fixture
async def db():
    """Create in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session

@pytest.fixture
async def client(db):
    """Override get_db dependency for tests."""
    from app.core.database import get_db
    
    async def override_get_db():
        yield db
        
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as ac:
        yield ac
        
    app.dependency_overrides.clear()

pytestmark = pytest.mark.asyncio

async def test_market_refresh_endpoint(client: AsyncClient):
    """Test that the refresh endpoint fetches data and populates the DB."""
    # 1. Check initial state
    res = await client.get("/api/v1/market/status")
    assert res.status_code == 200
    assert res.json()["data"]["total_records"] == 0
    
    # 2. Trigger refresh
    res = await client.post("/api/v1/market/refresh")
    assert res.status_code == 200
    data = res.json()["data"]
    assert data["records_fetched"] > 0
    
    # 3. Check status again
    res = await client.get("/api/v1/market/status")
    assert res.status_code == 200
    assert res.json()["data"]["total_records"] == data["records_fetched"]

async def test_market_prices_endpoint(client: AsyncClient):
    """Test fetching prices for a specific crop."""
    await client.post("/api/v1/market/refresh")
    
    # Get Tomato prices
    res = await client.get("/api/v1/market/prices?commodity=Tomato")
    assert res.status_code == 200
    
    data = res.json()["data"]
    assert data["data_status"] == "live"
    assert data["last_updated"] is not None
    assert data["total"] > 0
    
    # Check that price change is None for the first fetch (no previous data)
    assert data["items"][0]["price_change_pct"] is None
    
    # Get by market
    res2 = await client.get("/api/v1/market/prices/Azadpur")
    assert res2.status_code == 200
    assert len(res2.json()["data"]["items"]) > 0

async def test_market_comparison_endpoint(client: AsyncClient):
    """Test cross-market comparison."""
    await client.post("/api/v1/market/refresh")
    
    res = await client.get("/api/v1/market/compare?commodity=Tomato&markets=Azadpur&markets=Vashi")
    assert res.status_code == 200
    
    data = res.json()["data"]
    assert data["commodity"] == "Tomato"
    assert len(data["markets"]) > 0

async def test_market_summary_endpoint(client: AsyncClient):
    """Test the dashboard summary endpoint."""
    await client.post("/api/v1/market/refresh")
    
    res = await client.get("/api/v1/market/summary?commodities=Tomato&commodities=Rice")
    assert res.status_code == 200
    
    data = res.json()["data"]
    assert len(data["items"]) > 0
    
    # Find Tomato
    tomato_item = next(i for i in data["items"] if i["commodity"] == "Tomato")
    assert tomato_item["modal_price"] > 0

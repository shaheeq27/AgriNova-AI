import pytest
from httpx import AsyncClient, ASGITransport
from main import app as original_app
from unittest.mock import patch, AsyncMock
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.models.user import User

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with Session() as session:
        yield session

@pytest.fixture
def app(db):
    original_app.dependency_overrides[get_db] = lambda: db
    yield original_app
    original_app.dependency_overrides.clear()

@pytest.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_v6_recommend_unauthenticated_returns_401(client: AsyncClient):
    req_payload = {
        "soil_type": "Loamy",
        "temperature": 25.0,
        "humidity": 60.0,
        "rainfall": 50.0
    }

    with patch("app.services.crop_recommendation.orchestrator.RecommendationOrchestrator.recommend", new_callable=AsyncMock) as mock_recommend:
        response = await client.post("/api/v1/crops/v6/recommend", json=req_payload)
        assert response.status_code == 401

        # Verify it does not reach the expensive recommendation path
        mock_recommend.assert_not_called()

@pytest.mark.asyncio
async def test_v6_recommend_authenticated_succeeds(client: AsyncClient, app):
    req_payload = {
        "soil_type": "Loamy",
        "temperature": 25.0,
        "humidity": 60.0,
        "rainfall": 50.0
    }

    mock_user = User(id="user1", email="test@example.com", full_name="Test", is_active=True)
    app.dependency_overrides[get_current_user] = lambda: mock_user

    # Mock the orchestrator response to avoid external network calls
    class MockResponse:
        def model_dump(self, mode="json"):
            return {"recommendations": [], "input_conditions_used": {}}
        recommendations = []

    with patch("app.services.crop_recommendation.orchestrator.RecommendationOrchestrator.recommend", new_callable=AsyncMock) as mock_recommend:
        mock_recommend.return_value = MockResponse()
        response = await client.post("/api/v1/crops/v6/recommend", json=req_payload)

        assert response.status_code == 200
        json_resp = response.json()
        assert json_resp["status"] == "success"

        # Verify recommendation logic was invoked for the authenticated user
        mock_recommend.assert_called_once()

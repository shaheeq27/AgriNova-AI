import pytest
from httpx import AsyncClient, ASGITransport
from main import app as original_app
from unittest.mock import patch, AsyncMock
from app.api.deps import get_db, get_current_user
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.core.rate_limit import auth_rate_limit, disease_rate_limit
from app.core.config import settings
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

@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Reset rate limiters before every test to ensure test isolation."""
    auth_rate_limit.reset()
    disease_rate_limit.reset()
    yield
    auth_rate_limit.reset()
    disease_rate_limit.reset()

@pytest.mark.asyncio
async def test_auth_login_rate_limiting(client: AsyncClient):
    payload = {"email": "test@example.com", "password": "wrongpassword"}
    
    # Send requests up to limit
    for _ in range(settings.AUTH_RATE_LIMIT_REQUESTS):
        res = await client.post("/api/v1/auth/login", json=payload)
        # Assuming it returns 401 for wrong credentials normally
        assert res.status_code != 429

    # Exceed limit
    res_429 = await client.post("/api/v1/auth/login", json=payload)
    assert res_429.status_code == 429
    assert "retry-after" in res_429.headers

@pytest.mark.asyncio
async def test_auth_rate_limit_isolation_per_ip(app):
    payload = {"email": "test@example.com", "password": "wrongpassword"}
    
    async with AsyncClient(transport=ASGITransport(app=app, client=("192.168.1.1", 1234)), base_url="http://test") as client1:
        for _ in range(settings.AUTH_RATE_LIMIT_REQUESTS):
            await client1.post("/api/v1/auth/login", json=payload)
            
        res = await client1.post("/api/v1/auth/login", json=payload)
        assert res.status_code == 429

    # Different IP should not be rate limited
    async with AsyncClient(transport=ASGITransport(app=app, client=("192.168.1.2", 1234)), base_url="http://test") as client2:
        res2 = await client2.post("/api/v1/auth/login", json=payload)
        assert res2.status_code != 429

@pytest.mark.asyncio
async def test_disease_analyze_rate_limiting(client: AsyncClient, app):
    mock_user = User(id="user1", email="test@example.com", full_name="Test", is_active=True)
    app.dependency_overrides[get_current_user] = lambda: mock_user

    files = {"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
    
    with patch("app.services.disease_service.DiseaseService.analyze_image", new_callable=AsyncMock) as mock_analyze:
        # We need a proper response to avoid 500 when it succeeds.
        from app.schemas.disease import ImageAnalysisResponse, MLModelPrediction
        mock_analyze.return_value = ImageAnalysisResponse(
            model_prediction=MLModelPrediction(predicted_crop="Apple", predicted_disease="Healthy", model_probability=0.99, is_healthy=True),
            knowledge_base_evidence=None
        )
        
        # Requests up to limit
        for _ in range(settings.DISEASE_RATE_LIMIT_REQUESTS):
            # Must recreate files dict because httpx closes files after request
            files = {"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
            res = await client.post("/api/v1/disease/analyze-image", files=files)
            assert res.status_code == 200
            
        assert mock_analyze.call_count == settings.DISEASE_RATE_LIMIT_REQUESTS

        # Exceed limit
        files = {"file": ("test.jpg", b"fake image bytes", "image/jpeg")}
        res_429 = await client.post("/api/v1/disease/analyze-image", files=files)
        assert res_429.status_code == 429
        
        # Ensure expensive logic was NOT called again
        assert mock_analyze.call_count == settings.DISEASE_RATE_LIMIT_REQUESTS


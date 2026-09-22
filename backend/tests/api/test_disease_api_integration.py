import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI
from unittest.mock import patch, MagicMock, AsyncMock

from app.models.user import User
from app.core.database import Base
from app.api.deps import get_db, get_current_user
from app.core.security import create_access_token
from main import app as original_app
from app.schemas.disease import ImageAnalysisResponse, MLModelPrediction, KBDiseaseInfo
from app.services.disease_detection.exceptions import ImageProcessingError, EngineInferenceError
from app.core.exceptions import AgriNovaException

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
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c

@pytest.fixture
async def test_user(db_session):
    u = User(
        email="farmer@example.com",
        full_name="Farmer Bob",
        hashed_password="fakehash",
        is_active=True
    )
    db_session.add(u)
    await db_session.commit()
    return u

@pytest.fixture
def test_user_token_headers(test_user):
    token = create_access_token(test_user.id)
    return {"Authorization": f"Bearer {token}"}

def mock_service_response(disease="Early Blight", crop="Tomato", is_healthy=False, has_kb=True):
    ml_pred = MLModelPrediction(
        predicted_crop=crop,
        predicted_disease=disease,
        model_probability=0.99,
        is_healthy=is_healthy
    )
    kb = None
    if has_kb and not is_healthy:
        kb = KBDiseaseInfo(
            disease_name=disease,
            symptoms="Spots",
            treatment="Spray",
            prevention="Clean",
            severity="high"
        )
    return ImageAnalysisResponse(model_prediction=ml_pred, knowledge_base_evidence=kb)

async def test_analyze_image_success(client: AsyncClient, test_user_token_headers):
    with patch('app.api.v1.disease.DiseaseService') as mock_service_cls:
        mock_service = mock_service_cls.return_value
        mock_service.analyze_image = AsyncMock(return_value=mock_service_response())

        files = {"file": ("test.jpg", b"fake_image", "image/jpeg")}
        response = await client.post("/api/v1/disease/analyze-image", files=files, headers=test_user_token_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["model_prediction"]["predicted_crop"] == "Tomato"
        assert data["model_prediction"]["model_probability"] == 0.99
        assert data["knowledge_base_evidence"]["disease_name"] == "Early Blight"
        assert data["knowledge_base_evidence"]["severity"] == "high"

async def test_analyze_image_healthy(client: AsyncClient, test_user_token_headers):
    with patch('app.api.v1.disease.DiseaseService') as mock_service_cls:
        mock_service = mock_service_cls.return_value
        mock_service.analyze_image = AsyncMock(return_value=mock_service_response(disease="Healthy", crop="Tomato", is_healthy=True, has_kb=False))

        files = {"file": ("test.jpg", b"fake_image", "image/jpeg")}
        response = await client.post("/api/v1/disease/analyze-image", files=files, headers=test_user_token_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["model_prediction"]["is_healthy"] is True
        assert data["knowledge_base_evidence"] is None

async def test_analyze_image_no_kb(client: AsyncClient, test_user_token_headers):
    with patch('app.api.v1.disease.DiseaseService') as mock_service_cls:
        mock_service = mock_service_cls.return_value
        mock_service.analyze_image = AsyncMock(return_value=mock_service_response(disease="Unknown", crop="Maize", has_kb=False))

        files = {"file": ("test.jpg", b"fake_image", "image/jpeg")}
        response = await client.post("/api/v1/disease/analyze-image", files=files, headers=test_user_token_headers)

        assert response.status_code == 200
        data = response.json()["data"]
        assert data["model_prediction"]["predicted_disease"] == "Unknown"
        assert data["knowledge_base_evidence"] is None

async def test_analyze_image_unauthorized(client: AsyncClient):
    files = {"file": ("test.jpg", b"fake_image", "image/jpeg")}
    response = await client.post("/api/v1/disease/analyze-image", files=files)
    assert response.status_code == 401 # Should trigger FastAPI security

async def test_analyze_image_invalid_type(client: AsyncClient, test_user_token_headers):
    files = {"file": ("test.txt", b"fake text", "text/plain")}
    response = await client.post("/api/v1/disease/analyze-image", files=files, headers=test_user_token_headers)
    assert response.status_code == 400
    assert "Invalid file type" in response.json()["message"]

async def test_analyze_image_too_large(client: AsyncClient, test_user_token_headers):
    large_bytes = b"a" * (10 * 1024 * 1024 + 1) # > 10MB
    files = {"file": ("test.jpg", large_bytes, "image/jpeg")}
    response = await client.post("/api/v1/disease/analyze-image", files=files, headers=test_user_token_headers)
    assert response.status_code == 400
    assert "File too large" in response.json()["message"]

async def test_analyze_image_service_failure(client: AsyncClient, test_user_token_headers):
    with patch('app.api.v1.disease.DiseaseService') as mock_service_cls:
        mock_service = mock_service_cls.return_value
        # The service would raise an AgriNovaException for model failures
        mock_service.analyze_image = AsyncMock(side_effect=AgriNovaException("Model failed", status_code=500))

        files = {"file": ("test.jpg", b"fake_image", "image/jpeg")}
        response = await client.post("/api/v1/disease/analyze-image", files=files, headers=test_user_token_headers)

        assert response.status_code == 500
        assert "Model failed" in response.json()["message"]

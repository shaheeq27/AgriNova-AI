import pytest
from httpx import AsyncClient, ASGITransport
import io
from PIL import Image
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import FastAPI
import os

from app.models.user import User
from app.models.knowledge import DiseaseLibrary
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

    # Populate the KB with all possible disease outcomes from V6.6 mapping
    # just to be sure we get a KB match if it predicts a disease.
    async with Session() as session:
        diseases = [
            ("Leaf curl", "Chili"), ("Leaf spot", "Chili"), ("Yellowish", "Chili"),
            ("Blight", "Maize"), ("Common Rust", "Maize"), ("Gray Leaf Spot", "Maize"),
            ("Early Blight", "Potato"), ("Late Blight", "Potato"),
            ("Bacterial Spot", "Tomato"), ("Early Blight", "Tomato"), ("Late Blight", "Tomato"),
            ("Septoria Leaf Spot", "Tomato")
        ]
        for d_name, d_crop in diseases:
            kb = DiseaseLibrary(
                disease_name=d_name,
                affected_crops=d_crop,
                symptoms="Test symptom",
                treatment="Test treatment",
                prevention="Test prevention",
                severity="medium"
            )
            session.add(kb)
        await session.commit()

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
        email="e2efarmer@example.com",
        full_name="E2E Farmer",
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

def generate_test_image(color=(34, 139, 34)): # Forest Green
    img = Image.new("RGB", (300, 300), color=color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()

async def test_e2e_analyze_image_valid(client: AsyncClient, test_user_token_headers):
    # E2E test without mocking ML Engine
    img_bytes = generate_test_image()
    files = {"file": ("leaf.jpg", img_bytes, "image/jpeg")}

    response = await client.post("/api/v1/disease/analyze-image", files=files, headers=test_user_token_headers)
    assert response.status_code == 200

    data = response.json()["data"]

    # Assert model prediction exists
    model_pred = data["model_prediction"]
    assert "predicted_crop" in model_pred
    assert "predicted_disease" in model_pred
    assert "model_probability" in model_pred
    assert "is_healthy" in model_pred

    # Assert KB evidence behaves correctly
    kb = data["knowledge_base_evidence"]
    if model_pred["is_healthy"]:
        assert kb is None
    else:
        assert kb is not None
        assert kb["disease_name"] == model_pred["predicted_disease"]
        assert "severity" in kb
        assert "confidence" not in model_pred # Enforce nomenclature

async def test_e2e_analyze_image_invalid_bytes(client: AsyncClient, test_user_token_headers):
    files = {"file": ("bad.jpg", b"not an image", "image/jpeg")}
    response = await client.post("/api/v1/disease/analyze-image", files=files, headers=test_user_token_headers)

    # Preprocessor should fail and raise ImageProcessingError -> 400
    assert response.status_code == 400
    assert "Image analysis failed" in response.json()["message"]

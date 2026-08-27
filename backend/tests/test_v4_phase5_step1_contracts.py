import pytest
from httpx import AsyncClient
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.timeline import CropTimeline
from app.models.knowledge import DiseaseLibrary, CropProfile
from app.models.disease import DiseaseRecord
from app.models.fertilizer import FertilizerLog
from app.models.irrigation import IrrigationLog
from app.core.security import create_access_token

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.database import Base
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    async with TestingSessionLocal() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def async_client(db):
    from main import app
    from app.api.deps import get_db
    
    async def override_get_db():
        yield db
        
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()

@pytest.fixture
async def setup_test_data(db: AsyncSession):
    # User 1 (Has heavy history)
    u1 = User(id="u_test_contract_1", email="u1@test.com", hashed_password="x", full_name="User 1")
    # User 2 (Has empty history)
    u2 = User(id="u_test_contract_2", email="u2@test.com", hashed_password="x", full_name="User 2")
    db.add_all([u1, u2])
    
    # Knowledge
    dl = DiseaseLibrary(disease_name="Rust", affected_crops="Wheat", symptoms="yellow spots, brown spots", treatment="Fungicide", prevention="Spacing", severity="high")
    cp = CropProfile(crop_name="Wheat", temp_min=10, temp_max=25, humidity_min=40, humidity_max=60, rain_min=200, rain_max=500, ideal_soil_types="Loam, Clay", growing_season="Rabi")
    db.add_all([dl, cp])

    # Farm 1 (Heavy History)
    f1 = Farm(id="f_contract_1", user_id="u_test_contract_1", name="Farm 1", location_city="Pune", soil_type="Loam", total_area_acres=10.0)
    # Farm 2 (Empty History)
    f2 = Farm(id="f_contract_2", user_id="u_test_contract_2", name="Farm 2", location_city="Pune", soil_type="Loam", total_area_acres=10.0)
    db.add_all([f1, f2])

    # Crop with heavy history on Farm 1
    prev_crops = []
    for i in range(5):
        prev_crops.append(
            Crop(id=f"c_prev_{i}", farm_id="f_contract_1", crop_name="Wheat", variety="A", season="Rabi",
                 planting_date=date(2020+i, 1, 1), actual_harvest_date=date(2020+i, 4, 1),
                 status="harvested", area_acres=5.0, yield_amount=2000.0 + i*100, yield_unit="kg") # Increasing trend
        )
    db.add_all(prev_crops)

    # Active crop for context on Farm 1
    active_crop = Crop(id="c_active_1", farm_id="f_contract_1", crop_name="Wheat", variety="A", season="Rabi", planting_date=date(2025, 1, 1), status="active", area_acres=5.0)
    db.add(active_crop)
    db.add(CropTimeline(id="ct1", crop_id="c_active_1", stage_name="Seedling", stage_order=1, start_date=date(2025, 1, 1), end_date=date(2025, 12, 31), status="in_progress"))

    # Add heavy logs for prev crop 0
    ferts = [FertilizerLog(id=f"fl_{i}", crop_id=prev_crops[0].id, fertilizer_type="Urea", quantity=50.0, unit="kg", date=date(2024, 2, i+1)) for i in range(4)]
    irrs = [IrrigationLog(id=f"il_{i}", crop_id=prev_crops[0].id, water_amount_liters=20.0, date=date(2024, 1, i+1), growth_stage="Seedling") for i in range(6)]
    dis = [DiseaseRecord(id=f"dl_{i}", crop_id=prev_crops[0].id, disease_name="Rust", severity="high", status="resolved", outcome="Treated") for i in range(3)]
    
    db.add_all(ferts + irrs + dis)
    await db.commit()

    # Generate tokens
    token_u1 = create_access_token("u_test_contract_1")
    token_u2 = create_access_token("u_test_contract_2")

    return {"token_u1": token_u1, "token_u2": token_u2, "f1_id": "f_contract_1", "f2_id": "f_contract_2"}

@pytest.mark.asyncio
async def test_crop_recommendation_contracts(async_client: AsyncClient, setup_test_data):
    client = async_client
    token = setup_test_data["token_u1"]
    f1_id = setup_test_data["f1_id"]
    headers = {"Authorization": f"Bearer {token}"}
    base_payload = {
        "temperature": 20.0, "humidity": 50.0, "rainfall": 300.0, "soil_type": "Loam",
        "n": 50.0, "p": 35.0, "k": 35.0, "ph": 6.5
    }

    # A. Crop recommendation with no farm_id (Public/No Auth)
    res_no_farm = await client.post("/api/v1/crops/recommend", json=base_payload)
    assert res_no_farm.status_code == 200
    recs = res_no_farm.json()["data"]["recommendations"]
    assert len(recs) > 0
    assert "historically_adjusted" in recs[0]
    assert recs[0]["historically_adjusted"] is False

    # B. Crop recommendation with farm_id (Heavy History) -> Auth required now because of our patch!
    res_auth = await client.post("/api/v1/crops/recommend", json={**base_payload, "farm_id": f1_id}, headers=headers)
    assert res_auth.status_code == 200
    recs_auth = res_auth.json()["data"]["recommendations"]
    wheat_rec = next((r for r in recs_auth if r["crop_name"] == "Wheat"), None)
    if wheat_rec:
        assert wheat_rec["historically_adjusted"] is True
        assert wheat_rec["personalization_rationale"] is not None
        
    # Test unauth with farm_id
    res_unauth = await client.post("/api/v1/crops/recommend", json={**base_payload, "farm_id": f1_id})
    assert res_unauth.status_code == 401


@pytest.mark.asyncio
async def test_fertilizer_contracts(async_client: AsyncClient, setup_test_data):
    client = async_client
    token = setup_test_data["token_u1"]
    f1_id = setup_test_data["f1_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # C. Fertilizer with no farm_id
    res_no_farm = await client.get("/api/v1/fertilizer/recommend/Wheat?stage=Seedling&soil_type=Loam", headers=headers)
    assert res_no_farm.status_code == 200
    data = res_no_farm.json()["data"]
    assert "historically_adjusted" in data
    assert data["historically_adjusted"] is False

    # D. Fertilizer with farm_id + heavy historical usage
    res_farm = await client.get(f"/api/v1/fertilizer/recommend/Wheat?stage=Seedling&soil_type=Loam&farm_id={f1_id}", headers=headers)
    assert res_farm.status_code == 200
    data_farm = res_farm.json()["data"]
    assert data_farm["historically_adjusted"] is True
    assert data_farm["personalization_rationale"] is not None
    assert "reduced" in data_farm["personalization_rationale"].lower()


@pytest.mark.asyncio
async def test_irrigation_contracts(async_client: AsyncClient, setup_test_data):
    client = async_client
    token = setup_test_data["token_u1"]
    f1_id = setup_test_data["f1_id"]
    headers = {"Authorization": f"Bearer {token}"}

    # E. Irrigation with farm_id + heavy historical usage
    res_farm = await client.get(f"/api/v1/irrigation/recommend/Wheat?stage=Seedling&soil_type=Loam&farm_id={f1_id}", headers=headers)
    assert res_farm.status_code == 200
    data = res_farm.json()["data"]
    assert data["historically_adjusted"] is True
    assert data["personalization_rationale"] is not None


@pytest.mark.asyncio
async def test_disease_contracts(async_client: AsyncClient, setup_test_data):
    client = async_client
    token = setup_test_data["token_u1"]
    f1_id = setup_test_data["f1_id"]
    headers = {"Authorization": f"Bearer {token}"}
    payload = {"crop_name": "Wheat", "symptoms": ["yellow spots", "brown spots"]}

    # F. Disease with relevant historical recurrence
    res_farm = await client.post("/api/v1/disease/detect", json={**payload, "farm_id": f1_id}, headers=headers)
    assert res_farm.status_code == 200
    matches = res_farm.json()["data"]["matches"]
    rust = next((m for m in matches if m["disease_name"] == "Rust"), None)
    if rust:
        assert rust["historically_adjusted"] is True
        assert rust["personalization_rationale"] is not None

@pytest.mark.asyncio
async def test_historical_insights_endpoint(async_client: AsyncClient, setup_test_data):
    client = async_client
    token1 = setup_test_data["token_u1"]
    token2 = setup_test_data["token_u2"]
    f1_id = setup_test_data["f1_id"]
    f2_id = setup_test_data["f2_id"]

    # G. Historical insights endpoint -> returns valid schema
    res1 = await client.get(f"/api/v1/farms/{f1_id}/insights", headers={"Authorization": f"Bearer {token1}"})
    assert res1.status_code == 200
    data1 = res1.json()["data"]
    assert "yield_trends" in data1
    assert "input_usage" in data1
    assert len(data1["yield_trends"]) > 0

    # H. Unauthorized/non-owned farm -> rejected
    res_unauth = await client.get(f"/api/v1/farms/{f1_id}/insights", headers={"Authorization": f"Bearer {token2}"})
    assert res_unauth.status_code == 403

    # I. Empty/new farm -> valid response -> no fabricated personalization
    res2 = await client.get(f"/api/v1/farms/{f2_id}/insights", headers={"Authorization": f"Bearer {token2}"})
    assert res2.status_code == 200
    data2 = res2.json()["data"]
    assert len(data2["yield_trends"]) == 0

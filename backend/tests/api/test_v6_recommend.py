import pytest
from httpx import AsyncClient, ASGITransport
from main import app

@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client

@pytest.mark.asyncio
async def test_v6_recommend_api_contract(async_client: AsyncClient):
    req_payload = {
        "soil_type": "Loamy",
        "temperature": 25.0,
        "humidity": 60.0,
        "rainfall": 50.0
    }
    response = await async_client.post("/api/v1/crops/v6/recommend", json=req_payload)

    assert response.status_code == 200
    json_resp = response.json()

    # Must use standard APIResponse envelope
    assert "status" in json_resp
    assert json_resp["status"] == "success"
    assert "data" in json_resp
    assert "message" in json_resp

    data = json_resp["data"]
    # Ensure it's CropRecommendationResponseV6
    assert "recommendations" in data
    assert "input_conditions_used" in data

import pytest
from httpx import AsyncClient, ASGITransport
from main import app as original_app
from unittest.mock import patch, AsyncMock
from app.api.deps import get_current_user, get_db
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.timeline import DailyTask
from app.core.security import hash_password
import uuid
from datetime import date

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

@pytest.fixture
async def setup_test_data(db: AsyncSession):
    user_a = User(id="user_a", email="a@example.com", hashed_password="pwd", full_name="User A", is_active=True)
    user_b = User(id="user_b", email="b@example.com", hashed_password="pwd", full_name="User B", is_active=True)

    farm_a = Farm(id="farm_a", user_id="user_a", name="Farm A", location_city="City", location_state="State", total_area_acres=10.0, soil_type="Loam", water_source="Well")
    farm_b = Farm(id="farm_b", user_id="user_b", name="Farm B", location_city="City", location_state="State", total_area_acres=10.0, soil_type="Loam", water_source="Well")

    crop_a = Crop(id="crop_a", farm_id="farm_a", crop_name="Wheat", variety="V1", season="Summer", planting_date=date.today(), area_acres=5.0)
    crop_b = Crop(id="crop_b", farm_id="farm_b", crop_name="Corn", variety="V1", season="Summer", planting_date=date.today(), area_acres=5.0)

    from app.models.timeline import CropTimeline

    timeline_a = CropTimeline(id="timeline_a", crop_id="crop_a", stage_name="Initial", stage_order=1, start_date=date.today(), end_date=date.today())
    timeline_b = CropTimeline(id="timeline_b", crop_id="crop_b", stage_name="Initial", stage_order=1, start_date=date.today(), end_date=date.today())

    task_a = DailyTask(id="task_a", timeline_id="timeline_a", crop_id="crop_a", title="Task A", scheduled_date=date.today())
    task_b = DailyTask(id="task_b", timeline_id="timeline_b", crop_id="crop_b", title="Task B", scheduled_date=date.today())

    db.add_all([user_a, user_b, farm_a, farm_b, crop_a, crop_b, timeline_a, timeline_b, task_a, task_b])
    await db.commit()

    return {"user_a": user_a, "user_b": user_b, "task_a": task_a, "task_b": task_b}

@pytest.mark.asyncio
async def test_owner_can_update_own_task(client: AsyncClient, app, setup_test_data):
    app.dependency_overrides[get_current_user] = lambda: setup_test_data["user_a"]

    payload = {"is_completed": True, "notes": "Done"}
    response = await client.put("/api/v1/crops/tasks/task_a", json=payload)

    assert response.status_code == 200
    assert response.json()["data"]["is_completed"] is True
    assert response.json()["data"]["notes"] == "Done"

@pytest.mark.asyncio
async def test_user_cannot_update_others_task(client: AsyncClient, app, setup_test_data):
    app.dependency_overrides[get_current_user] = lambda: setup_test_data["user_a"]

    payload = {"is_completed": True, "notes": "Hacked"}
    response = await client.put("/api/v1/crops/tasks/task_b", json=payload)

    # Existing behavior from FarmService might raise 403 or 404 depending on how NotFoundException vs Forbidden is handled
    # Wait, _check_farm_ownership raises 403 Forbidden
    assert response.status_code == 403

@pytest.mark.asyncio
async def test_nonexistent_task_returns_404(client: AsyncClient, app, setup_test_data):
    app.dependency_overrides[get_current_user] = lambda: setup_test_data["user_a"]

    payload = {"is_completed": True, "notes": "Hacked"}
    response = await client.put("/api/v1/crops/tasks/task_missing", json=payload)

    assert response.status_code == 404


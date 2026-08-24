
import json
from datetime import date
import pytest
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select

from app.core.database import Base
from app.models.user import User
from app.models.farm import Farm
from app.models.crop import Crop
from app.models.activity_log import ActivityLog

from app.schemas.fertilizer import FertilizerLogCreate
from app.schemas.irrigation import IrrigationLogCreate
from app.schemas.disease import DiseaseRecordCreate, DiseaseRecordUpdate
from app.schemas.crop import CropUpdate

from app.services.fertilizer_engine import FertilizerEngine
from app.services.irrigation_engine import IrrigationEngine
from app.services.disease_service import DiseaseService
from app.services.crop_service import CropService

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
    user = User(id="user1", email="test@test.com", hashed_password="123", full_name="Test")
    farm = Farm(id="farm1", user_id="user1", name="Test Farm", location_city="City", soil_type="Loamy", total_area_acres=10.0)
    crop = Crop(id="crop1", farm_id="farm1", crop_name="Wheat", season="Rabi", planting_date=date.today(), area_acres=5.0, status="active")
    
    db.add(user)
    db.add(farm)
    db.add(crop)
    await db.commit()
    
    return {"user_id": "user1", "farm_id": "farm1", "crop_id": "crop1"}


@pytest.mark.asyncio
async def test_fertilizer_application_logging(db: AsyncSession, setup_data):
    engine = FertilizerEngine()
    data = FertilizerLogCreate(
        crop_id=setup_data["crop_id"],
        date=date.today(),
        fertilizer_type="Urea",
        quantity=10,
        unit="kg",
        application_method="Broadcasting",
        growth_stage="Vegetative"
    )
    
    await engine.log_application(db, setup_data["user_id"], setup_data["crop_id"], data)
    
    # Check activity log
    result = await db.execute(select(ActivityLog).where(ActivityLog.action == "fertilizer_applied"))
    log = result.scalar_one()
    
    assert log.entity_type == "fertilizer"
    assert log.farm_id == setup_data["farm_id"]
    assert log.crop_id == setup_data["crop_id"]
    
    metadata = json.loads(log.metadata_json)
    assert metadata["fertilizer_type"] == "Urea"


@pytest.mark.asyncio
async def test_irrigation_performed_logging(db: AsyncSession, setup_data):
    engine = IrrigationEngine()
    data = IrrigationLogCreate(
        crop_id=setup_data["crop_id"],
        date=date.today(),
        water_amount_liters=500.0,
        duration_minutes=60.0,
        method="Drip",
        growth_stage="Vegetative"
    )
    
    await engine.log_irrigation(db, setup_data["user_id"], setup_data["crop_id"], data)
    
    result = await db.execute(select(ActivityLog).where(ActivityLog.action == "irrigation_performed"))
    log = result.scalar_one()
    
    assert log.entity_type == "irrigation"
    assert log.farm_id == setup_data["farm_id"]
    
    metadata = json.loads(log.metadata_json)
    assert metadata["method"] == "Drip"


@pytest.mark.asyncio
async def test_disease_treatment_and_resolution_logging(db: AsyncSession, setup_data):
    service = DiseaseService(db)
    
    # Create disease
    create_data = DiseaseRecordCreate(
        crop_id=setup_data["crop_id"],
        disease_name="Rust",
        severity="high",
        detection_source="manual"
    )
    record = await service.create_record_with_logging(setup_data["user_id"], setup_data["crop_id"], create_data)
    
    # Test Treatment (creates disease_treated)
    update_data = DiseaseRecordUpdate(treatment_applied="Fungicide X")
    await service.update_record(setup_data["user_id"], record.id, update_data)
    
    result = await db.execute(select(ActivityLog).where(ActivityLog.action == "disease_treated"))
    log_treat = result.scalar_one()
    assert log_treat.entity_type == "disease"
    assert log_treat.entity_id == record.id
    
    # Test duplicate prevention (same treatment, should not create another log)
    await service.update_record(setup_data["user_id"], record.id, DiseaseRecordUpdate(treatment_applied="Fungicide X", notes="still monitoring"))
    result = await db.execute(select(ActivityLog).where(ActivityLog.action == "disease_treated"))
    assert len(result.scalars().all()) == 1  # Still 1
    
    # Test Resolution (creates disease_resolved)
    await service.update_record(setup_data["user_id"], record.id, DiseaseRecordUpdate(status="resolved"))
    result = await db.execute(select(ActivityLog).where(ActivityLog.action == "disease_resolved"))
    log_res = result.scalar_one()
    assert log_res.entity_id == record.id


@pytest.mark.asyncio
async def test_crop_harvested_logging(db: AsyncSession, setup_data):
    service = CropService(db)
    
    # Test Harvest (creates crop_harvested)
    update_data = CropUpdate(status="harvested", yield_amount=100.0, yield_unit="kg")
    await service.update_crop(setup_data["user_id"], setup_data["crop_id"], update_data)
    
    result = await db.execute(select(ActivityLog).where(ActivityLog.action == "crop_harvested"))
    log = result.scalar_one()
    assert log.entity_type == "crop"
    assert log.entity_id == setup_data["crop_id"]
    
    # Test duplicate prevention (updating harvested crop shouldnt create another harvest log)
    await service.update_crop(setup_data["user_id"], setup_data["crop_id"], CropUpdate(status="harvested", notes="stored"))
    result = await db.execute(select(ActivityLog).where(ActivityLog.action == "crop_harvested"))
    assert len(result.scalars().all()) == 1  # Still 1

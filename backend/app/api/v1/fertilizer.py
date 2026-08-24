"""
AgriNova AI — Fertilizer API routes.
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.fertilizer import FertilizerLogCreate
from app.services.fertilizer_engine import FertilizerEngine


router = APIRouter(prefix="/fertilizer", tags=["Fertilizer"])


@router.get("/recommend/{crop_name}", response_model=APIResponse)
async def get_fertilizer_recommendation(
    crop_name: str,
    stage: str = Query(..., description="Growth stage"),
    soil_type: str = Query(..., description="Soil type"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = FertilizerEngine()
    recommendation = await engine.get_recommendation(db, crop_name, stage, soil_type)
    return APIResponse.success(data=recommendation)


@router.post("/log", response_model=APIResponse)
async def log_fertilizer(
    data: FertilizerLogCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = FertilizerEngine()
    log = await engine.log_application(db, current_user.id, data.crop_id, data)
    return APIResponse.success(data=log.model_dump(), message="Fertilizer log created")


@router.get("/logs/{crop_id}", response_model=APIResponse)
async def get_fertilizer_logs(
    crop_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    engine = FertilizerEngine()
    logs = await engine.get_logs(db, crop_id)
    return APIResponse.success(data=[log.model_dump() for log in logs])

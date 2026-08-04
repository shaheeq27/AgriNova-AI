"""
AgriNova AI — Knowledge Base API routes.
"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.models.knowledge import (
    CropProfile,
    DiseaseLibrary,
    FertilizerLibrary,
    GrowthStage,
    IrrigationGuideline,
)
from app.schemas.common import APIResponse
from app.schemas.knowledge import (
    CropProfileResponse,
    DiseaseLibraryResponse,
    FertilizerLibraryResponse,
    GrowthStageResponse,
    IrrigationGuidelineResponse,
)

router = APIRouter(prefix="/knowledge", tags=["Knowledge Base"])


# ── Crop Profiles ──


@router.get("/crops", response_model=APIResponse)
async def list_crop_profiles(db: AsyncSession = Depends(get_db)):
    """List all crop profiles in the knowledge base."""
    result = await db.execute(select(CropProfile).order_by(CropProfile.crop_name))
    profiles = result.scalars().all()
    data = [CropProfileResponse.model_validate(p).model_dump() for p in profiles]
    return APIResponse.success(data=data)


@router.get("/crops/{crop_name}", response_model=APIResponse)
async def get_crop_profile(crop_name: str, db: AsyncSession = Depends(get_db)):
    """Get a specific crop profile by name."""
    result = await db.execute(
        select(CropProfile).where(CropProfile.crop_name == crop_name)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        return APIResponse.error(message=f"Crop '{crop_name}' not found in knowledge base")
    return APIResponse.success(
        data=CropProfileResponse.model_validate(profile).model_dump()
    )


@router.get("/crops/{crop_name}/stages", response_model=APIResponse)
async def get_growth_stages(crop_name: str, db: AsyncSession = Depends(get_db)):
    """Get growth stages for a specific crop."""
    result = await db.execute(
        select(GrowthStage)
        .where(GrowthStage.crop_name == crop_name)
        .order_by(GrowthStage.stage_order)
    )
    stages = result.scalars().all()
    data = [GrowthStageResponse.model_validate(s).model_dump() for s in stages]
    return APIResponse.success(data=data)


# ── Disease Library ──


@router.get("/diseases", response_model=APIResponse)
async def list_diseases(db: AsyncSession = Depends(get_db)):
    """List all diseases in the knowledge base."""
    result = await db.execute(
        select(DiseaseLibrary).order_by(DiseaseLibrary.disease_name)
    )
    diseases = result.scalars().all()
    data = [DiseaseLibraryResponse.model_validate(d).model_dump() for d in diseases]
    return APIResponse.success(data=data)


# ── Fertilizer Library ──


@router.get("/fertilizers", response_model=APIResponse)
async def list_fertilizer_guidelines(
    crop_name: str | None = None, db: AsyncSession = Depends(get_db)
):
    """List fertilizer guidelines, optionally filtered by crop."""
    query = select(FertilizerLibrary)
    if crop_name:
        query = query.where(FertilizerLibrary.crop_name == crop_name)
    query = query.order_by(FertilizerLibrary.crop_name)
    result = await db.execute(query)
    guidelines = result.scalars().all()
    data = [FertilizerLibraryResponse.model_validate(g).model_dump() for g in guidelines]
    return APIResponse.success(data=data)


# ── Irrigation Guidelines ──


@router.get("/irrigation", response_model=APIResponse)
async def list_irrigation_guidelines(
    crop_name: str | None = None, db: AsyncSession = Depends(get_db)
):
    """List irrigation guidelines, optionally filtered by crop."""
    query = select(IrrigationGuideline)
    if crop_name:
        query = query.where(IrrigationGuideline.crop_name == crop_name)
    query = query.order_by(IrrigationGuideline.crop_name)
    result = await db.execute(query)
    guidelines = result.scalars().all()
    data = [IrrigationGuidelineResponse.model_validate(g).model_dump() for g in guidelines]
    return APIResponse.success(data=data)

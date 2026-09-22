"""
AgriNova AI — Disease detection API routes.
"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.core.exceptions import ForbiddenException, NotFoundException, AgriNovaException
from app.models.crop import Crop
from app.models.farm import Farm
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.disease import (
    DiseaseDetectionRequest,
    DiseaseDetectionResponse,
    DiseaseRecordCreate,
    DiseaseRecordUpdate,
)
from app.services.disease_service import DiseaseService
from app.repositories.disease_repo import DiseaseRepository

router = APIRouter(prefix="/disease", tags=["Disease Detection"])


async def verify_crop_ownership(db: AsyncSession, user_id: str, crop_id: str) -> None:
    """Helper to verify that the current user owns the crop."""
    # Fetch crop
    result = await db.execute(select(Crop).where(Crop.id == crop_id))
    crop = result.scalar_one_or_none()
    if not crop:
        raise NotFoundException("Crop", crop_id)

    # Fetch farm
    farm_result = await db.execute(select(Farm).where(Farm.id == crop.farm_id))
    farm = farm_result.scalar_one_or_none()
    if not farm or farm.user_id != user_id:
        raise ForbiddenException("You do not have access to this crop")


from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.security import decode_access_token
from app.repositories.user_repo import UserRepository
from fastapi import HTTPException, status, Security

security_optional = HTTPBearer(auto_error=False)

async def get_optional_user(db: AsyncSession, credentials: HTTPAuthorizationCredentials | None) -> User | None:
    if not credentials or not hasattr(credentials, 'credentials'):
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    repo = UserRepository(db)
    user = await repo.get_by_id(payload["sub"])
    if not user or not user.is_active:
        return None
    return user

@router.post("/detect", response_model=APIResponse)
async def detect_disease(
    data: DiseaseDetectionRequest,
    credentials: HTTPAuthorizationCredentials | None = Security(security_optional),
    db: AsyncSession = Depends(get_db),
):
    """Detect disease from symptoms (Public/Personalized if farm_id given)."""
    historical_insights = None
    if data.farm_id:
        user = await get_optional_user(db, credentials)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Must be logged in to use farm context")

        from app.services.farm_service import FarmService
        farm_service = FarmService(db)
        await farm_service.get_farm(user.id, data.farm_id) # Validates ownership

        from app.ai.services.historical_insights_service import HistoricalInsightsService
        insights_service = HistoricalInsightsService()
        historical_insights = await insights_service.compute_insights_context(db, data.farm_id)

    service = DiseaseService(db)
    matches = await service.detect_from_symptoms(data.crop_name, data.symptoms, historical_insights)
    return APIResponse.success(
        data={"matches": [m.model_dump() for m in matches]},
        message=f"Found {len(matches)} potential matches"
    )


@router.post("/upload/{crop_id}", response_model=APIResponse)
async def upload_image(
    crop_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a disease image for a crop."""
    await verify_crop_ownership(db, current_user.id, crop_id)

    service = DiseaseService(db)
    image = await service.upload_image(crop_id, file)

    # In V1.0, return a placeholder analysis result using symptom-based matching
    # We return the saved file path and a placeholder message
    return APIResponse.success(
        data={"file_path": image.file_path, "file_name": image.file_name},
        message="Image uploaded successfully. Symptom-based analysis active."
    )



@router.post("/analyze-image", response_model=APIResponse)
async def analyze_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Analyze a crop leaf image for disease using the ML Engine."""
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if file.content_type not in allowed_types:
        raise AgriNovaException("Invalid file type. Allowed types: jpeg, png, webp.", status_code=400)

    content = await file.read()
    if len(content) > 10 * 1024 * 1024:
        raise AgriNovaException("File too large. Maximum size is 10MB.", status_code=400)

    service = DiseaseService(db)
    result = await service.analyze_image(content)

    return APIResponse.success(
        data=result.model_dump(),
        message="Image analysis complete"
    )

@router.post("/record", response_model=APIResponse)
async def create_record(
    data: DiseaseRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a disease record."""
    await verify_crop_ownership(db, current_user.id, data.crop_id)

    service = DiseaseService(db)
    record = await service.create_record(data.crop_id, data)
    return APIResponse.success(
        data=record.model_dump(),
        message="Disease record created successfully"
    )


@router.get("/records/{crop_id}", response_model=APIResponse)
async def get_records(
    crop_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all disease records for a crop."""
    await verify_crop_ownership(db, current_user.id, crop_id)

    service = DiseaseService(db)
    records = await service.get_records(crop_id)
    return APIResponse.success(
        data=[r.model_dump() for r in records],
        message="Disease records fetched successfully"
    )


@router.put("/record/{record_id}", response_model=APIResponse)
async def update_record(
    record_id: str,
    data: DiseaseRecordUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a disease record."""
    # To verify ownership, we need the record's crop_id
    repo = DiseaseRepository(db)
    record = await repo.get_by_id(record_id)
    if not record:
        raise NotFoundException("DiseaseRecord", record_id)

    await verify_crop_ownership(db, current_user.id, record.crop_id)

    service = DiseaseService(db)
    updated_record = await service.update_record(current_user.id, record_id, data)
    return APIResponse.success(
        data=updated_record.model_dump(),
        message="Disease record updated successfully"
    )


@router.get("/info/{disease_name}", response_model=APIResponse)
async def get_disease_info(
    disease_name: str,
    db: AsyncSession = Depends(get_db),
):
    """Get disease info from KB (Public)."""
    service = DiseaseService(db)
    info = await service.get_disease_info(disease_name)
    return APIResponse.success(data=info)

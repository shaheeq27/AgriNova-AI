import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.database import Base
from app.models.knowledge import DiseaseLibrary
from app.services.disease_service import DiseaseService
from app.schemas.disease import ImageAnalysisResponse
from app.services.disease_detection.schemas import DiseaseDetectionResult, DiseasePrediction, EngineMetadata
from app.services.disease_detection.exceptions import ImageProcessingError, EngineInferenceError

@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    Session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

    async with Session() as session:
        # Populate KB
        kb1 = DiseaseLibrary(
            disease_name="Early Blight",
            affected_crops="Tomato, Potato",
            symptoms="Spots on leaves",
            treatment="Fungicide X",
            prevention="Crop rotation",
            severity="high"
        )
        kb2 = DiseaseLibrary(
            disease_name="Late Blight",
            affected_crops="Potato, Tomato",
            symptoms="Water-soaked spots",
            treatment="Fungicide Y",
            prevention="Ensure ventilation",
            severity="critical"
        )
        kb3 = DiseaseLibrary(
            disease_name="Bacterial Spot",
            affected_crops="Tomato, Chili",
            symptoms="Black spots",
            treatment="Copper spray",
            prevention="Clean seeds",
            severity="medium"
        )
        session.add_all([kb1, kb2, kb3])
        await session.commit()

    async with Session() as session:
        yield session

@pytest.fixture
def service(db):
    return DiseaseService(db)

def mock_prediction_result(crop, disease, is_healthy=False):
    return DiseaseDetectionResult(
        predictions=[
            DiseasePrediction(crop=crop, disease=disease, probability=0.95, is_healthy=is_healthy)
        ],
        inference_time_ms=10.0,
        metadata=EngineMetadata()
    )

@pytest.mark.asyncio
async def test_mapping_tomato_early_blight(service):
    # Tomato + Early Blight -> matches shared KB record
    mock_engine = MagicMock()
    mock_engine.predict.return_value = mock_prediction_result("Tomato", "Early Blight")

    with patch('app.services.disease_service.DiseaseDetectionEngine', return_value=mock_engine):
        result = await service.analyze_image(b"bytes")

    assert result.model_prediction.predicted_crop == "Tomato"
    assert result.knowledge_base_evidence.disease_name == "Early Blight"
    assert result.knowledge_base_evidence.severity == "high"

@pytest.mark.asyncio
async def test_mapping_potato_early_blight(service):
    # Potato + Early Blight -> matches same shared KB record
    mock_engine = MagicMock()
    mock_engine.predict.return_value = mock_prediction_result("Potato", "Early Blight")

    with patch('app.services.disease_service.DiseaseDetectionEngine', return_value=mock_engine):
        result = await service.analyze_image(b"bytes")

    assert result.model_prediction.predicted_crop == "Potato"
    assert result.knowledge_base_evidence.disease_name == "Early Blight"

@pytest.mark.asyncio
async def test_mapping_tomato_late_blight(service):
    # Tomato + Late Blight -> matches shared KB record
    mock_engine = MagicMock()
    mock_engine.predict.return_value = mock_prediction_result("Tomato", "Late Blight")

    with patch('app.services.disease_service.DiseaseDetectionEngine', return_value=mock_engine):
        result = await service.analyze_image(b"bytes")

    assert result.model_prediction.predicted_crop == "Tomato"
    assert result.knowledge_base_evidence.disease_name == "Late Blight"
    assert result.knowledge_base_evidence.severity == "critical"

@pytest.mark.asyncio
async def test_mapping_no_kb_match(service):
    # e.g., Maize + Early Blight (not in affected_crops)
    mock_engine = MagicMock()
    mock_engine.predict.return_value = mock_prediction_result("Maize", "Early Blight")

    with patch('app.services.disease_service.DiseaseDetectionEngine', return_value=mock_engine):
        result = await service.analyze_image(b"bytes")

    assert result.model_prediction.predicted_crop == "Maize"
    assert result.knowledge_base_evidence is None

@pytest.mark.asyncio
async def test_mapping_healthy(service):
    mock_engine = MagicMock()
    mock_engine.predict.return_value = mock_prediction_result("Tomato", "Healthy", is_healthy=True)

    with patch('app.services.disease_service.DiseaseDetectionEngine', return_value=mock_engine):
        result = await service.analyze_image(b"bytes")

    assert result.model_prediction.is_healthy is True
    assert result.knowledge_base_evidence is None

@pytest.mark.asyncio
async def test_analyze_image_processing_failure(service):
    mock_engine = MagicMock()
    mock_engine.predict.side_effect = ImageProcessingError("Corrupt image")

    with patch('app.services.disease_service.DiseaseDetectionEngine', return_value=mock_engine):
        with pytest.raises(Exception) as exc:
            await service.analyze_image(b"bytes")
        assert "Corrupt image" in str(exc.value)
        # Verify custom error type mapping in service layer (e.g. 400 for image processing)
        assert getattr(exc.value, 'status_code', None) == 400

@pytest.mark.asyncio
async def test_analyze_image_model_failure(service):
    mock_engine = MagicMock()
    mock_engine.predict.side_effect = EngineInferenceError("OOM")

    with patch('app.services.disease_service.DiseaseDetectionEngine', return_value=mock_engine):
        with pytest.raises(Exception) as exc:
            await service.analyze_image(b"bytes")
        assert "OOM" in str(exc.value)
        assert getattr(exc.value, 'status_code', None) == 500

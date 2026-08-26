import pytest
from unittest.mock import AsyncMock

from app.ai.schemas.historical_analysis import HistoricalInsightsContext, CropPerformanceInsight
from app.services.fertilizer_engine import FertilizerEngine
from app.services.irrigation_engine import IrrigationEngine
from app.services.disease_service import DiseaseService
from app.services.crop_recommendation_service import recommend_crops

# Mock AsyncSession
class MockSession:
    async def execute(self, *args, **kwargs):
        class MockResult:
            def scalar_one_or_none(self):
                return None
            def scalars(self):
                class MockScalars:
                    def all(self):
                        return []
                return MockScalars()
        return MockResult()


@pytest.fixture
def mock_db():
    return MockSession()


@pytest.fixture
def sample_insights():
    return HistoricalInsightsContext(
        crop_performance=[
            CropPerformanceInsight(
                crop_name="Wheat", variety="A", seasons_observed=["Rabi"],
                crops_observed=1, harvested_count=1, average_yield=100.0,
                yield_unit="kg", best_yield=100.0, worst_yield=100.0,
                disease_records=0, fertilizer_applications=0, irrigation_applications=0,
                confidence=0.5
            )
        ]
    )

@pytest.mark.asyncio
async def test_fertilizer_engine_accepts_insights(mock_db, sample_insights):
    engine = FertilizerEngine()
    
    # 1. Existing caller with None
    res1 = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=None)
    
    # 2. Caller with populated insights
    res2 = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=sample_insights)
    
    # 3. Exactly same behavior
    assert res1 == res2
    assert res1["fertilizer_type"] == "NPK 19:19:19"


@pytest.mark.asyncio
async def test_irrigation_engine_accepts_insights(mock_db, sample_insights):
    engine = IrrigationEngine()
    weather = {"rainfall": 0.0, "temperature": 25.0, "humidity": 50.0}
    
    res1 = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", current_weather=weather, historical_insights=None)
    res2 = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", current_weather=weather, historical_insights=sample_insights)
    
    assert res1 == res2
    assert res1["water_requirement_mm"] == 20.0


@pytest.mark.asyncio
async def test_disease_service_accepts_insights(mock_db, sample_insights):
    service = DiseaseService(mock_db)
    
    res1 = await service.detect_from_symptoms("Wheat", ["yellow leaves"], historical_insights=None)
    res2 = await service.detect_from_symptoms("Wheat", ["yellow leaves"], historical_insights=sample_insights)
    
    assert res1 == res2
    assert isinstance(res1, list)


@pytest.mark.asyncio
async def test_crop_recommendation_accepts_insights(mock_db, sample_insights, monkeypatch):
    import app.services.crop_recommendation_service as crs
    
    monkeypatch.setattr(crs, "_load_model", lambda: None)
    
    res1 = await recommend_crops(mock_db, 25.0, 50.0, 100.0, "Loam", historical_insights=None)
    res2 = await recommend_crops(mock_db, 25.0, 50.0, 100.0, "Loam", historical_insights=sample_insights)
    
    assert res1 == res2
    assert isinstance(res1, list)

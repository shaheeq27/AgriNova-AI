import pytest
from unittest.mock import AsyncMock
from app.services.crop_recommendation.orchestrator import RecommendationOrchestrator
from app.services.crop_recommendation.context import RecommendationContext
from app.models.knowledge import CropProfile

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_orchestrator(mock_db):
    orchestrator = RecommendationOrchestrator(mock_db)
    mock_crops = [
        CropProfile(crop_name="Cotton", temp_min=20, temp_max=35, rain_min=500, rain_max=1000, humidity_min=50, humidity_max=80, ideal_soil_types="Black", growing_season="All"),
    ]
    orchestrator.candidate_generator.get_candidates = AsyncMock(return_value=mock_crops)

    # Mock Water requirements
    async def mock_execute(*args, **kwargs):
        class MockResult:
            def all(self):
                class Row:
                    def __init__(self, c, w):
                        self.crop_name = c
                        self.total_water = w
                return [Row("Cotton", 700)]
        return MockResult()
    mock_db.execute = mock_execute

    return orchestrator

@pytest.mark.asyncio
async def test_a_soil_only(mock_orchestrator):
    ctx = RecommendationContext(soil_type="Black", temperature=None, humidity=None, rainfall=None)
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    scores = await mock_orchestrator.scorer.score_candidates(candidates, ctx)
    base_score, evidence, expl, pos, neg = scores["Cotton"]
    assert base_score == 1.0
    assert evidence == 0.25
    assert "Temperature, Humidity and Rainfall were unavailable" in expl

@pytest.mark.asyncio
async def test_b_temperature_soil_only(mock_orchestrator):
    ctx = RecommendationContext(soil_type="Black", temperature=25.0, humidity=None, rainfall=None)
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    scores = await mock_orchestrator.scorer.score_candidates(candidates, ctx)
    base_score, evidence, expl, pos, neg = scores["Cotton"]
    assert base_score == 1.0
    assert evidence == 0.50
    assert "Humidity and Rainfall were unavailable" in expl

@pytest.mark.asyncio
async def test_c_rainfall_soil_temp(mock_orchestrator):
    ctx = RecommendationContext(soil_type="Black", temperature=25.0, humidity=None, rainfall=700.0)
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    scores = await mock_orchestrator.scorer.score_candidates(candidates, ctx)
    base_score, evidence, expl, pos, neg = scores["Cotton"]
    assert base_score == 1.0
    assert evidence == 0.75
    assert "Humidity was unavailable" in expl

@pytest.mark.asyncio
async def test_d_all_weather_available(mock_orchestrator):
    ctx = RecommendationContext(soil_type="Black", temperature=25.0, humidity=60.0, rainfall=700.0)
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    scores = await mock_orchestrator.scorer.score_candidates(candidates, ctx)
    base_score, evidence, expl, pos, neg = scores["Cotton"]
    assert base_score == 1.0
    assert evidence == 1.0
    assert "unavailable" not in expl

@pytest.mark.asyncio
async def test_e_poor_rainfall(mock_orchestrator):
    # rainfall=100 is far from Cotton's min of 500, distance=400, penalty > 1.0 -> rain score=0.0
    ctx = RecommendationContext(soil_type="Black", temperature=25.0, humidity=None, rainfall=100.0)
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    scores = await mock_orchestrator.scorer.score_candidates(candidates, ctx)
    base_score, evidence, expl, pos, neg = scores["Cotton"]
    # 3 factors evaluated: soil(1), temp(1), rain(0) -> sum=2. 2/3 = 0.6667
    assert base_score == 0.6667
    assert evidence == 0.75
    assert "Humidity was unavailable" in expl

@pytest.mark.asyncio
async def test_f_no_weather_available(mock_orchestrator):
    ctx = RecommendationContext(soil_type="Black", temperature=None, humidity=None, rainfall=None)
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    scores = await mock_orchestrator.scorer.score_candidates(candidates, ctx)
    base_score, evidence, expl, pos, neg = scores["Cotton"]
    assert base_score == 1.0
    assert evidence == 0.25
    assert "Temperature, Humidity and Rainfall were unavailable" in expl

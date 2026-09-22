from app.schemas.crop_v6_domain import EvidenceStrength
import pytest
from unittest.mock import AsyncMock
from app.schemas.crop_v6 import CropRecommendationRequestV6
from app.services.crop_recommendation.orchestrator import RecommendationOrchestrator
from app.services.crop_recommendation.context import RecommendationContext
from app.models.knowledge import CropProfile, IrrigationGuideline
from app.ai.schemas.historical_analysis import (
    HistoricalInsightsContext,
    CropPerformanceInsight,
    YieldTrendInsight,
    DiseasePatternInsight
)

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_orchestrator(mock_db):
    orchestrator = RecommendationOrchestrator(mock_db)

    # Setup candidate generator with a subset of crops
    mock_crops = [
        CropProfile(crop_name="Cotton", temp_min=20, temp_max=35, rain_min=500, rain_max=1000, humidity_min=50, humidity_max=80, ideal_soil_types="Black", growing_season="Kharif"),
        CropProfile(crop_name="Wheat", temp_min=10, temp_max=25, rain_min=200, rain_max=500, humidity_min=40, humidity_max=70, ideal_soil_types="Alluvial, Loamy", growing_season="Rabi"),
        CropProfile(crop_name="Rice", temp_min=20, temp_max=35, rain_min=1000, rain_max=2000, humidity_min=60, humidity_max=80, ideal_soil_types="Clay", growing_season="Kharif"),
        CropProfile(crop_name="Tomato", temp_min=15, temp_max=30, rain_min=400, rain_max=800, humidity_min=50, humidity_max=70, ideal_soil_types="Loamy, Sandy", growing_season="All"),
    ]
    orchestrator.candidate_generator.get_candidates = AsyncMock(return_value=mock_crops)

    # Mock Water requirements so WaterAdjuster works
    async def mock_execute(*args, **kwargs):
        class MockResult:
            def all(self):
                class Row:
                    def __init__(self, c, w):
                        self.crop_name = c
                        self.total_water = w
                return [Row("Rice", 1200), Row("Cotton", 700), Row("Wheat", 400), Row("Tomato", 600)]
        return MockResult()

    mock_db.execute = mock_execute

    return orchestrator

@pytest.mark.asyncio
async def test_scenario_1_hyderabad_black_kharif_borewell(mock_orchestrator):
    # Hyderabad + Black soil + Kharif + Borewell
    # Temp ~ 30, Rain ~ 600
    ctx = RecommendationContext(
        soil_type="Black", season="Kharif", water_source="borewell",
        temperature=30.0, humidity=65.0, rainfall=600.0
    )
    # Orchestrator doesn't take ctx directly for testing, we can simulate the scorer pipeline
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    trackers = [AdjustmentTracker(crop=c, base_score=1.0) for c in candidates]
    mock_orchestrator.season_filter.apply(trackers, ctx)
    filtered = [t.crop for t in trackers if not t.is_filtered]
    assert any(c.crop_name == "Cotton" for c in filtered)

    scores = await mock_orchestrator.scorer.score_candidates(filtered, ctx)
    # Cotton should have perfect soil, temp, rain -> score 1.0
    assert scores["Cotton"][0] == 1.0

@pytest.mark.asyncio
async def test_scenario_10_rainfed_insufficient_rainfall(mock_orchestrator):
    # Rainfed + crop requiring 1200mm (Rice)
    ctx = RecommendationContext(soil_type="Clay", water_source="rainfed", rainfall=100.0)
    candidates = await mock_orchestrator.candidate_generator.get_candidates()

    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    trackers = [AdjustmentTracker(crop=c, base_score=1.0) for c in candidates]

    await mock_orchestrator.water_adjuster.apply(trackers, ctx)

    # Rice requires 1200mm, threshold is 500mm for filter
    rice_tracker = next(t for t in trackers if t.crop.crop_name == "Rice")
    rice_tracker.crop.water_requirement_mm = 1200
    await mock_orchestrator.water_adjuster.apply(trackers, ctx)
    assert rice_tracker.is_filtered is True
    assert len(rice_tracker.eligibility_constraints) > 0

@pytest.mark.asyncio
async def test_scenario_11_previous_crop_same_family(mock_orchestrator):
    ctx = RecommendationContext(soil_type="Loamy", previous_crop="Tomato", previous_crop_family="Solanaceae")
    # We add Potato to candidates
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    candidates.append(CropProfile(crop_name="Potato", ideal_soil_types="Loamy", growing_season="All", botanical_family="Solanaceae"))

    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    trackers = [AdjustmentTracker(crop=c, base_score=1.0) for c in candidates]

    mock_orchestrator.rotation_adjuster.apply(trackers, ctx)
    potato_tracker = next(t for t in trackers if t.crop.crop_name == "Potato")
    from app.schemas.crop_v6_domain import RiskLevel
    assert potato_tracker.biological_risks[0].level == RiskLevel.MEDIUM

@pytest.mark.asyncio
async def test_scenario_15_farm_with_strong_history(mock_orchestrator):
    # Farm with strong yield trend for Cotton
    performance = HistoricalInsightsContext(
        crop_performance=[CropPerformanceInsight(crop_name="Cotton", crops_observed=3, harvested_count=3)],
        yield_trends=[YieldTrendInsight(crop_name="Cotton", yield_unit="kg/ha", trend_direction="increasing", confidence=0.8)]
    )
    ctx = RecommendationContext(soil_type="Black", farm_performance=performance)

    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    tracker = AdjustmentTracker(crop=candidates[0], base_score=0.8) # Cotton

    mock_orchestrator.performance_adjuster.apply([tracker], ctx)

    assert tracker.historical_evidence.level == EvidenceStrength.STRONG


@pytest.mark.asyncio
async def test_scenario_2_delhi_alluvial_rabi_irrigated(mock_orchestrator):
    ctx = RecommendationContext(
        soil_type="Alluvial", season="Rabi", water_source="canal",
        temperature=15.0, humidity=50.0, rainfall=50.0
    )
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    trackers = [AdjustmentTracker(crop=c, base_score=1.0) for c in candidates]
    mock_orchestrator.season_filter.apply(trackers, ctx)
    filtered = [t.crop for t in trackers if not t.is_filtered]
    assert any(c.crop_name == "Wheat" for c in filtered)

    scores = await mock_orchestrator.scorer.score_candidates(filtered, ctx)
    assert scores["Wheat"][0] >= 0.75

@pytest.mark.asyncio
async def test_scenario_4_unknown_location_no_weather(mock_orchestrator):
    ctx = RecommendationContext(soil_type="Alluvial")
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    scores = await mock_orchestrator.scorer.score_candidates(candidates, ctx)
    assert scores["Wheat"][0] == 1.0 # 1/1 criteria met (soil only)
    assert scores["Cotton"][0] == 0.0 # 0/1 criteria met

@pytest.mark.asyncio
async def test_scenario_5_missing_humidity(mock_orchestrator):
    ctx = RecommendationContext(
        soil_type="Black", temperature=25.0, rainfall=600.0, humidity=None
    )
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    scores = await mock_orchestrator.scorer.score_candidates(candidates, ctx)
    # Cotton hits temp, rain, soil -> 3/3 -> 1.0
    assert scores["Cotton"][0] == 1.0

@pytest.mark.asyncio
async def test_scenario_8_unknown_soil(mock_orchestrator):
    ctx = RecommendationContext(
        soil_type="MarsDust", temperature=25.0, rainfall=600.0, humidity=60.0
    )
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    scores = await mock_orchestrator.scorer.score_candidates(candidates, ctx)
    # Cotton hits temp, rain, hum -> 3/4 -> 0.75
    assert scores["Cotton"][0] == 0.75
    assert "MarsDust" in scores["Cotton"][4][0] # in negative factors (index 4 in 5-tuple)

@pytest.mark.asyncio
async def test_scenario_12_previous_crop_unmapped(mock_orchestrator):
    ctx = RecommendationContext(soil_type="Loamy", previous_crop="Dragonfruit")
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    trackers = [AdjustmentTracker(crop=c, base_score=1.0) for c in candidates]
    mock_orchestrator.rotation_adjuster.apply(trackers, ctx)
    # No penalty because Dragonfruit is unmapped and not in candidates
    assert all(len(t.biological_risks) == 0 for t in trackers)

@pytest.mark.asyncio
async def test_scenario_13_disease_history(mock_orchestrator):
    ctx = RecommendationContext(
        soil_type="Loamy",
        disease_history=[DiseasePatternInsight(disease_name="Blight", affected_crop="Tomato", occurrence_count=2, common_severity="critical")]
    )
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    trackers = [AdjustmentTracker(crop=c, base_score=1.0) for c in candidates]
    mock_orchestrator.disease_adjuster.apply(trackers, ctx)

    tomato_tracker = next(t for t in trackers if t.crop.crop_name == "Tomato")
    from app.schemas.crop_v6_domain import RiskLevel
    assert tomato_tracker.biological_risks[0].level == RiskLevel.HIGH
    assert tomato_tracker.biological_risks[0].level.value == "high"

@pytest.mark.asyncio
async def test_scenario_16_farm_insufficient_history(mock_orchestrator):
    performance = HistoricalInsightsContext(
        crop_performance=[CropPerformanceInsight(crop_name="Cotton", crops_observed=1, harvested_count=1)],
        yield_trends=[]
    )
    ctx = RecommendationContext(soil_type="Loamy", farm_performance=performance)
    candidates = await mock_orchestrator.candidate_generator.get_candidates()
    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    trackers = [AdjustmentTracker(crop=c, base_score=1.0) for c in candidates]
    mock_orchestrator.performance_adjuster.apply(trackers, ctx)

    cotton_tracker = next(t for t in trackers if t.crop.crop_name == "Cotton")
    # Need at least 2 observations for historical success to apply
    assert len(cotton_tracker.biological_risks) == 0

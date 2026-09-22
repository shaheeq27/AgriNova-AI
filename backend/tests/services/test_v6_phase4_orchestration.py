import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.models.user import User
from app.schemas.crop_v6 import CropRecommendationRequestV6
from app.services.crop_recommendation.orchestrator import RecommendationOrchestrator
from app.services.crop_recommendation.context import RecommendationContext
from app.models.knowledge import CropProfile
from app.ai.schemas.historical_analysis import HistoricalInsightsContext, DiseasePatternInsight
from app.core.exceptions import ForbiddenException

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.fixture
def mock_user():
    user = User(id="user-123", email="test@example.com")
    return user

@pytest.fixture
def orchestrator(mock_db):
    o = RecommendationOrchestrator(mock_db)

    # Mock candidate generation
    o.candidate_generator = AsyncMock()
    o.candidate_generator.get_candidates.return_value = [
        CropProfile(crop_name="Wheat", temp_min=10, temp_max=30, rain_min=20, rain_max=100, humidity_min=40, humidity_max=70, ideal_soil_types="Loamy"),
        CropProfile(crop_name="Rice", temp_min=20, temp_max=40, rain_min=100, rain_max=200, humidity_min=60, humidity_max=90, ideal_soil_types="Clay")
    ]

    # Adjusters
    o.water_adjuster = AsyncMock()
    o.water_adjuster.apply = AsyncMock()

    return o

@pytest.mark.asyncio
async def test_orchestrator_anonymous_recommendation(orchestrator):
    # No farm_id, purely environmental
    req = CropRecommendationRequestV6(
        soil_type="Loamy",
        temperature=25.0,
        humidity=60.0,
        rainfall=50.0
    )

    resp = await orchestrator.recommend(req, user=None)

    assert len(resp.recommendations) > 0
    assert resp.input_conditions_used["soil_type"] == "Loamy"
    assert resp.input_conditions_used["temperature_source"] == "explicit"
    assert resp.input_conditions_used["water_source"] is None
    assert "previous_crop" not in resp.input_conditions_used

    # Highest score should be Wheat (matches Loamy and 50mm rain better)
    assert resp.recommendations[0].crop_name == "Wheat"

@pytest.mark.asyncio
async def test_orchestrator_missing_weather_defaults(orchestrator):
    # We should NOT fabricate weather defaults. They should remain None if unavailable.
    req = CropRecommendationRequestV6(soil_type="Loamy")
    resp = await orchestrator.recommend(req, user=None)

    assert resp.input_conditions_used["temperature"] is None
    assert resp.input_conditions_used["temperature_source"] == "unavailable"
    assert resp.input_conditions_used["rainfall"] is None
    assert resp.input_conditions_used["humidity_source"] == "unavailable"

@pytest.mark.asyncio
@patch("app.services.crop_recommendation.orchestrator.FarmService")
@patch("app.services.crop_recommendation.orchestrator.HistoricalInsightsService")
@patch("app.services.crop_recommendation.orchestrator.HistoryRepository")
async def test_orchestrator_farm_context(MockHistRepo, MockInsightsSvc, MockFarmSvc, orchestrator, mock_user):
    # Mock Farm Service
    mock_farm_svc = AsyncMock()
    mock_farm = MagicMock()
    mock_farm.water_source = "Canal"
    mock_farm.latitude = None
    mock_farm_svc.get_farm.return_value = mock_farm
    MockFarmSvc.return_value = mock_farm_svc

    # Mock Insights Service
    mock_insights_svc = AsyncMock()
    mock_insights_svc.compute_insights_context.return_value = HistoricalInsightsContext(
        disease_patterns=[DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat", occurrence_count=2, common_severity="critical")]
    )
    MockInsightsSvc.return_value = mock_insights_svc

    # Mock History Repo
    mock_hist_repo = AsyncMock()
    mock_prev_crop = MagicMock()
    mock_prev_crop.crop_name = "Wheat"
    mock_hist_repo.get_crop_history.return_value = [mock_prev_crop]
    MockHistRepo.return_value = mock_hist_repo

    req = CropRecommendationRequestV6(
        farm_id="farm-123",
        soil_type="Loamy",
        temperature=25.0,
        humidity=60.0,
        rainfall=50.0
    )

    # Needs real adjusters to test end-to-end adjustment
    orchestrator.disease_adjuster = __import__("app.services.crop_recommendation.adjusters.disease_history", fromlist=[""]).DiseaseHistoryAdjuster()
    orchestrator.rotation_adjuster = __import__("app.services.crop_recommendation.adjusters.crop_rotation", fromlist=[""]).CropRotationAdjuster()

    resp = await orchestrator.recommend(req, user=mock_user)

    assert resp.input_conditions_used["water_source"] == "Canal"
    assert resp.input_conditions_used["previous_crop"] == "Wheat"

    wheat_rec = next((r for r in resp.recommendations if r.crop_name == "Wheat"), None)
    assert wheat_rec is not None
    # Wheat was previous crop -> penalty 0.85
    # Wheat has disease pattern -> penalty 0.80
    # Final score should be heavily penalized compared to base
    assert len(wheat_rec.biological_risks) > 0
    assert any("Repeated" in str(r.factors) for r in wheat_rec.biological_risks)

@pytest.mark.asyncio
async def test_orchestrator_unauthorized_farm(orchestrator):
    req = CropRecommendationRequestV6(farm_id="farm-123", soil_type="Loamy")
    # No user provided, should raise ValueError
    with pytest.raises(ValueError, match="Must be logged in to use farm context"):
        await orchestrator.recommend(req, user=None)

@pytest.mark.asyncio
@patch("app.services.crop_recommendation.orchestrator.FarmService")
async def test_orchestrator_cross_user_farm_security(MockFarmSvc, orchestrator, mock_user):
    # Test for cross-user authorization block
    mock_farm_svc = AsyncMock()
    mock_farm_svc.get_farm.side_effect = ForbiddenException("You do not have access to this farm")
    MockFarmSvc.return_value = mock_farm_svc

    req = CropRecommendationRequestV6(farm_id="other-users-farm-123", soil_type="Loamy")

    with pytest.raises(ForbiddenException):
        await orchestrator.recommend(req, user=mock_user)

@pytest.mark.asyncio
async def test_orchestrator_no_candidates(orchestrator):
    orchestrator.candidate_generator.get_candidates.return_value = []

    req = CropRecommendationRequestV6(soil_type="Loamy")
    resp = await orchestrator.recommend(req, user=None)

    assert len(resp.recommendations) == 0

@pytest.mark.asyncio
async def test_orchestrator_all_filtered_by_season(orchestrator):
    # Setup candidate, but we will mock season filter

    def mock_apply(trackers, ctx):
        for t in trackers:
            t.apply_filter("test mock")
    orchestrator.season_filter.apply = MagicMock(side_effect=mock_apply)


    req = CropRecommendationRequestV6(soil_type="Loamy", season="Winter")
    resp = await orchestrator.recommend(req, user=None)

    assert len(resp.recommendations) == 0

@pytest.mark.asyncio
@patch("app.services.crop_recommendation.orchestrator.FarmService")
@patch("app.services.crop_recommendation.orchestrator.HistoricalInsightsService")
@patch("app.services.crop_recommendation.orchestrator.HistoryRepository")
async def test_orchestrator_water_source_distinctions(MockHistRepo, MockInsightsSvc, MockFarmSvc, orchestrator, mock_user):
    # missing water source
    mock_farm_svc = AsyncMock()
    mock_farm = MagicMock()
    mock_farm.water_source = None
    mock_farm.latitude = None
    mock_farm_svc.get_farm.return_value = mock_farm
    MockFarmSvc.return_value = mock_farm_svc

    mock_insights_svc = AsyncMock()
    mock_insights_svc.compute_insights_context.return_value = None
    MockInsightsSvc.return_value = mock_insights_svc

    mock_hist_repo = AsyncMock()
    mock_hist_repo.get_crop_history.return_value = []
    MockHistRepo.return_value = mock_hist_repo

    # 1. water_source = None (unavailable)
    req = CropRecommendationRequestV6(farm_id="farm-123", soil_type="Loamy")
    resp = await orchestrator.recommend(req, user=mock_user)
    assert resp.input_conditions_used["water_source"] is None

    # 2. water_source = "none"
    mock_farm.water_source = "none"
    resp = await orchestrator.recommend(req, user=mock_user)
    assert resp.input_conditions_used["water_source"] == "none"

    # 3. water_source = "rainfed"
    mock_farm.water_source = "rainfed"
    resp = await orchestrator.recommend(req, user=mock_user)
    assert resp.input_conditions_used["water_source"] == "rainfed"

    # 4. irrigated source
    mock_farm.water_source = "canal"
    resp = await orchestrator.recommend(req, user=mock_user)
    assert resp.input_conditions_used["water_source"] == "canal"

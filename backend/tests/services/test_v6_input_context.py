import pytest
from unittest.mock import patch, AsyncMock
from app.schemas.crop_v6 import CropRecommendationRequestV6
from app.services.crop_recommendation.orchestrator import RecommendationOrchestrator
from app.services.crop_recommendation.context import RecommendationContext

@pytest.fixture
def mock_db():
    return AsyncMock()

@pytest.mark.asyncio
async def test_v6_orchestrator_location_no_weather_fallback(mock_db):
    """
    Test that if WeatherService fails (e.g. unknown location or API timeout),
    the flow continues gracefully without fabricating weather.
    """
    request = CropRecommendationRequestV6(
        soil_type="Clay",
        location_name="Unknown City",
        season="Kharif"
    )

    orchestrator = RecommendationOrchestrator(mock_db)

    # Mock CandidateGenerator to return nothing so we don't need real DB
    orchestrator.candidate_generator.get_candidates = AsyncMock(return_value=[])

    with patch('app.services.weather_service.WeatherService._fetch_weather_data', new_callable=AsyncMock) as mock_fetch:
        # Simulate API failure returning empty dict (which gets translated to None for temp/rainfall)
        mock_fetch.return_value = {}

        response = await orchestrator.recommend(request)

        # Verify it didn't fabricate defaults
        assert response.input_conditions_used["temperature"] is None
        assert response.input_conditions_used["rainfall"] is None
        assert response.input_conditions_used["temperature_source"] == "unavailable"

@pytest.mark.asyncio
async def test_v6_orchestrator_season_normalization(mock_db):
    """
    Test that 'zaid' and 'annual' are normalized properly by the SeasonFilter.
    """
    request = CropRecommendationRequestV6(
        soil_type="Loamy",
        season="zaid" # The UI sends "zaid"
    )

    orchestrator = RecommendationOrchestrator(mock_db)

    from app.models.knowledge import CropProfile
    # Mock candidate generator to return a summer crop and an all-season crop
    mock_summer_crop = CropProfile(crop_name="SummerCrop", growing_season="summer")
    mock_all_crop = CropProfile(crop_name="AllCrop", growing_season="all")
    mock_rabi_crop = CropProfile(crop_name="RabiCrop", growing_season="rabi")

    candidates = [mock_summer_crop, mock_all_crop, mock_rabi_crop]

    # Build context
    ctx = RecommendationContext(soil_type="Loamy", season="zaid")

    # Test season filter
    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    trackers = [AdjustmentTracker(crop=c, base_score=1.0) for c in candidates]
    orchestrator.season_filter.apply(trackers, ctx)
    filtered = [t.crop for t in trackers if not t.is_filtered]

    assert len(filtered) == 2
    assert filtered[0].crop_name == "SummerCrop"
    assert filtered[1].crop_name == "AllCrop"

@pytest.mark.asyncio
async def test_v6_orchestrator_water_constraint_missing_irrigation(mock_db):
    """
    Test that if water_source is not explicitly 'none' or 'rainfed',
    it assumes irrigated and doesn't penalize.
    """
    orchestrator = RecommendationOrchestrator(mock_db)

    from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
    from app.models.knowledge import CropProfile

    # Mock a crop
    crop = CropProfile(crop_name="Rice")
    tracker = AdjustmentTracker(crop=crop, base_score=1.0)

    # Context with 'borewell' (irrigated)
    ctx1 = RecommendationContext(soil_type="Clay", water_source="borewell")
    await orchestrator.water_adjuster.apply([tracker], ctx1)

    # Tracker should be untouched because it's not rainfed
    assert tracker.is_filtered is False
    assert len(tracker.eligibility_constraints) == 0

@pytest.mark.asyncio
async def test_v6_orchestrator_farm_auth_missing_user(mock_db):
    """
    Test that providing farm_id without a logged-in user raises an error.
    """
    request = CropRecommendationRequestV6(
        soil_type="Clay",
        farm_id="farm_123"
    )

    orchestrator = RecommendationOrchestrator(mock_db)

    with pytest.raises(ValueError, match="Must be logged in to use farm context"):
        await orchestrator.recommend(request, user=None)

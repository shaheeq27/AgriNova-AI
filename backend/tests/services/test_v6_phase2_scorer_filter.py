import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models.knowledge import CropProfile
from app.models.weather import WeatherRecord
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.candidate_generator import CandidateGenerator
from app.services.crop_recommendation.scorers.rule_scorer import RuleBasedScorer
from app.services.crop_recommendation.filters.season_filter import SeasonFilter

@pytest.fixture
def mock_profiles():
    return [
        CropProfile(
            crop_name="Wheat",
            temp_min=15.0, temp_max=25.0,
            humidity_min=50.0, humidity_max=70.0,
            rain_min=300.0, rain_max=500.0,
            ideal_soil_types="Loamy, Clay",
            growing_season="Rabi"
        ),
        CropProfile(
            crop_name="Rice",
            temp_min=20.0, temp_max=35.0,
            humidity_min=60.0, humidity_max=80.0,
            rain_min=1000.0, rain_max=1500.0,
            ideal_soil_types="Clay",
            growing_season="Kharif"
        ),
        CropProfile(
            crop_name="Tomato",
            temp_min=18.0, temp_max=28.0,
            humidity_min=40.0, humidity_max=60.0,
            rain_min=400.0, rain_max=600.0,
            ideal_soil_types="Sandy, Loamy",
            growing_season="All"
        )
    ]

@pytest.mark.asyncio
async def test_candidate_generation(mock_profiles):
    # Setup mock db
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = mock_profiles
    mock_db.execute.return_value = mock_result
    
    generator = CandidateGenerator(mock_db)
    candidates = await generator.get_candidates()
    
    assert len(candidates) == 3
    assert candidates[0].crop_name == "Wheat"
    assert candidates[1].crop_name == "Rice"

@pytest.mark.asyncio
async def test_rule_scorer_perfect_match(mock_profiles):
    context = RecommendationContext(
        soil_type="Clay",
        temperature=28.0,
        humidity=70.0,
        rainfall=1200.0
    )
    scorer = RuleBasedScorer()
    scores = await scorer.score_candidates(mock_profiles, context)
    
    # Rice should be perfect
    assert scores["Rice"] == 1.0
    # Wheat should be penalized
    assert scores["Wheat"] < 1.0

@pytest.mark.asyncio
async def test_rule_scorer_partial_match(mock_profiles):
    context = RecommendationContext(
        soil_type="Loamy",
        temperature=27.0, # Outside Wheat (max 25), dist = 2. penalty = 2/10 = 0.2
        humidity=60.0,    # Perfect for Wheat
        rainfall=400.0    # Perfect for Wheat
    )
    scorer = RuleBasedScorer()
    scores = await scorer.score_candidates(mock_profiles, context)
    
    wheat_score = scores["Wheat"]
    # Temp=0.8, Hum=1.0, Rain=1.0, Soil=1.0 -> 3.8/4 = 0.95
    assert wheat_score == 0.95
    
@pytest.mark.asyncio
async def test_rule_scorer_soil_mismatch(mock_profiles):
    context = RecommendationContext(
        soil_type="Sandy",
        temperature=28.0, # Tomato perfect
        humidity=50.0,    # Tomato perfect
        rainfall=500.0    # Tomato perfect
    )
    scorer = RuleBasedScorer()
    scores = await scorer.score_candidates(mock_profiles, context)
    
    # Tomato has Sandy
    assert scores["Tomato"] == 1.0
    # Rice does not have Sandy
    assert scores["Rice"] < 1.0 # Rice misses soil, temp (within range -> 1), rain misses heavily

@pytest.mark.asyncio
async def test_rule_scorer_missing_weather(mock_profiles):
    # Only soil type is provided
    context = RecommendationContext(soil_type="Clay")
    scorer = RuleBasedScorer()
    scores = await scorer.score_candidates(mock_profiles, context)
    
    # Score should only be based on soil.
    # Rice has Clay -> 1.0/1.0 = 1.0
    # Wheat has Clay -> 1.0/1.0 = 1.0
    # Tomato does not have Clay -> 0.0/1.0 = 0.0
    assert scores["Rice"] == 1.0
    assert scores["Tomato"] == 0.0

@pytest.mark.asyncio
async def test_rule_scorer_current_weather_fallback(mock_profiles):
    weather = WeatherRecord(temp_avg=28.0, humidity=70.0, rainfall=1200.0)
    context = RecommendationContext(soil_type="Clay", current_weather=weather)
    scorer = RuleBasedScorer()
    scores = await scorer.score_candidates(mock_profiles, context)
    
    assert scores["Rice"] == 1.0

def test_season_filter_matching(mock_profiles):
    filter_obj = SeasonFilter()
    
    # Rabi target
    context = RecommendationContext(soil_type="Clay", season="Rabi")
    filtered = filter_obj.filter_candidates(mock_profiles, context)
    names = [p.crop_name for p in filtered]
    
    assert "Wheat" in names
    assert "Tomato" in names # "All" is always kept
    assert "Rice" not in names # Kharif is excluded

def test_season_filter_no_target(mock_profiles):
    filter_obj = SeasonFilter()
    context = RecommendationContext(soil_type="Clay")
    filtered = filter_obj.filter_candidates(mock_profiles, context)
    
    assert len(filtered) == 3

def test_season_filter_case_insensitive(mock_profiles):
    filter_obj = SeasonFilter()
    context = RecommendationContext(soil_type="Clay", season=" kharif ")
    filtered = filter_obj.filter_candidates(mock_profiles, context)
    names = [p.crop_name for p in filtered]
    
    assert "Rice" in names
    assert "Tomato" in names
    assert "Wheat" not in names

@pytest.mark.asyncio
async def test_rule_scorer_score_bounds(mock_profiles):
    # Extreme weather to test clamp to [0, 1]
    context = RecommendationContext(
        soil_type="Clay",
        temperature=100.0, # distance=75 for wheat, penalty=7.5 -> clamp to 0
        humidity=150.0,
        rainfall=5000.0
    )
    scorer = RuleBasedScorer()
    scores = await scorer.score_candidates(mock_profiles, context)
    
    for crop, score in scores.items():
        assert 0.0 <= score <= 1.0

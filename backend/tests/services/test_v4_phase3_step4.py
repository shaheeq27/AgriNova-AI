import pytest
from app.services.disease_service import DiseaseService
from app.services.crop_recommendation_service import recommend_crops
from app.ai.schemas.historical_analysis import HistoricalInsightsContext, DiseasePatternInsight, YieldTrendInsight
from app.schemas.disease import DiseaseMatch
import app.services.crop_recommendation_service as crs

class MockSession:
    async def execute(self, *args, **kwargs):
        class MockResult:
            def scalar_one_or_none(self):
                return None
            def scalars(self):
                class MockScalars:
                    def all(self):
                        class MockLib:
                            disease_name = "Rust"
                            affected_crops = "Wheat"
                            symptoms = "yellow spots,brown spots"
                            treatment = "Fungicide"
                            prevention = "Spacing"
                            severity = "High"
                        
                        class MockProfile:
                            crop_name = "Wheat"
                            temp_min = 10
                            temp_max = 25
                            humidity_min = 40
                            humidity_max = 60
                            rain_min = 200
                            rain_max = 500
                            ideal_soil_types = "Loam"
                            
                        # Differentiate by checking if the query is for CropProfile
                        # But wait, we can't easily tell. Let's just return a class that acts as both.
                        class MockHybrid:
                            disease_name = "Rust"
                            affected_crops = "Wheat"
                            symptoms = "yellow spots,brown spots"
                            treatment = "Fungicide"
                            prevention = "Spacing"
                            severity = "High"
                            
                            crop_name = "Wheat"
                            temp_min = 10
                            temp_max = 25
                            humidity_min = 40
                            humidity_max = 60
                            rain_min = 200
                            rain_max = 500
                            ideal_soil_types = "Loam"
                            
                        return [MockHybrid()]
                return MockScalars()
        return MockResult()

class MockRepo:
    pass

@pytest.fixture
def mock_db(monkeypatch):
    monkeypatch.setattr(crs, "_load_model", lambda: None)
    return MockSession()

@pytest.mark.asyncio
async def test_1_historical_insights_none(mock_db):
    # Disease
    ds = DiseaseService(mock_db)
    symptoms = ["yellow spots"]
    matches = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=None)
    assert matches[0].disease_name == "Rust"
    assert matches[0].historically_adjusted is False
    
    # Crop
    crops = await recommend_crops(mock_db, 20.0, 50.0, 300.0, "Loam", top_k=1, historical_insights=None)
    assert crops[0]["crop_name"] == "Wheat"
    assert crops[0]["historically_adjusted"] is False

@pytest.mark.asyncio
async def test_2_insufficient_confidence(mock_db):
    ds = DiseaseService(mock_db)
    symptoms = ["yellow spots"]
    
    insights = HistoricalInsightsContext(
        disease_patterns=[
            DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat", occurrence_count=5, confidence=0.2)
        ]
    )
    
    matches = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=insights)
    assert matches[0].historically_adjusted is False

@pytest.mark.asyncio
async def test_3_relevant_crop_history(mock_db):
    insights = HistoricalInsightsContext(
        yield_trends=[
            YieldTrendInsight(crop_name="Wheat", yield_unit="kg", trend_direction="increasing", confidence=0.8)
        ]
    )
    
    crops = await recommend_crops(mock_db, 20.0, 50.0, 300.0, "Loam", top_k=1, historical_insights=insights)
    assert crops[0]["historically_adjusted"] is True
    assert "increased by 5%" in crops[0]["personalization_rationale"]

@pytest.mark.asyncio
async def test_4_relevant_disease_history(mock_db):
    ds = DiseaseService(mock_db)
    symptoms = ["yellow spots"]
    
    insights = HistoricalInsightsContext(
        disease_patterns=[
            DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat", occurrence_count=2, confidence=0.8)
        ]
    )
    
    matches = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=insights)
    assert matches[0].historically_adjusted is True
    assert "increased by 5%" in matches[0].personalization_rationale

@pytest.mark.asyncio
async def test_5_different_histories(mock_db):
    ds = DiseaseService(mock_db)
    symptoms = ["yellow spots"]
    
    history_A = HistoricalInsightsContext(
        disease_patterns=[DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat", occurrence_count=1, confidence=0.9)]
    )
    history_B = HistoricalInsightsContext(
        disease_patterns=[DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat", occurrence_count=5, confidence=0.9)]
    )
    
    match_A = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=history_A)
    match_B = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=history_B)
    
    assert match_A[0].confidence < match_B[0].confidence

@pytest.mark.asyncio
async def test_6_maximum_adjustment_boundary(mock_db):
    ds = DiseaseService(mock_db)
    symptoms = ["yellow spots"]
    
    insights = HistoricalInsightsContext(
        disease_patterns=[
            DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat", occurrence_count=100, confidence=1.0)
        ]
    )
    
    match_no_history = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=None)
    match_with_history = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=insights)
    
    # Difference should be capped at 5% (0.05)
    diff = match_with_history[0].confidence - match_no_history[0].confidence
    assert round(diff, 3) == 0.05
    assert "increased by 5%" in match_with_history[0].personalization_rationale

@pytest.mark.asyncio
async def test_7_determinism(mock_db):
    ds = DiseaseService(mock_db)
    symptoms = ["yellow spots"]
    insights = HistoricalInsightsContext(
        disease_patterns=[DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat", occurrence_count=2, confidence=0.9)]
    )
    
    res1 = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=insights)
    res2 = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=insights)
    
    assert res1[0].confidence == res2[0].confidence

@pytest.mark.asyncio
async def test_8_unrelated_crop_history(mock_db):
    ds = DiseaseService(mock_db)
    symptoms = ["yellow spots"]
    
    insights = HistoricalInsightsContext(
        disease_patterns=[
            DiseasePatternInsight(disease_name="Rust", affected_crop="Rice", occurrence_count=5, confidence=0.9)
        ]
    )
    
    # Querying for Wheat, but history is for Rice
    matches = await ds.detect_from_symptoms("Wheat", symptoms, historical_insights=insights)
    
    assert matches[0].historically_adjusted is False

import pytest
from app.services.fertilizer_engine import FertilizerEngine
from app.services.irrigation_engine import IrrigationEngine
from app.ai.schemas.historical_analysis import HistoricalInsightsContext, InputUsageInsight

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

@pytest.mark.asyncio
async def test_1_historical_insights_none(mock_db):
    engine = FertilizerEngine()
    result = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=None)
    
    assert result["quantity_per_acre"] == 50.0
    assert result.get("historically_adjusted") is False
    assert result.get("personalization_rationale") is None

@pytest.mark.asyncio
async def test_2_insufficient_confidence(mock_db):
    engine = FertilizerEngine()
    
    insights = HistoricalInsightsContext(
        input_usage=[
            InputUsageInsight(
                input_type="fertilizer",
                crop_name="Wheat",
                application_count=5,
                confidence=0.2
            )
        ]
    )
    
    result = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=insights)
    
    assert result["quantity_per_acre"] == 50.0
    assert result.get("historically_adjusted") is False

@pytest.mark.asyncio
async def test_3_relevant_fertilizer_history(mock_db):
    engine = FertilizerEngine()
    
    insights = HistoricalInsightsContext(
        input_usage=[
            InputUsageInsight(
                input_type="fertilizer",
                crop_name="Wheat",
                application_count=3,
                confidence=0.8
            )
        ]
    )
    
    result = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=insights)
    
    assert result["quantity_per_acre"] == 47.5
    assert result.get("historically_adjusted") is True
    assert "reduced by 5%" in result.get("personalization_rationale")

@pytest.mark.asyncio
async def test_4_relevant_irrigation_history(mock_db):
    engine = IrrigationEngine()
    
    insights = HistoricalInsightsContext(
        input_usage=[
            InputUsageInsight(
                input_type="irrigation",
                crop_name="Wheat",
                application_count=5,
                confidence=0.9
            )
        ]
    )
    
    result = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", current_weather=None, historical_insights=insights)
    
    assert result["water_requirement_mm"] == 19.0
    assert result.get("historically_adjusted") is True

@pytest.mark.asyncio
async def test_5_different_histories(mock_db):
    engine = FertilizerEngine()
    
    history_A = HistoricalInsightsContext(
        input_usage=[InputUsageInsight(input_type="fertilizer", crop_name="Wheat", application_count=1, confidence=0.9)]
    )
    history_B = HistoricalInsightsContext(
        input_usage=[InputUsageInsight(input_type="fertilizer", crop_name="Wheat", application_count=5, confidence=0.9)]
    )
    
    res_A = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=history_A)
    res_B = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=history_B)
    
    assert res_A["quantity_per_acre"] == 50.0
    assert res_B["quantity_per_acre"] == 45.0
    assert res_A != res_B

@pytest.mark.asyncio
async def test_6_maximum_adjustment_boundary(mock_db):
    engine = FertilizerEngine()
    
    insights = HistoricalInsightsContext(
        input_usage=[
            InputUsageInsight(
                input_type="fertilizer",
                crop_name="Wheat",
                application_count=100,
                confidence=1.0
            )
        ]
    )
    
    result = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=insights)
    
    assert result["quantity_per_acre"] == 45.0
    assert "reduced by 10%" in result.get("personalization_rationale")

@pytest.mark.asyncio
async def test_7_determinism(mock_db):
    engine = FertilizerEngine()
    insights = HistoricalInsightsContext(
        input_usage=[InputUsageInsight(input_type="fertilizer", crop_name="Wheat", application_count=4, confidence=0.9)]
    )
    
    res1 = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=insights)
    res2 = await engine.get_recommendation(mock_db, "Wheat", "Vegetative", "Loam", historical_insights=insights)
    
    assert res1 == res2

@pytest.mark.asyncio
async def test_8_unrelated_crop_history(mock_db):
    engine = FertilizerEngine()
    
    insights = HistoricalInsightsContext(
        input_usage=[
            InputUsageInsight(
                input_type="fertilizer",
                crop_name="Wheat",
                application_count=5,
                confidence=0.9
            )
        ]
    )
    
    result = await engine.get_recommendation(mock_db, "Rice", "Vegetative", "Loam", historical_insights=insights)
    
    assert result["quantity_per_acre"] == 50.0
    assert result.get("historically_adjusted") is False

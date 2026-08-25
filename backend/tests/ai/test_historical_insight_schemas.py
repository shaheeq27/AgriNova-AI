import pytest
from pydantic import ValidationError
from app.ai.schemas.historical_analysis import (
    CropPerformanceInsight,
    SeasonalPerformanceInsight,
    DiseasePatternInsight,
    InputUsageInsight,
    YieldTrendInsight,
    HistoricalInsightsContext
)

def test_crop_performance_insight_complete():
    insight = CropPerformanceInsight(
        crop_name="Wheat",
        variety="Sharbati",
        seasons_observed=["Rabi"],
        crops_observed=3,
        harvested_count=3,
        average_yield=200.0,
        yield_unit="kg",
        best_yield=250.0,
        worst_yield=150.0,
        disease_records=2,
        fertilizer_applications=4,
        irrigation_applications=6,
        confidence=0.9
    )
    assert insight.crop_name == "Wheat"
    assert insight.average_yield == 200.0
    assert insight.confidence == 0.9

def test_optional_fields():
    insight = CropPerformanceInsight(crop_name="Rice")
    assert insight.variety is None
    assert insight.average_yield is None
    assert insight.confidence is None
    assert insight.crops_observed == 0

def test_confidence_validation_rejects_below_zero():
    with pytest.raises(ValidationError) as exc:
        CropPerformanceInsight(crop_name="Rice", confidence=-0.1)
    assert "Input should be greater than or equal to 0" in str(exc.value)

def test_confidence_validation_rejects_above_one():
    with pytest.raises(ValidationError) as exc:
        CropPerformanceInsight(crop_name="Rice", confidence=1.1)
    assert "Input should be less than or equal to 1" in str(exc.value)

def test_seasonal_performance_insight():
    insight = SeasonalPerformanceInsight(season="Kharif", harvested_crops=5, average_yield=100.5, yield_unit="kg")
    assert insight.season == "Kharif"
    assert insight.average_yield == 100.5

def test_disease_pattern_insight():
    insight = DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat", occurrence_count=2, resolved_count=2)
    assert insight.disease_name == "Rust"
    assert insight.resolved_count == 2

def test_input_usage_insight():
    insight = InputUsageInsight(input_type="Fertilizer", crop_name="Wheat", total_quantity=150.0, quantity_unit="kg")
    assert insight.total_quantity == 150.0

def test_yield_trend_insight():
    insight = YieldTrendInsight(crop_name="Wheat", yield_unit="kg", trend_direction="increasing", highest_yield=250.0)
    assert insight.trend_direction == "increasing"

def test_mixed_yield_units_remain_separate():
    ctx = HistoricalInsightsContext(
        crop_performance=[
            CropPerformanceInsight(crop_name="Wheat", average_yield=200.0, yield_unit="kg"),
            CropPerformanceInsight(crop_name="Wheat", average_yield=1.5, yield_unit="tons")
        ]
    )
    assert ctx.crop_performance[0].yield_unit == "kg"
    assert ctx.crop_performance[1].yield_unit == "tons"

def test_historical_insights_context_multiple():
    ctx = HistoricalInsightsContext(
        crop_performance=[CropPerformanceInsight(crop_name="Wheat")],
        seasonal_performance=[SeasonalPerformanceInsight(season="Kharif")],
        disease_patterns=[DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat")],
        input_usage=[InputUsageInsight(input_type="Water", crop_name="Wheat")],
        yield_trends=[YieldTrendInsight(crop_name="Wheat", yield_unit="kg")]
    )
    assert len(ctx.crop_performance) == 1
    assert len(ctx.seasonal_performance) == 1

def test_empty_historical_insights_context_safe():
    ctx = HistoricalInsightsContext()
    assert ctx.crop_performance == []
    assert ctx.seasonal_performance == []
    assert ctx.disease_patterns == []
    assert ctx.input_usage == []
    assert ctx.yield_trends == []

def test_model_dump_serialization():
    ctx = HistoricalInsightsContext(
        crop_performance=[CropPerformanceInsight(crop_name="Wheat", yield_unit="kg")]
    )
    dumped = ctx.model_dump()
    assert dumped["crop_performance"][0]["crop_name"] == "Wheat"
    assert dumped["crop_performance"][0]["variety"] is None


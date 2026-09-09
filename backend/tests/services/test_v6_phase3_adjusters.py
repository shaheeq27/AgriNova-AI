import pytest
from unittest.mock import AsyncMock, MagicMock
from app.models.knowledge import CropProfile
from app.schemas.crop_v6 import ExplanationPayload
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.services.crop_recommendation.adjusters.water_constraint import WaterConstraintAdjuster
from app.services.crop_recommendation.adjusters.crop_rotation import CropRotationAdjuster
from app.services.crop_recommendation.adjusters.disease_history import DiseaseHistoryAdjuster
from app.services.crop_recommendation.adjusters.historical_performance import HistoricalPerformanceAdjuster
from app.ai.schemas.historical_analysis import (
    HistoricalInsightsContext,
    DiseasePatternInsight,
    YieldTrendInsight,
    CropPerformanceInsight
)

@pytest.fixture
def base_tracker():
    crop = CropProfile(crop_name="Wheat", ideal_soil_types="Loamy")
    return AdjustmentTracker(crop=crop, base_score=0.80, current_score=0.80)

def test_tracker_logic():
    crop = CropProfile(crop_name="Test")
    t = AdjustmentTracker(crop=crop, base_score=0.8, current_score=0.8)
    
    t.apply_multiplier(1.1, "Bonus")
    assert t.current_score == 0.88
    assert "Bonus" in t.positive_factors
    
    t.apply_multiplier(0.5, "Penalty")
    assert t.current_score == 0.44
    assert "Penalty" in t.negative_factors
    
    t.apply_filter("Too hot")
    assert t.current_score == 0.0
    assert t.is_filtered is True
    assert "Too hot" in t.constraints_applied
    
    # Should not apply multiplier if filtered
    t.apply_multiplier(10.0, "Doesn't matter")
    assert t.current_score == 0.0

@pytest.mark.asyncio
async def test_water_adjuster_rainfed_high(base_tracker):
    # Setup mock db
    mock_db = AsyncMock()
    mock_result = MagicMock()
    # Mock row returned by DB
    mock_row = MagicMock()
    mock_row.crop_name = "Wheat"
    mock_row.total_water = 600.0 # > 500
    mock_result.all.return_value = [mock_row]
    mock_db.execute.return_value = mock_result
    
    ctx = RecommendationContext(soil_type="Loamy", water_source="Rainfed")
    adj = WaterConstraintAdjuster(mock_db)
    
    await adj.apply([base_tracker], ctx)
    assert base_tracker.is_filtered is True
    assert base_tracker.current_score == 0.0

@pytest.mark.asyncio
async def test_water_adjuster_rainfed_medium(base_tracker):
    mock_db = AsyncMock()
    mock_result = MagicMock()
    mock_row = MagicMock()
    mock_row.crop_name = "Wheat"
    mock_row.total_water = 400.0 # > 300, < 500
    mock_result.all.return_value = [mock_row]
    mock_db.execute.return_value = mock_result
    
    ctx = RecommendationContext(soil_type="Loamy", water_source="Rainfed")
    adj = WaterConstraintAdjuster(mock_db)
    
    await adj.apply([base_tracker], ctx)
    assert base_tracker.is_filtered is False
    assert base_tracker.current_score == 0.64 # 0.80 * 0.80

@pytest.mark.asyncio
async def test_water_adjuster_irrigated(base_tracker):
    mock_db = AsyncMock()
    ctx = RecommendationContext(soil_type="Loamy", water_source="Canal")
    adj = WaterConstraintAdjuster(mock_db)
    
    await adj.apply([base_tracker], ctx)
    assert base_tracker.current_score == 0.80
    assert mock_db.execute.called is False

def test_rotation_adjuster():
    t_wheat = AdjustmentTracker(crop=CropProfile(crop_name="Wheat"), base_score=0.8, current_score=0.8)
    
    # Same crop
    ctx1 = RecommendationContext(soil_type="Loamy", previous_crop="Wheat")
    adj = CropRotationAdjuster()
    adj.apply([t_wheat], ctx1)
    assert t_wheat.current_score == 0.68 # 0.8 * 0.85
    
    # Same family (Wheat and Rice are Poaceae)
    t_rice = AdjustmentTracker(crop=CropProfile(crop_name="Rice"), base_score=0.8, current_score=0.8)
    ctx2 = RecommendationContext(soil_type="Loamy", previous_crop="Wheat", previous_crop_family="Poaceae")
    adj.apply([t_rice], ctx2)
    assert t_rice.current_score == 0.72 # 0.8 * 0.90
    
    # Beneficial (Wheat after Legume like Soybean)
    t_wheat2 = AdjustmentTracker(crop=CropProfile(crop_name="Wheat"), base_score=0.8, current_score=0.8)
    ctx3 = RecommendationContext(soil_type="Loamy", previous_crop="Soybean")
    adj.apply([t_wheat2], ctx3)
    assert t_wheat2.current_score == 0.88 # 0.8 * 1.10

def test_disease_adjuster():
    t_wheat = AdjustmentTracker(crop=CropProfile(crop_name="Wheat"), base_score=0.8, current_score=0.8)
    
    disease_insight = DiseasePatternInsight(
        disease_name="Leaf Blight",
        affected_crop="Wheat",
        occurrence_count=2,
        common_severity="critical"
    )
    
    ctx = RecommendationContext(
        soil_type="Loamy",
        disease_history=[disease_insight]
    )
    
    adj = DiseaseHistoryAdjuster()
    adj.apply([t_wheat], ctx)
    
    assert t_wheat.current_score == 0.64 # 0.8 * 0.80

def test_disease_adjuster_stacking():
    t_wheat = AdjustmentTracker(crop=CropProfile(crop_name="Wheat"), base_score=0.8, current_score=0.8)
    
    insight1 = DiseasePatternInsight(
        disease_name="Leaf Blight",
        affected_crop="Wheat",
        occurrence_count=2,
        common_severity="critical"
    )
    
    insight2 = DiseasePatternInsight(
        disease_name="Rust",
        affected_crop="Wheat",
        occurrence_count=2,
        common_severity="high"
    )
    
    ctx = RecommendationContext(
        soil_type="Loamy",
        disease_history=[insight1, insight2]
    )
    
    adj = DiseaseHistoryAdjuster()
    adj.apply([t_wheat], ctx)
    
    # 0.8 * 0.80 (critical) = 0.64
    # 0.64 * 0.90 (high) = 0.576
    assert t_wheat.current_score == 0.576

def test_historical_performance_adjuster():
    t_wheat = AdjustmentTracker(crop=CropProfile(crop_name="Wheat"), base_score=0.8, current_score=0.8)
    
    trend = YieldTrendInsight(
        crop_name="Wheat",
        yield_unit="kg",
        trend_direction="increasing",
        confidence=0.8
    )
    
    perf = CropPerformanceInsight(
        crop_name="Wheat",
        crops_observed=3,
        harvested_count=3
    )
    
    ctx = RecommendationContext(
        soil_type="Loamy",
        farm_performance=HistoricalInsightsContext(
            yield_trends=[trend],
            crop_performance=[perf],
        )
    )
    
    adj = HistoricalPerformanceAdjuster()
    adj.apply([t_wheat], ctx)
    
    # 0.8 * 1.08 = 0.864 -> 0.864 * 1.05 = 0.9072
    assert t_wheat.current_score == 0.9072

def test_historical_performance_variety_aggregation():
    t_wheat = AdjustmentTracker(crop=CropProfile(crop_name="Wheat"), base_score=0.8, current_score=0.8)
    
    # Variety 1: 1 observation, 1 harvest
    perf1 = CropPerformanceInsight(
        crop_name="Wheat",
        variety="V1",
        crops_observed=1,
        harvested_count=1
    )
    
    # Variety 2: 1 observation, 1 harvest
    perf2 = CropPerformanceInsight(
        crop_name="Wheat",
        variety="V2",
        crops_observed=1,
        harvested_count=1
    )
    
    # Aggregated: 2 observations, 2 harvests -> success rate 1.0, count >= 2 -> bonus should apply!
    
    ctx = RecommendationContext(
        soil_type="Loamy",
        farm_performance=HistoricalInsightsContext(
            crop_performance=[perf1, perf2],
        )
    )
    
    adj = HistoricalPerformanceAdjuster()
    adj.apply([t_wheat], ctx)
    
    # 0.8 * 1.05 = 0.84
    assert t_wheat.current_score == 0.84

def test_rotation_unmapped_family():
    # If previous crop is unmapped (e.g. unknown family), same-crop penalty still works
    t_unknown = AdjustmentTracker(crop=CropProfile(crop_name="UnknownCrop"), base_score=0.8, current_score=0.8)
    t_wheat = AdjustmentTracker(crop=CropProfile(crop_name="Wheat"), base_score=0.8, current_score=0.8)
    
    ctx = RecommendationContext(soil_type="Loamy", previous_crop="UnknownCrop")
    
    adj = CropRotationAdjuster()
    adj.apply([t_unknown, t_wheat], ctx)
    
    # Same crop penalized
    assert t_unknown.current_score == 0.68  # 0.8 * 0.85
    # Wheat unchanged
    assert t_wheat.current_score == 0.8

def test_tracker_small_delta():
    t = AdjustmentTracker(crop=CropProfile(crop_name="Wheat"), base_score=0.10, current_score=0.10)
    # A 2% bonus at base score 0.10 yields a delta of 0.002
    t.apply_multiplier(1.02, "Small Bonus")
    
    # Still recorded in positive factors
    assert "Small Bonus" in t.positive_factors
    assert t.current_score == 0.102

@pytest.mark.asyncio
async def test_water_adjuster_soil_filtering():
    mock_db = AsyncMock()
    mock_result = MagicMock()
    # Assume the query is executed correctly; we just verify the call arguments.
    mock_result.all.return_value = []
    mock_db.execute.return_value = mock_result
    
    ctx = RecommendationContext(soil_type="Sandy", water_source="Rainfed")
    adj = WaterConstraintAdjuster(mock_db)
    
    tracker = AdjustmentTracker(crop=CropProfile(crop_name="Wheat"), base_score=0.8, current_score=0.8)
    await adj.apply([tracker], ctx)
    
    # Get the statement passed to db.execute
    stmt = mock_db.execute.call_args[0][0]
    stmt_str = str(stmt.compile(compile_kwargs={"literal_binds": True}))
    
    # Verify the compiled statement includes the soil_type filter
    assert "kb_irrigation_guidelines.soil_type = 'Sandy'" in stmt_str


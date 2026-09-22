import pytest
from app.models.knowledge import CropProfile
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.services.crop_recommendation.adjusters.historical_performance import HistoricalPerformanceAdjuster
from app.services.crop_recommendation.context import RecommendationContext
from app.schemas.crop_v6_domain import EvidenceStrength
from app.ai.schemas.historical_analysis import HistoricalInsightsContext
from app.ai.schemas.historical_analysis import CropPerformanceInsight

def get_tracker(name: str) -> AdjustmentTracker:
    return AdjustmentTracker(crop=CropProfile(crop_name=name), base_score=0.8)

@pytest.mark.asyncio
async def test_historical_performance_adjuster_strong():
    adj = HistoricalPerformanceAdjuster()
    # Mock some context
    ctx = RecommendationContext(
        soil_type="Loamy",
        farm_performance=HistoricalInsightsContext(
            crop_performance=[
                CropPerformanceInsight(crop_name="Wheat", crops_observed=3, harvested_count=3, total_yield_kg=1000)
            ],
            seasonal_performance=[],
            disease_patterns=[],
            input_usage=[],
            yield_trends=[]
        )
    )
    t = get_tracker("Wheat")
    adj.apply([t], ctx)
    assert t.historical_evidence.level == EvidenceStrength.STRONG

@pytest.mark.asyncio
async def test_historical_performance_adjuster_none():
    adj = HistoricalPerformanceAdjuster()
    ctx = RecommendationContext(
        soil_type="Loamy",
        farm_performance=HistoricalInsightsContext(
            crop_performance=[
                CropPerformanceInsight(crop_name="Wheat", crops_observed=3, harvested_count=1, total_yield_kg=100) # poor
            ],
            seasonal_performance=[],
            disease_patterns=[],
            input_usage=[],
            yield_trends=[]
        )
    )
    t = get_tracker("Wheat")
    adj.apply([t], ctx)
    assert t.historical_evidence.level == EvidenceStrength.NONE

@pytest.mark.asyncio
async def test_historical_performance_variety_aggregation():
    adj = HistoricalPerformanceAdjuster()
    ctx = RecommendationContext(
        soil_type="Loamy",
        farm_performance=HistoricalInsightsContext(
            crop_performance=[
                CropPerformanceInsight(crop_name="wheat", crops_observed=2, harvested_count=2, total_yield_kg=1000),
                CropPerformanceInsight(crop_name="WHEAT", crops_observed=1, harvested_count=1, total_yield_kg=500)
            ],
            seasonal_performance=[],
            disease_patterns=[],
            input_usage=[],
            yield_trends=[]
        )
    )
    t = get_tracker("Wheat")
    adj.apply([t], ctx)
    assert t.historical_evidence.observations == 3
    assert t.historical_evidence.successful_observations == 3

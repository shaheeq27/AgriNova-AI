import pytest
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.models.knowledge import CropProfile
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.filters.season_filter import SeasonFilter
from app.services.crop_recommendation.adjusters.water_constraint import WaterConstraintAdjuster
from app.services.crop_recommendation.adjusters.crop_rotation import CropRotationAdjuster
from app.services.crop_recommendation.adjusters.disease_history import DiseaseHistoryAdjuster
from app.schemas.crop_v6_domain import EligibilityStatus, RiskLevel
from app.ai.schemas.historical_analysis import DiseasePatternInsight
import asyncio

def make_tracker(crop_name: str, family: str = None, season: str = "All", water_req: float = None):
    crop = CropProfile(
        crop_name=crop_name,
        botanical_family=family,
        growing_season=season,
        water_requirement_mm=water_req
    )
    return AdjustmentTracker(crop=crop, base_score=1.0)

def test_season_eligibility():
    filter_adj = SeasonFilter()
    context = RecommendationContext(soil_type="Loamy", season="Summer")

    t_match = make_tracker("CropA", season="Summer")
    t_all = make_tracker("CropB", season="All")
    t_mismatch = make_tracker("CropC", season="Winter")

    trackers = [t_match, t_all, t_mismatch]
    filter_adj.apply(trackers, context)

    assert trackers[0].eligibility_constraints[-1].status == EligibilityStatus.ELIGIBLE
    assert not trackers[0].is_filtered

    assert trackers[1].eligibility_constraints[-1].status == EligibilityStatus.ELIGIBLE
    assert not trackers[1].is_filtered

    assert trackers[2].eligibility_constraints[-1].status == EligibilityStatus.INELIGIBLE
    assert trackers[2].is_filtered

@pytest.mark.asyncio
async def test_water_constraint_adjuster():
    adj = WaterConstraintAdjuster(db=None) # DB not used anymore

    # 1. Unavailable water data -> No constraints
    ctx1 = RecommendationContext(soil_type="Loamy", water_source=None, rainfall=100)
    t1 = [make_tracker("A", water_req=200)]
    await adj.apply(t1, ctx1)
    assert not t1[0].eligibility_constraints
    assert not t1[0].is_filtered

    # 2. Known irrigation -> No rainfed constraint
    ctx2 = RecommendationContext(soil_type="Loamy", water_source="canal", rainfall=100)
    t2 = [make_tracker("B", water_req=200)]
    await adj.apply(t2, ctx2)
    assert not t2[0].eligibility_constraints

    # 3. Unknown water source -> No invented meaning
    ctx3 = RecommendationContext(soil_type="Loamy", water_source="magic_pond", rainfall=100)
    t3 = [make_tracker("C", water_req=200)]
    await adj.apply(t3, ctx3)
    assert not t3[0].eligibility_constraints

    # 4. Rainfed behavior
    ctx4 = RecommendationContext(soil_type="Loamy", water_source="rainfed", rainfall=150)
    t_ok = make_tracker("D", water_req=100)
    t_fail = make_tracker("E", water_req=200)
    t_none = make_tracker("F", water_req=None)

    t4 = [t_ok, t_fail, t_none]
    await adj.apply(t4, ctx4)

    assert t_ok.eligibility_constraints[-1].status == EligibilityStatus.ELIGIBLE
    assert not t_ok.is_filtered

    assert t_fail.eligibility_constraints[-1].status == EligibilityStatus.INELIGIBLE
    assert t_fail.is_filtered

    assert not t_none.eligibility_constraints
    assert not t_none.is_filtered

def test_crop_rotation_adjuster():
    adj = CropRotationAdjuster()

    ctx = RecommendationContext(
        soil_type="Loamy",
        previous_crop="Wheat",
        previous_crop_family="Poaceae"
    )

    # Same crop
    t_same_crop = make_tracker("Wheat", family="Poaceae")
    # Same family
    t_same_family = make_tracker("Maize", family="Poaceae")
    # Beneficial
    t_cereal = make_tracker("Wheat", family="Poaceae")
    ctx_beneficial = RecommendationContext(soil_type="Loamy", previous_crop="Soybean", previous_crop_family="Leguminosae")

    # Unknown family
    t_unknown = make_tracker("MysteryCrop", family=None)

    adj.apply([t_same_crop, t_same_family, t_unknown], ctx)

    assert len(t_same_crop.biological_risks) == 1
    assert t_same_crop.biological_risks[0].level == RiskLevel.HIGH

    assert len(t_same_family.biological_risks) == 1
    assert t_same_family.biological_risks[0].level == RiskLevel.MEDIUM

    assert len(t_unknown.biological_risks) == 0

    # Beneficial
    adj.apply([t_cereal], ctx_beneficial)
    assert len(t_cereal.biological_risks) == 0
    assert any("Beneficial rotation" in f for f in t_cereal.positive_factors)

def test_disease_history_adjuster():
    adj = DiseaseHistoryAdjuster()

    insight1 = DiseasePatternInsight(disease_name="Blight", affected_crop="Potato", occurrence_count=2, common_severity="high")
    insight2 = DiseasePatternInsight(disease_name="Rust", affected_crop="Wheat", occurrence_count=2, common_severity="critical")

    ctx = RecommendationContext(
        soil_type="Loamy",
        disease_history=[insight1, insight2]
    )

    t_exact = make_tracker("Wheat", family="Poaceae")
    t_family_match = make_tracker("Tomato", family="Solanaceae")
    t_potato = make_tracker("Potato", family="Solanaceae")
    t_no_family = make_tracker("Mystery", family=None)

    trackers = [t_exact, t_family_match, t_potato, t_no_family]
    adj.apply(trackers, ctx)

    # Exact match for Wheat -> Critical -> High risk
    assert len(t_exact.biological_risks) == 1
    assert t_exact.biological_risks[0].level == RiskLevel.HIGH

    # Same family for Tomato (Solanaceae, matches Potato) -> No risk
    assert len(t_family_match.biological_risks) == 0

    # Exact match for Potato -> High severity -> Medium risk
    assert len(t_potato.biological_risks) == 1
    assert t_potato.biological_risks[0].level == RiskLevel.MEDIUM

    # Unknown family -> No risk
    assert len(t_no_family.biological_risks) == 0

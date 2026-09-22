import pytest
from app.services.crop_recommendation.ranker import RecommendationRanker
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.models.knowledge import CropProfile
from app.schemas.crop_v6_domain import RiskLevel, BiologicalRisk, EvidenceStrength, HistoricalEvidence, HardConstraint, EligibilityStatus

def make_tracker(name: str, base_score: float, is_filtered: bool = False, risk_level: RiskLevel = None, evidence_level: EvidenceStrength = None) -> AdjustmentTracker:
    t = AdjustmentTracker(crop=CropProfile(crop_name=name), base_score=base_score)
    t.is_filtered = is_filtered
    if risk_level:
        t.biological_risks.append(BiologicalRisk(level=risk_level))
    if evidence_level:
        t.historical_evidence = HistoricalEvidence(level=evidence_level)
    return t

def test_ranker_ineligible_excluded():
    t1 = make_tracker("Wheat", 0.9, is_filtered=True)
    t2 = make_tracker("Rice", 0.8)

    ranked = RecommendationRanker.rank([t1, t2])
    assert len(ranked) == 1
    assert ranked[0].crop.crop_name == "Rice"

def test_ranker_agronomic_suitability_wins():
    t1 = make_tracker("Wheat", 0.8)
    t2 = make_tracker("Rice", 0.9) # Higher score

    ranked = RecommendationRanker.rank([t1, t2])
    assert ranked[0].crop.crop_name == "Rice"
    assert ranked[1].crop.crop_name == "Wheat"

def test_ranker_lower_risk_wins_on_tie():
    t1 = make_tracker("Wheat", 0.8, risk_level=RiskLevel.MEDIUM)
    t2 = make_tracker("Rice", 0.8, risk_level=RiskLevel.LOW) # Lower risk

    ranked = RecommendationRanker.rank([t1, t2])
    assert ranked[0].crop.crop_name == "Rice"

def test_ranker_stronger_evidence_wins_on_tie():
    t1 = make_tracker("Wheat", 0.8, evidence_level=EvidenceStrength.LIMITED)
    t2 = make_tracker("Rice", 0.8, evidence_level=EvidenceStrength.STRONG) # Stronger evidence

    ranked = RecommendationRanker.rank([t1, t2])
    assert ranked[0].crop.crop_name == "Rice"

def test_ranker_crop_name_tie_breaker():
    t1 = make_tracker("Zucchini", 0.8)
    t2 = make_tracker("Apple", 0.8)

    ranked = RecommendationRanker.rank([t1, t2])
    assert ranked[0].crop.crop_name == "Apple"
    assert ranked[1].crop.crop_name == "Zucchini"

def test_ranker_mixed_candidates():
    # high suitability + high risk
    t1 = make_tracker("HighRiskWheat", 0.95, risk_level=RiskLevel.HIGH)
    # medium suitability + low risk
    t2 = make_tracker("SafeRice", 0.70, risk_level=RiskLevel.LOW)
    # high suitability + no history (and no risk)
    t3 = make_tracker("NoHistoryCorn", 0.95)

    ranked = RecommendationRanker.rank([t1, t2, t3])
    # 1. NoHistoryCorn (score 0.95, risk 0, evidence 0)
    # 2. HighRiskWheat (score 0.95, risk HIGH(3), evidence 0)
    # 3. SafeRice      (score 0.70, risk LOW(1), evidence 0)
    assert ranked[0].crop.crop_name == "NoHistoryCorn"
    assert ranked[1].crop.crop_name == "HighRiskWheat"
    assert ranked[2].crop.crop_name == "SafeRice"

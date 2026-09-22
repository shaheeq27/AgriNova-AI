import pytest
from pydantic import ValidationError
from app.schemas.crop_v6_domain import (
    AgronomicSuitability,
    BiologicalRisk,
    RiskLevel,
    HistoricalEvidence,
    EvidenceStrength,
    HardConstraint,
    EligibilityStatus
)
from app.models.knowledge import CropProfile

def test_agronomic_suitability_valid():
    suitability = AgronomicSuitability(
        score=0.85,
        evaluated_factors=4,
        expected_factors=4,
        evidence_coverage_ratio=1.0,
        positive_factors=["Good temp"],
        negative_factors=[]
    )
    assert suitability.score == 0.85

def test_agronomic_suitability_invalid_score():
    with pytest.raises(ValidationError):
        AgronomicSuitability(
            score=1.5,  # Invalid: > 1.0
            evaluated_factors=4,
            expected_factors=4,
            evidence_coverage_ratio=1.0
        )

def test_agronomic_suitability_invalid_evidence_coverage():
    with pytest.raises(ValidationError):
        AgronomicSuitability(
            score=0.5,
            evaluated_factors=5,
            expected_factors=4,
            evidence_coverage_ratio=1.25  # Invalid: > 1.0
        )

def test_biological_risk_valid():
    risk = BiologicalRisk(
        level=RiskLevel.MEDIUM,
        factors=["Same family planted previously"],
        source="rotation"
    )
    assert risk.level == "medium"

def test_biological_risk_invalid_level():
    with pytest.raises(ValidationError):
        BiologicalRisk(level="EXTREME", factors=[])

def test_historical_evidence_zero_observations():
    evidence = HistoricalEvidence(
        level=EvidenceStrength.NONE,
        observations=0,
        successful_observations=0,
        trend=None
    )
    assert evidence.level == "none"
    assert evidence.observations == 0

def test_historical_evidence_invalid_observations():
    with pytest.raises(ValidationError):
        HistoricalEvidence(
            level=EvidenceStrength.STRONG,
            observations=-1,
            successful_observations=0
        )

def test_hard_constraint_eligibility():
    constraint = HardConstraint(
        status=EligibilityStatus.INELIGIBLE,
        reason="Requires 500mm water, but farm is rainfed"
    )
    assert constraint.status == "ineligible"

def test_crop_profile_nullable_botanical_fields():
    profile = CropProfile(
        crop_name="TestCrop",
        temp_min=10.0,
        temp_max=30.0,
        rain_min=100.0,
        rain_max=500.0,
        humidity_min=40.0,
        humidity_max=80.0,
        ideal_soil_types="Clay",
        growing_season="Kharif"
    )
    assert profile.botanical_family is None
    assert profile.water_requirement_mm is None

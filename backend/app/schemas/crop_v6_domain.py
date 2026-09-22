from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

class EligibilityStatus(str, Enum):
    ELIGIBLE = "eligible"
    INELIGIBLE = "ineligible"

class HardConstraint(BaseModel):
    status: EligibilityStatus
    reason: Optional[str] = None

class AgronomicSuitability(BaseModel):
    score: float = Field(..., ge=0.0, le=1.0)
    evaluated_factors: int = Field(..., ge=0)
    expected_factors: int = Field(..., gt=0)
    evidence_coverage_ratio: float = Field(..., ge=0.0, le=1.0)
    positive_factors: List[str] = Field(default_factory=list)
    negative_factors: List[str] = Field(default_factory=list)
    unavailable_factors: List[str] = Field(default_factory=list)

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class BiologicalRisk(BaseModel):
    level: RiskLevel
    factors: List[str] = Field(default_factory=list)
    source: str = "agronomic_rules"
    explanation: Optional[str] = None
    is_farm_history_based: bool = False

class EvidenceStrength(str, Enum):
    NONE = "none"
    INSUFFICIENT = "insufficient"
    LIMITED = "limited"
    STRONG = "strong"

class HistoricalEvidence(BaseModel):
    level: EvidenceStrength
    observations: int = Field(0, ge=0)
    successful_observations: int = Field(0, ge=0)
    trend: Optional[str] = None
    supporting_factors: List[str] = Field(default_factory=list)
    explanation: Optional[str] = None

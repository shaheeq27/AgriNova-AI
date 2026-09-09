import pytest
from pydantic import ValidationError
from app.schemas.crop_v6 import (
    CropRecommendationRequestV6,
    CropRecommendationV6,
    CropRecommendationResponseV6,
    ExplanationPayload
)
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.interfaces import RecommendationScorer
from app.models.knowledge import CropProfile

def test_v6_explanation_payload_validation():
    # Valid payload
    payload = ExplanationPayload(
        base_explanation="Good soil.",
        positive_factors=["Loamy soil"],
        negative_factors=[],
        constraints_applied=["Water penalty"]
    )
    assert payload.base_explanation == "Good soil."
    assert payload.positive_factors == ["Loamy soil"]
    assert payload.negative_factors == []
    assert payload.constraints_applied == ["Water penalty"]
    
    # Missing required field
    with pytest.raises(ValidationError):
        ExplanationPayload()

def test_v6_crop_recommendation_validation():
    explanation = ExplanationPayload(
        base_explanation="Good match",
        positive_factors=[],
        negative_factors=[],
        constraints_applied=[]
    )
    
    # Valid
    rec = CropRecommendationV6(
        crop_name="Wheat",
        final_score=0.85,
        base_score=0.75,
        explanation=explanation,
        personalization_applied=True,
        engine_version="v6.3-rules"
    )
    assert rec.crop_name == "Wheat"
    assert rec.final_score == 0.85
    assert rec.personalization_applied is True
    
    # Missing required final_score
    with pytest.raises(ValidationError):
        CropRecommendationV6(
            crop_name="Wheat",
            base_score=0.75,
            explanation=explanation,
            engine_version="v6.3-rules"
        )

def test_v6_recommendation_request_validation():
    # Valid
    req = CropRecommendationRequestV6(soil_type="Clay")
    assert req.soil_type == "Clay"
    assert req.farm_id is None
    
    # Missing required soil_type
    with pytest.raises(ValidationError):
        CropRecommendationRequestV6(farm_id="123")

def test_recommendation_context_optionality():
    # Valid with only required fields
    ctx = RecommendationContext(soil_type="Loamy")
    assert ctx.soil_type == "Loamy"
    assert ctx.farm_id is None
    assert ctx.current_weather is None
    assert ctx.disease_history is None
    
    # Valid with some optional fields
    ctx = RecommendationContext(
        soil_type="Clay",
        farm_id="farm_123",
        previous_crop="Rice",
        previous_crop_family="Poaceae"
    )
    assert ctx.previous_crop == "Rice"

def test_scorer_interface_instantiation():
    # Cannot instantiate abstract class
    with pytest.raises(TypeError):
        RecommendationScorer()

    # Can instantiate implementation
    class MockScorer(RecommendationScorer):
        async def score_candidates(self, candidates, context):
            return {c.crop_name: 0.5 for c in candidates}
            
    scorer = MockScorer()
    assert isinstance(scorer, RecommendationScorer)

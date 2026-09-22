"""
AgriNova AI — V6 Crop Recommendation Orchestrator.
"""

from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.crop_v6 import (
    CropRecommendationRequestV6,
    CropRecommendationV6,
    CropRecommendationResponseV6,
    ExplanationPayload
)
from app.services.farm_service import FarmService
from app.services.weather_service import WeatherService
from app.ai.services.historical_insights_service import HistoricalInsightsService
from app.repositories.history_repo import HistoryRepository

from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.candidate_generator import CandidateGenerator
from app.services.crop_recommendation.filters.season_filter import SeasonFilter
from app.services.crop_recommendation.scorers.rule_scorer import RuleBasedScorer
from app.services.crop_recommendation.adjusters.tracker import AdjustmentTracker
from app.services.crop_recommendation.adjusters.water_constraint import WaterConstraintAdjuster
from app.services.crop_recommendation.adjusters.crop_rotation import CropRotationAdjuster
from app.services.crop_recommendation.adjusters.disease_history import DiseaseHistoryAdjuster
from app.services.crop_recommendation.adjusters.historical_performance import HistoricalPerformanceAdjuster

class RecommendationOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.candidate_generator = CandidateGenerator(db)
        self.season_filter = SeasonFilter()
        self.scorer = RuleBasedScorer()

        # Fixed order of adjusters
        self.water_adjuster = WaterConstraintAdjuster(db)
        self.rotation_adjuster = CropRotationAdjuster()
        self.disease_adjuster = DiseaseHistoryAdjuster()
        self.performance_adjuster = HistoricalPerformanceAdjuster()

    async def recommend(self, request: CropRecommendationRequestV6, user: User | None = None) -> CropRecommendationResponseV6:
        # 1. Resolve Farm Context
        farm = None
        historical_insights = None
        previous_crop = None

        input_conditions_used: dict[str, Any] = {
            "soil_type": request.soil_type,
            "season": request.season,
            "temperature_source": "explicit" if request.temperature is not None else "unavailable",
            "humidity_source": "explicit" if request.humidity is not None else "unavailable",
            "rainfall_source": "explicit" if request.rainfall is not None else "unavailable",
            "water_source": request.water_source,
        }

        if request.farm_id:
            if not user:
                raise ValueError("Must be logged in to use farm context")

            farm_service = FarmService(self.db)
            # Will raise ForbiddenException/NotFoundException if invalid
            farm = await farm_service.get_farm(user.id, request.farm_id)

            insights_service = HistoricalInsightsService()
            historical_insights = await insights_service.compute_insights_context(self.db, request.farm_id)

            if input_conditions_used["water_source"] is None and farm.water_source is not None:
                input_conditions_used["water_source"] = farm.water_source

            # Resolve previous crop from history
            history_repo = HistoryRepository(self.db)
            crop_history = await history_repo.get_crop_history(request.farm_id)
            if crop_history:
                # Get the most recent crop
                previous_crop = crop_history[0].crop_name
                input_conditions_used["previous_crop"] = previous_crop

        # 2. Resolve Weather Context
        temp = request.temperature
        humidity = request.humidity
        rain = request.rainfall

        if temp is None or humidity is None or rain is None:
            weather_svc = WeatherService()
            lat, lon = None, None

            if farm and farm.latitude and farm.longitude:
                lat, lon = farm.latitude, farm.longitude
            elif getattr(request, "location_name", None):
                resolved = await weather_svc.resolve_location(request.location_name)
                if resolved:
                    lat, lon = resolved
                    input_conditions_used["location_resolved"] = request.location_name

            if lat is not None and lon is not None:
                weather_data = await weather_svc.get_current_weather(lat, lon)
                if temp is None:
                    temp = weather_data.get("temperature")
                    input_conditions_used["temperature_source"] = weather_data.get("source", "weather_service") if temp is not None else "unavailable"
                if humidity is None:
                    humidity = weather_data.get("humidity")
                    input_conditions_used["humidity_source"] = weather_data.get("source", "weather_service") if humidity is not None else "unavailable"
                # Do NOT fallback rain to daily weather_data.get("rainfall")
                # Daily precipitation cannot be compared to seasonal crop water requirements.

        input_conditions_used["temperature"] = temp
        input_conditions_used["humidity"] = humidity
        input_conditions_used["rainfall"] = rain

        # 3. Construct Recommendation Context
        context = RecommendationContext(
            soil_type=request.soil_type,
            season=request.season,
            water_source=input_conditions_used["water_source"],
            temperature=temp,
            humidity=humidity,
            rainfall=rain,
            farm_id=request.farm_id,
            previous_crop=previous_crop,
            disease_history=historical_insights.disease_patterns if historical_insights else None,
            farm_performance=historical_insights,
        )

        # 4. Generate Candidates & Base Scores
        candidates = await self.candidate_generator.get_candidates()
        if not candidates:
            return CropRecommendationResponseV6(recommendations=[], input_conditions_used=input_conditions_used)

        base_scores = await self.scorer.score_candidates(candidates, context)

        # 5. Initialize Trackers
        trackers = []
        for candidate in candidates:
            c_name = candidate.crop_name
            # Exclude zero-score candidates before adjustment
            if c_name in base_scores and base_scores[c_name][0] > 0:
                base_score, evidence_coverage_ratio, base_explanation, pos_factors, neg_factors = base_scores[c_name]
                tracker = AdjustmentTracker(
                    crop=candidate,
                    base_score=base_score,
                    base_explanation=base_explanation,
                    evidence_coverage_ratio=evidence_coverage_ratio
                )
                tracker.positive_factors.extend(pos_factors)
                tracker.negative_factors.extend(neg_factors)
                trackers.append(tracker)

        # 6. Apply Adjustments in Fixed Order
        self.season_filter.apply(trackers, context)
        await self.water_adjuster.apply(trackers, context)
        self.rotation_adjuster.apply(trackers, context)
        self.disease_adjuster.apply(trackers, context)
        self.performance_adjuster.apply(trackers, context)

        # 6.5 Rank candidates
        from app.services.crop_recommendation.ranker import RecommendationRanker
        ranked_trackers = RecommendationRanker.rank(trackers)

        # 6.6 Limit to Top 4 recommendations
        ranked_trackers = ranked_trackers[:4]

        # 7. Construct Final Responses
        final_recs = []
        for t in ranked_trackers:
            has_personalization = bool(t.positive_factors or t.negative_factors or t.constraints_applied)

            final_recs.append(
                CropRecommendationV6(
                    crop_name=t.crop.crop_name,
                    final_score=t.base_score,  # final_score is preserved as agronomic suitability for backward compatibility
                    base_score=t.base_score,
                    explanation=t.to_explanation_payload(),
                    personalization_applied=has_personalization,
                    engine_version="v6.3-core",
                    eligibility_constraints=t.eligibility_constraints,
                    biological_risks=t.biological_risks,
                    historical_evidence=t.historical_evidence
                )
            )

        return CropRecommendationResponseV6(
            recommendations=final_recs,
            input_conditions_used=input_conditions_used
        )

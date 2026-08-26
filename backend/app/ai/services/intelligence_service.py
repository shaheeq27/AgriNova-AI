"""
AgriNova AI — Intelligence Service.

Orchestrates the existing AgriNova intelligence engines based on
intent-aware engine selection.  Only calls engines that are relevant
to the user's question.

Design principles:
  - Never calls an engine without the required inputs.
  - Never fabricates input values (e.g. fake weather for irrigation).
  - Never mutates the database (read-only engine calls).
  - Engine results are returned as structured Pydantic models,
    NOT pre-formatted strings.
  - Failures in individual engines are caught and logged, never
    propagated to the caller.
"""

from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas.context import (
    CropEngineOutput,
    DiseaseResult,
    EngineContext,
    FarmContext,
    FertilizerResult,
    IrrigationResult,
    WeatherData,
)
from app.ai.services.intent_router import IntentResult
from app.services.irrigation_engine import IrrigationEngine
from app.services.fertilizer_engine import FertilizerEngine
from app.services.disease_service import DiseaseService
from app.services.timeline_service import get_timeline

logger = logging.getLogger(__name__)


class IntelligenceService:
    """Builds ``EngineContext`` by calling relevant engines.

    Usage::

        svc = IntelligenceService(db)
        engine_ctx = await svc.build_engine_context(
            farm_context, weather_data, intent
        )
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.irrigation_engine = IrrigationEngine()
        self.fertilizer_engine = FertilizerEngine()
        self.disease_service = DiseaseService(db)

    async def build_engine_context(
        self,
        farm_context: FarmContext,
        weather_data: WeatherData | None,
        intent: IntentResult,
        historical_insights: HistoricalInsightsContext | None = None
    ) -> EngineContext | None:
        """Build engine outputs for the relevant crops.

        Args:
            farm_context: The farmer's farm context (crops, soil, etc.).
            weather_data: Available weather data (may be None).
            intent: Detected intent from the user's message.

        Returns:
            ``EngineContext`` with outputs, or ``None`` if no engines
            were invoked or no crops are available.
        """
        if not farm_context.crops:
            return None

        if not intent.any_engine:
            return None

        crop_outputs: list[CropEngineOutput] = []

        for crop in farm_context.crops:
            if crop.status != "active":
                continue

            output = await self._build_crop_output(
                crop_name=crop.crop_name,
                crop_id=crop.crop_id,
                soil_type=farm_context.soil_type,
                weather_data=weather_data,
                intent=intent,
                historical_insights=historical_insights,
            )

            if output:
                crop_outputs.append(output)

        if not crop_outputs:
            return None

        return EngineContext(crop_outputs=crop_outputs)

    # ── Private helpers ─────────────────────────────────────────────────

    async def _build_crop_output(
        self,
        crop_name: str,
        crop_id: str | None,
        soil_type: str,
        weather_data: WeatherData | None,
        intent: IntentResult,
        historical_insights: HistoricalInsightsContext | None = None
    ) -> CropEngineOutput | None:
        """Build engine outputs for a single crop."""

        current_stage: str | None = None
        irrigation: IrrigationResult | None = None
        fertilizer: FertilizerResult | None = None
        diseases: list[DiseaseResult] = []

        # Step 1: Determine current growth stage from timeline
        # (needed by irrigation and fertilizer engines)
        if (intent.irrigation or intent.fertilizer or intent.timeline) and crop_id:
            current_stage = await self._get_current_stage(crop_id)

        # Step 2: Irrigation engine
        if intent.irrigation and current_stage:
            weather_dict = self._extract_weather_dict(weather_data)
            if weather_dict is not None:
                irrigation = await self._get_irrigation(
                    crop_name, current_stage, soil_type, weather_dict, historical_insights
                )
            else:
                # No weather → call without weather adjustment
                irrigation = await self._get_irrigation(
                    crop_name, current_stage, soil_type, None, historical_insights
                )

        # Step 3: Fertilizer engine
        if intent.fertilizer and current_stage:
            fertilizer = await self._get_fertilizer(
                crop_name, current_stage, soil_type, historical_insights
            )

        # Step 4: Disease detection (only when symptoms provided)
        if intent.disease and intent.symptoms:
            diseases = await self._get_diseases(crop_name, intent.symptoms, historical_insights)

        # Only return an output if something was computed
        has_data = current_stage or irrigation or fertilizer or diseases
        if not has_data:
            return None

        return CropEngineOutput(
            crop_name=crop_name,
            current_stage=current_stage,
            irrigation=irrigation,
            fertilizer=fertilizer,
            diseases=diseases,
        )

    async def _get_current_stage(self, crop_id: str) -> str | None:
        """Get the current growth stage from the timeline service.

        Read-only — does NOT generate a timeline if one doesn't exist.
        """
        try:
            timeline = await get_timeline(self.db, crop_id)
            return timeline.current_stage
        except Exception:
            logger.debug(
                "No timeline for crop %s — skipping stage lookup", crop_id
            )
            return None

    async def _get_irrigation(
        self,
        crop_name: str,
        growth_stage: str,
        soil_type: str,
        weather_dict: dict | None,
        historical_insights: HistoricalInsightsContext | None = None
    ) -> IrrigationResult | None:
        """Call the irrigation engine and convert to structured result."""
        try:
            raw = await self.irrigation_engine.get_recommendation(
                self.db, crop_name, growth_stage, soil_type, weather_dict, historical_insights
            )
            return IrrigationResult(
                water_requirement_mm=raw["water_requirement_mm"],
                frequency=raw["frequency"],
                method=raw["method"],
                explanation=raw["explanation"],
                weather_adjusted=raw.get("weather_adjusted", False),
                historically_adjusted=raw.get("historically_adjusted", False),
                personalization_rationale=raw.get("personalization_rationale"),
            )
        except Exception:
            logger.warning(
                "Irrigation engine failed for %s", crop_name, exc_info=True
            )
            return None

    async def _get_fertilizer(
        self,
        crop_name: str,
        growth_stage: str,
        soil_type: str,
        historical_insights: HistoricalInsightsContext | None = None
    ) -> FertilizerResult | None:
        """Call the fertilizer engine and convert to structured result."""
        try:
            raw = await self.fertilizer_engine.get_recommendation(
                self.db, crop_name, growth_stage, soil_type, historical_insights
            )
            return FertilizerResult(
                fertilizer_type=raw["fertilizer_type"],
                quantity_per_acre=raw["quantity_per_acre"],
                unit=raw["unit"],
                timing=raw["timing"],
                application_method=raw["application_method"],
                explanation=raw["explanation"],
                historically_adjusted=raw.get("historically_adjusted", False),
                personalization_rationale=raw.get("personalization_rationale"),
            )
        except Exception:
            logger.warning(
                "Fertilizer engine failed for %s", crop_name, exc_info=True
            )
            return None

    async def _get_diseases(
        self,
        crop_name: str,
        symptoms: list[str],
        historical_insights: HistoricalInsightsContext | None = None
    ) -> list[DiseaseResult]:
        """Call the disease service and convert to structured results."""
        try:
            matches = await self.disease_service.detect_from_symptoms(
                crop_name, symptoms, historical_insights
            )
            return [
                DiseaseResult(
                    disease_name=m.disease_name,
                    confidence=m.confidence,
                    symptoms=m.symptoms,
                    treatment=m.treatment,
                    prevention=m.prevention,
                    severity=m.severity,
                    explanation=m.explanation,
                )
                for m in matches
            ]
        except Exception:
            logger.warning(
                "Disease detection failed for %s", crop_name, exc_info=True
            )
            return []

    @staticmethod
    def _extract_weather_dict(weather_data: WeatherData | None) -> dict | None:
        """Extract the latest weather as a dict for the irrigation engine.

        Returns ``None`` if no weather data is available.
        Never fabricates values.
        """
        if not weather_data:
            return None

        # Prefer the most recent historical entry (actual data)
        source = None
        if weather_data.historical:
            source = weather_data.historical[0]  # Most recent first
        elif weather_data.forecast:
            source = weather_data.forecast[0]

        if not source:
            return None

        # Build the dict the irrigation engine expects.
        # Only include fields that have real values.
        result: dict = {}

        temp = source.temp_avg
        if temp is None and source.temp_max is not None and source.temp_min is not None:
            temp = (source.temp_max + source.temp_min) / 2
        if temp is not None:
            result["temperature"] = temp

        if source.rainfall is not None:
            result["rainfall"] = source.rainfall

        if source.humidity is not None:
            result["humidity"] = source.humidity

        return result if result else None

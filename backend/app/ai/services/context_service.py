"""
AgriNova AI — Context Service.

Builds a structured ``UnifiedContext`` by gathering data from the
farmer's farm, crops, weather, knowledge base, and intelligence engines.

Design principles:
  - Returns structured Pydantic models, NOT formatted strings.
  - Missing optional data (weather API down, no crops yet, KB empty)
    must never fail the chat request — populate what's available,
    leave the rest as None / empty.
  - Ownership validation is the caller's responsibility.  This service
    assumes the ``farm_id`` has already been validated.
  - Reuses existing AgriNova repositories and services.

Phase 6 additions:
  - Accepts ``user_message`` for intent-aware engine selection.
  - Passes ``crop_id`` through to ``CropContext``.
  - Calls ``IntelligenceService`` when intent requires engines.
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas.context import (
    CropContext,
    FarmContext,
    UnifiedContext,
    WeatherContext,
    WeatherData,
)
from app.models.farm import Farm
from app.repositories.crop_repo import CropRepository
from app.repositories.weather_repo import WeatherRepository
from app.services.weather_service import WeatherService
from app.ai.services.knowledge_service import KnowledgeService
from app.ai.services.intelligence_service import IntelligenceService
from app.ai.services.intent_router import IntentResult, detect_intent

logger = logging.getLogger(__name__)

# ── Configuration ────────────────────────────────────────────────────────────
_HISTORICAL_WEATHER_DAYS = 7
_FORECAST_DAYS = 3


class ContextService:
    """Builds the ``UnifiedContext`` for the AI prompt.

    Usage::

        ctx_svc = ContextService(db)
        context = await ctx_svc.build_unified_context(farm, user_message="...")
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db
        self.crop_repo = CropRepository(db)
        self.weather_repo = WeatherRepository(db)
        self.weather_service = WeatherService()
        self.knowledge_service = KnowledgeService(db)
        self.intelligence_service = IntelligenceService(db)

    async def build_unified_context(
        self,
        farm: Farm,
        user_message: str = "",
    ) -> UnifiedContext:
        """Assemble the full context for a farm.

        Args:
            farm: The validated Farm ORM object (with crops eager-loaded
                  via ``selectinload`` from ``FarmRepository.get_by_id``).
            user_message: The user's raw message text, used for
                  intent-aware engine selection (Phase 6).

        Returns:
            Populated ``UnifiedContext``.  Individual sections may be
            ``None`` / empty if the underlying data is unavailable.
        """
        farm_context = self._build_farm_context(farm)
        weather_data = await self._build_weather_data(farm)

        # Phase 4: Retrieve structured knowledge for the farmer's crops
        knowledge = await self._build_knowledge(farm_context, farm.soil_type)

        # Phase 6: Run intelligence engines based on user intent
        intelligence = await self._build_intelligence(
            farm_context, weather_data, user_message
        )

        return UnifiedContext(
            farm=farm_context,
            weather=weather_data,
            knowledge=knowledge,
            intelligence=intelligence,
        )

    # ── Private builders ─────────────────────────────────────────────────

    def _build_farm_context(self, farm: Farm) -> FarmContext:
        """Extract farm + crop context from the ORM model.

        ``farm.crops`` is expected to be eager-loaded (selectinload)
        by ``FarmRepository.get_by_id``.
        """
        crops: list[CropContext] = []
        for crop in (farm.crops or []):
            crops.append(
                CropContext(
                    crop_id=crop.id,
                    crop_name=crop.crop_name,
                    season=crop.season,
                    planting_date=crop.planting_date,
                    expected_harvest_date=crop.expected_harvest_date,
                    status=crop.status,
                    area_acres=crop.area_acres,
                )
            )

        return FarmContext(
            name=farm.name,
            location_city=farm.location_city,
            location_state=farm.location_state,
            soil_type=farm.soil_type,
            total_area_acres=farm.total_area_acres,
            water_source=farm.water_source,
            crops=crops,
        )

    async def _build_weather_data(self, farm: Farm) -> WeatherData | None:
        """Fetch historical weather from DB + forecast from the API.

        Returns ``None`` if both sources fail or if the farm has no
        coordinates (lat/lon required for forecast API).
        """
        historical = await self._get_historical_weather(farm.id)
        forecast = await self._get_forecast_weather(farm)

        if not historical and not forecast:
            return None

        return WeatherData(
            historical=historical,
            forecast=forecast,
        )

    async def _get_historical_weather(
        self, farm_id: str
    ) -> list[WeatherContext]:
        """Load recent weather records from the database."""
        try:
            records = await self.weather_repo.get_history(
                farm_id, days=_HISTORICAL_WEATHER_DAYS
            )
            return [
                WeatherContext(
                    date=r.date,
                    temp_min=r.temp_min,
                    temp_max=r.temp_max,
                    temp_avg=r.temp_avg,
                    rainfall=r.rainfall,
                    humidity=r.humidity,
                    wind_speed=r.wind_speed,
                    condition=r.condition,
                )
                for r in records
            ]
        except Exception:
            logger.warning(
                "Failed to load historical weather for farm %s", farm_id, exc_info=True
            )
            return []

    async def _get_forecast_weather(self, farm: Farm) -> list[WeatherContext]:
        """Fetch forecast from the weather API (Open-Meteo).

        Requires farm latitude/longitude.  Returns empty list if
        coordinates are missing or the API call fails.
        """
        if not farm.latitude or not farm.longitude:
            logger.debug(
                "No coordinates for farm %s — skipping forecast", farm.id
            )
            return []

        try:
            raw_forecast = await self.weather_service.get_forecast(
                latitude=farm.latitude,
                longitude=farm.longitude,
                days=_FORECAST_DAYS,
            )
            return [
                WeatherContext(
                    date=date.fromisoformat(day["date"])
                    if isinstance(day["date"], str)
                    else day["date"],
                    temp_min=day.get("temp_min"),
                    temp_max=day.get("temp_max"),
                    rainfall=day.get("precipitation", 0.0),
                    wind_speed=day.get("wind_speed"),
                    condition=day.get("condition"),
                )
                for day in raw_forecast
            ]
        except Exception:
            logger.warning(
                "Failed to fetch forecast for farm %s", farm.id, exc_info=True
            )
            return []

    async def _build_knowledge(self, farm_context, soil_type: str):
        """Retrieve knowledge from the KB for the farmer's active crops."""
        if not farm_context or not farm_context.crops:
            return None

        crop_names = [c.crop_name for c in farm_context.crops]
        try:
            return await self.knowledge_service.build_knowledge_context(
                crop_names=crop_names,
                soil_type=soil_type,
            )
        except Exception:
            logger.warning(
                "Failed to build knowledge context", exc_info=True
            )
            return None

    async def _build_intelligence(
        self,
        farm_context: FarmContext,
        weather_data: WeatherData | None,
        user_message: str,
    ):
        """Run intelligence engines based on the user's intent.

        Phase 6: Only calls engines relevant to the user's question.
        """
        if not user_message or not farm_context or not farm_context.crops:
            return None

        try:
            intent = detect_intent(user_message)

            if not intent.any_engine:
                return None

            return await self.intelligence_service.build_engine_context(
                farm_context=farm_context,
                weather_data=weather_data,
                intent=intent,
            )
        except Exception:
            logger.warning(
                "Failed to build intelligence context", exc_info=True
            )
            return None

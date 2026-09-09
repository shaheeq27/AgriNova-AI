"""
AgriNova AI — Rule-Based Scorer.
"""
from app.models.knowledge import CropProfile
from app.services.crop_recommendation.context import RecommendationContext
from app.services.crop_recommendation.interfaces import RecommendationScorer

class RuleBasedScorer(RecommendationScorer):
    """
    Calculates the BASE environmental/agronomic suitability score.
    """
    
    async def score_candidates(
        self,
        candidates: list[CropProfile],
        context: RecommendationContext
    ) -> dict[str, float]:
        """
        Score crops based on temperature, humidity, rainfall, and soil.
        Normalizes the score to [0.0, 1.0].
        If an environmental input is missing, it is omitted from the total
        calculation (does not penalize the score).
        """
        results = {}
        
        # Extract environmental conditions
        temp = context.temperature
        humidity = context.humidity
        rain = context.rainfall
        
        # Fallback to current weather if explicit inputs not provided
        if temp is None and context.current_weather:
            temp = context.current_weather.temp_avg
        if humidity is None and context.current_weather:
            humidity = context.current_weather.humidity
        if rain is None and context.current_weather:
            rain = context.current_weather.rainfall

        soil_type = context.soil_type

        for p in candidates:
            score = 0.0
            total = 0.0

            # Temperature match
            if temp is not None:
                total += 1.0
                if p.temp_min <= temp <= p.temp_max:
                    score += 1.0
                else:
                    dist = min(abs(temp - p.temp_min), abs(temp - p.temp_max))
                    score += max(0.0, 1.0 - (dist / 10.0))

            # Humidity match
            if humidity is not None:
                total += 1.0
                if p.humidity_min <= humidity <= p.humidity_max:
                    score += 1.0
                else:
                    dist = min(abs(humidity - p.humidity_min), abs(humidity - p.humidity_max))
                    score += max(0.0, 1.0 - (dist / 20.0))

            # Rainfall match
            if rain is not None:
                total += 1.0
                if p.rain_min <= rain <= p.rain_max:
                    score += 1.0
                else:
                    dist = min(abs(rain - p.rain_min), abs(rain - p.rain_max))
                    score += max(0.0, 1.0 - (dist / 50.0))

            # Soil match
            if soil_type:
                total += 1.0
                # Using existing CropProfile convention (comma-separated string)
                if soil_type.lower() in (p.ideal_soil_types or "").lower():
                    score += 1.0

            # Calculate final normalized score
            if total > 0.0:
                final_score = round(max(0.0, min(1.0, score / total)), 4)
            else:
                # If no environmental or soil data is available at all
                final_score = 0.0

            results[p.crop_name] = final_score
            
        return results

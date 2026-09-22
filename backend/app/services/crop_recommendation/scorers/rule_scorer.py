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
    ) -> dict[str, tuple[float, float, str, list[str], list[str]]]:
        """
        Score crops based on temperature, humidity, rainfall, and soil.
        Normalizes the score to [0.0, 1.0] based ONLY on evaluated factors.
        Returns raw suitability and a separate evidence coverage ratio.
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
        # Do not fallback rain to daily rainfall

        soil_type = context.soil_type

        expected_factors = 4.0

        for p in candidates:
            score = 0.0
            total = 0.0
            pos = []
            neg = []
            unavailable_factors = []

            # Temperature match
            if temp is not None:
                total += 1.0
                if p.temp_min <= temp <= p.temp_max:
                    score += 1.0
                    pos.append("Temperature falls within the crop's supported range.")
                else:
                    dist = min(abs(temp - p.temp_min), abs(temp - p.temp_max))
                    added = max(0.0, 1.0 - (dist / 10.0))
                    score += added
                    if added > 0:
                        neg.append("Temperature is slightly outside preferred bounds.")
                    else:
                        neg.append("Temperature is far outside preferred bounds.")
            else:
                unavailable_factors.append("Temperature")

            # Humidity match
            if humidity is not None:
                total += 1.0
                if p.humidity_min <= humidity <= p.humidity_max:
                    score += 1.0
                    pos.append("Humidity matches ideal conditions.")
                else:
                    dist = min(abs(humidity - p.humidity_min), abs(humidity - p.humidity_max))
                    added = max(0.0, 1.0 - (dist / 20.0))
                    score += added
                    if added > 0:
                        neg.append("Humidity is slightly outside ideal bounds.")
                    else:
                        neg.append("Humidity is far outside ideal bounds.")
            else:
                unavailable_factors.append("Humidity")

            # Rainfall match
            if rain is not None:
                total += 1.0
                if p.rain_min <= rain <= p.rain_max:
                    score += 1.0
                    pos.append("Current rainfall is well-suited.")
                else:
                    dist = min(abs(rain - p.rain_min), abs(rain - p.rain_max))
                    added = max(0.0, 1.0 - (dist / 50.0))
                    score += added
                    if added > 0:
                        neg.append("Rainfall is sub-optimal but tolerable.")
                    else:
                        neg.append("Rainfall is severely deficient/excessive.")
            else:
                unavailable_factors.append("Rainfall")

            # Soil match
            if soil_type:
                total += 1.0
                if soil_type.lower() in (p.ideal_soil_types or "").lower():
                    score += 1.0
                    pos.append(f"Soil type ({soil_type}) is compatible.")
                else:
                    neg.append(f"Soil type ({soil_type}) is not ideal.")
            else:
                unavailable_factors.append("Soil type")

            # Calculate final normalized score
            evidence_coverage_ratio = total / expected_factors

            if total > 0.0:
                raw_suitability = score / total
                final_score = round(max(0.0, min(1.0, raw_suitability)), 4)

                # Build explanation
                base_explanation = f"Base environmental suitability: {final_score:.2f}."
                if unavailable_factors:
                    if len(unavailable_factors) == 1:
                        msg = f"{unavailable_factors[0]} was unavailable, so {unavailable_factors[0].lower()} suitability was not evaluated."
                    else:
                        if len(unavailable_factors) == 2:
                            joined = f"{unavailable_factors[0]} and {unavailable_factors[1]}"
                        else:
                            joined = ", ".join(unavailable_factors[:-1]) + f" and {unavailable_factors[-1]}"
                        msg = f"{joined} were unavailable and were not evaluated."
                    base_explanation += f" ({msg})"
            else:
                final_score = 0.0
                base_explanation = "No environmental factors were available to evaluate."

            results[p.crop_name] = (final_score, evidence_coverage_ratio, base_explanation, pos, neg)

        return results

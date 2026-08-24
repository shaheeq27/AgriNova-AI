"""
AgriNova AI — Historical Insights Service.

Generates deterministic, lightweight insights from existing farm history
without executing a secondary LLM call.
"""

from collections import defaultdict
from app.ai.schemas.context import FarmHistoryContext, HistoricalInsights


class HistoricalInsightsService:
    """Extracts structured insights from FarmHistoryContext."""

    def generate_insights(self, history: FarmHistoryContext | None) -> HistoricalInsights:
        """
        Generate deterministic insights based on historical farm data.
        
        Rules:
        - "Successful crop": must be harvested with a >0 yield.
        - "Recurring diseases": must appear >1 time in recent_diseases.
        - Yield observations: must preserve units distinctly.
        - If no history exists, safely returns empty insights.
        """
        insights = HistoricalInsights()
        
        if not history:
            return insights

        # 1. Successful crops
        # Must be harvested and have yield > 0.
        successful = []
        for crop in history.past_crops:
            if crop.status == "harvested" and crop.yield_amount is not None and crop.yield_amount > 0:
                name = crop.crop_name
                if crop.variety:
                    name += f" ({crop.variety})"
                successful.append(name)
        
        # Deduplicate while preserving order mostly
        # Using dict.fromkeys to keep order
        insights.successful_crops = list(dict.fromkeys(successful))

        # 2. Recurring diseases
        # recent_diseases strings are formatted like "Rust — high severity — resolved"
        disease_counts = defaultdict(int)
        for d in history.recent_diseases:
            name = d.split(" — ")[0].strip()
            disease_counts[name] += 1
            
        recurring = []
        for name, count in disease_counts.items():
            if count > 1:
                recurring.append(name)
        insights.recurring_diseases = recurring
        
        # 3. Seasonal crop patterns
        insights.seasonal_crop_patterns = history.seasonal_patterns.copy()

        # 4. Historical yield observations
        # Group by crop and unit to avoid averaging incompatible units.
        # "200 kg" and "1.5 tons" remain separate.
        yield_obs = defaultdict(list)
        for crop in history.past_crops:
            if crop.yield_amount is not None and crop.yield_amount > 0 and crop.yield_unit:
                obs = f"{crop.yield_amount} {crop.yield_unit}"
                yield_obs[crop.crop_name].append(obs)
                
        yield_summaries = []
        for crop_name, obs_list in yield_obs.items():
            yield_summaries.append(f"{crop_name}: {', '.join(obs_list)}")
            
        insights.historical_yield_observations = yield_summaries
        
        return insights

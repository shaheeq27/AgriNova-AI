"""
AgriNova AI — Season Filter.
"""
from app.models.knowledge import CropProfile
from app.services.crop_recommendation.context import RecommendationContext

class SeasonFilter:
    """
    Filters candidates based on season compatibility.
    Does not modify the base score.
    """
    
    def filter_candidates(
        self,
        candidates: list[CropProfile],
        context: RecommendationContext
    ) -> list[CropProfile]:
        """
        Retains candidates if:
        - No target season is supplied
        - Target season matches growing season
        - Growing season is "All"
        """
        if not context.season:
            return list(candidates)
            
        target_season = context.season.strip().lower()
        
        filtered = []
        for p in candidates:
            crop_season = (p.growing_season or "").strip().lower()
            if crop_season == target_season or crop_season == "all":
                filtered.append(p)
                
        return filtered

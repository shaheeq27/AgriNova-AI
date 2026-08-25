"""
AgriNova AI — Context Formatter.

Translates the populated ``UnifiedContext`` into a concise,
deterministic, clearly delimited representation for the LLM.

Design principles:
  - Do NOT include unnecessary fields or raw database objects.
  - Output is human-readable plain text, not JSON.
  - Explicitly indicate when data is unavailable rather than
    silently omitting sections.
  - Delimited with ``[FARM CONTEXT]`` / ``[/FARM CONTEXT]`` markers
    so the system prompt can instruct Aira to treat it as data.
"""

from __future__ import annotations

from datetime import date

from app.ai.schemas.context import UnifiedContext, HistoricalInsights


def format_context(context: UnifiedContext) -> str:
    """Format the ``UnifiedContext`` into a prompt-ready string.

    Returns an empty string if no context sections are populated.
    """
    sections: list[str] = []

    if context.farm:
        sections.append(_format_farm(context))

    if context.weather:
        sections.append(_format_weather(context))

    if not sections:
        farm_block = ""
    else:
        body = "\n\n".join(sections)
        farm_block = f"[FARM CONTEXT]\n{body}\n[/FARM CONTEXT]"

    knowledge_block = ""
    if context.knowledge and context.knowledge.crop_knowledge:
        knowledge_block = _format_knowledge(context)

    intelligence_block = ""
    if context.intelligence and context.intelligence.crop_outputs:
        intelligence_block = _format_intelligence(context)

    history_block = ""
    if context.history:
        history_block = _format_history(context)
        
    parts = [p for p in [farm_block, knowledge_block, intelligence_block, history_block] if p]
    return "\n\n".join(parts)


# ── Private formatters ───────────────────────────────────────────────────────

def _format_farm(context: UnifiedContext) -> str:
    """Format farm information + crops."""
    farm = context.farm
    lines = [
        "Farm:",
        f"  Name: {farm.name}",
        f"  Location: {farm.location_city}"
        + (f", {farm.location_state}" if farm.location_state else ""),
        f"  Soil: {farm.soil_type}",
        f"  Area: {farm.total_area_acres} acres",
    ]
    if farm.water_source:
        lines.append(f"  Water Source: {farm.water_source}")

    if farm.crops:
        lines.append("")
        lines.append("Crops:")
        for crop in farm.crops:
            lines.append(f"  - {crop.crop_name} ({crop.status})")
            lines.append(f"    Season: {crop.season}")
            lines.append(f"    Area: {crop.area_acres} acres")
            if crop.planting_date:
                days_since = (date.today() - crop.planting_date).days
                lines.append(
                    f"    Planted: {crop.planting_date.isoformat()}"
                    f" ({days_since} days ago)"
                )
            if crop.expected_harvest_date:
                days_until = (crop.expected_harvest_date - date.today()).days
                if days_until > 0:
                    lines.append(
                        f"    Expected Harvest: {crop.expected_harvest_date.isoformat()}"
                        f" ({days_until} days from now)"
                    )
                else:
                    lines.append(
                        f"    Expected Harvest: {crop.expected_harvest_date.isoformat()}"
                        f" (overdue by {abs(days_until)} days)"
                    )
    else:
        lines.append("")
        lines.append("Crops: None currently planted.")

    return "\n".join(lines)


def _format_weather(context: UnifiedContext) -> str:
    """Format historical + forecast weather."""
    weather = context.weather
    lines = []

    if weather.historical:
        lines.append("Recent Weather:")
        for w in weather.historical[:5]:  # Cap at 5 most recent
            parts = [f"  {w.date.isoformat()}: {_temp_str(w)}"]
            if w.rainfall and w.rainfall > 0:
                parts.append(f"Rain {w.rainfall}mm")
            if w.humidity is not None:
                parts.append(f"Humidity {w.humidity}%")
            if w.condition:
                parts.append(w.condition)
            lines.append(", ".join(parts))
    else:
        lines.append("Recent Weather: Unavailable.")

    if weather.forecast:
        lines.append("")
        lines.append("Forecast:")
        for w in weather.forecast:
            parts = [f"  {w.date.isoformat()}: {_temp_str(w)}"]
            if w.rainfall and w.rainfall > 0:
                parts.append(f"Rain {w.rainfall}mm")
            if w.condition:
                parts.append(w.condition)
            lines.append(", ".join(parts))
    else:
        lines.append("")
        lines.append("Forecast: Unavailable.")

    return "\n".join(lines)


def _temp_str(w) -> str:
    """Build a temperature description from available fields."""
    if w.temp_min is not None and w.temp_max is not None:
        return f"{w.temp_min}–{w.temp_max}°C"
    if w.temp_avg is not None:
        return f"{w.temp_avg}°C avg"
    return "temp N/A"


def _format_knowledge(context: UnifiedContext) -> str:
    """Format knowledge base entries for the farmer's crops."""
    knowledge = context.knowledge
    lines = ["[KNOWLEDGE]"]

    for ck in knowledge.crop_knowledge:
        lines.append(f"\n{ck.crop_name}:")

        if ck.profile_description:
            lines.append(f"  Description: {ck.profile_description}")
        if ck.ideal_conditions:
            lines.append(f"  Ideal Conditions: {ck.ideal_conditions}")

        if ck.growth_stages:
            lines.append("  Growth Stages:")
            for stage in ck.growth_stages:
                lines.append(f"    - {stage}")

        if ck.diseases:
            lines.append("  Known Diseases:")
            for disease in ck.diseases:
                lines.append(f"    - {disease}")

        if ck.fertilizer_schedule:
            lines.append("  Fertilizer Schedule:")
            for fert in ck.fertilizer_schedule:
                lines.append(f"    - {fert}")

        if ck.irrigation_guidelines:
            lines.append("  Irrigation Guidelines:")
            for irrig in ck.irrigation_guidelines:
                lines.append(f"    - {irrig}")

        # If nothing was found for this crop
        has_data = any([
            ck.profile_description, ck.ideal_conditions,
            ck.growth_stages, ck.diseases,
            ck.fertilizer_schedule, ck.irrigation_guidelines,
        ])
        if not has_data:
            lines.append("  No knowledge base entries available for this crop.")

    lines.append("[/KNOWLEDGE]")
    return "\n".join(lines)


def _format_intelligence(context: UnifiedContext) -> str:
    """Format intelligence engine outputs for the farmer's crops."""
    intelligence = context.intelligence
    lines = ["[INTELLIGENCE]"]

    for co in intelligence.crop_outputs:
        lines.append(f"\n{co.crop_name}:")

        if co.current_stage:
            lines.append(f"  Current Growth Stage: {co.current_stage}")

        if co.irrigation:
            ir = co.irrigation
            parts = [f"{ir.water_requirement_mm}mm via {ir.method}"]
            parts.append(f"Frequency: {ir.frequency}")
            if ir.weather_adjusted:
                parts.append("(weather-adjusted)")
            lines.append(f"  Irrigation Recommendation: {', '.join(parts)}")
            lines.append(f"    Reason: {ir.explanation}")

        if co.fertilizer:
            fr = co.fertilizer
            lines.append(
                f"  Fertilizer Recommendation: {fr.fertilizer_type}"
                f" {fr.quantity_per_acre} {fr.unit}/acre,"
                f" {fr.timing} ({fr.application_method})"
            )
            lines.append(f"    Reason: {fr.explanation}")

        if co.diseases:
            lines.append("  Disease Analysis:")
            for dr in co.diseases:
                pct = int(dr.confidence * 100)
                lines.append(f"    - {dr.disease_name} (confidence: {pct}%, severity: {dr.severity})")
                if dr.treatment:
                    lines.append(f"      Treatment: {dr.treatment}")
                if dr.prevention:
                    lines.append(f"      Prevention: {dr.prevention}")

    lines.append("[/INTELLIGENCE]")
    return "\n".join(lines)


def _format_history(context: UnifiedContext) -> str:
    """Format historical farm data."""
    history = context.history
    lines = ["[FARM HISTORY]"]
    
    has_data = False

    if history.past_crops:
        has_data = True
        lines.append("\nPast Crops:")
        for crop in history.past_crops:
            header = f"  - {crop.crop_name}"
            if crop.variety:
                header += f" | Variety: {crop.variety}"
            if crop.season:
                header += f" | Season: {crop.season}"
            lines.append(header)
            
            lines.append(f"    Status: {crop.status}")
            if crop.planting_date:
                lines.append(f"    Planted: {crop.planting_date.isoformat()}")
            if crop.harvest_date:
                lines.append(f"    Harvested: {crop.harvest_date.isoformat()}")
            if crop.yield_amount is not None and crop.yield_unit:
                lines.append(f"    Yield: {crop.yield_amount} {crop.yield_unit}")
                
            lines.append(f"    Disease records: {crop.disease_count}")
            lines.append(f"    Fertilizer applications: {crop.fertilizer_applications}")
            lines.append(f"    Irrigation applications: {crop.irrigation_applications}")

    if history.recent_diseases:
        has_data = True
        lines.append("\nRecent Diseases:")
        for d in history.recent_diseases:
            lines.append(f"  - {d}")

    if history.seasonal_patterns:
        has_data = True
        lines.append("\nSeasonal Patterns:")
        for pattern in history.seasonal_patterns:
            lines.append(f"  - {pattern}")

    if history.performance_summary:
        has_data = True
        lines.append("\nPerformance Summary:")
        for line in history.performance_summary.split("\n"):
            lines.append(f"  {line}")

    if not has_data:
        lines.append("  No historical data available.")

    lines.append("[/FARM HISTORY]")
    return "\n".join(lines)

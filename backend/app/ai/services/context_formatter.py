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

    historical_insights_block = ""
    if context.historical_insights:
        historical_insights_block = _format_historical_insights(context)

    market_block = ""
    if context.market and context.market.prices:
        market_block = _format_market(context)

    parts = [p for p in [farm_block, knowledge_block, intelligence_block, history_block, historical_insights_block, market_block] if p]
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
            if getattr(ir, "historically_adjusted", False) and getattr(ir, "personalization_rationale", None):
                lines.append(f"    Personalization: Adjusted based on farm history - {ir.personalization_rationale}")

        if co.fertilizer:
            fr = co.fertilizer
            lines.append(
                f"  Fertilizer Recommendation: {fr.fertilizer_type}"
                f" {fr.quantity_per_acre} {fr.unit}/acre,"
                f" {fr.timing} ({fr.application_method})"
            )
            lines.append(f"    Reason: {fr.explanation}")
            if getattr(fr, "historically_adjusted", False) and getattr(fr, "personalization_rationale", None):
                lines.append(f"    Personalization: Adjusted based on farm history - {fr.personalization_rationale}")

        if co.diseases:
            lines.append("  Disease Analysis:")
            for dr in co.diseases:
                pct = int(dr.confidence * 100)
                lines.append(f"    - {dr.disease_name} (confidence: {pct}%, severity: {dr.severity})")
                if dr.treatment:
                    lines.append(f"      Treatment: {dr.treatment}")
                if dr.prevention:
                    lines.append(f"      Prevention: {dr.prevention}")
                if getattr(dr, "historically_adjusted", False) and getattr(dr, "personalization_rationale", None):
                    lines.append(f"      Personalization: Adjusted based on farm history - {dr.personalization_rationale}")

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



def _format_historical_insights(context: UnifiedContext) -> str:
    """Format deterministic historical insights."""
    insights = context.historical_insights
    if not insights:
        return ""

    lines = ["[HISTORICAL INSIGHTS]"]
    has_data = False

    if insights.crop_performance:
        has_data = True
        lines.append("\nCrop Performance:")
        for cp in insights.crop_performance:
            header = f"  - {cp.crop_name}"
            if cp.variety:
                header += f" ({cp.variety})"
            lines.append(header)
            lines.append(f"    Observed: {cp.crops_observed} planted, {cp.harvested_count} harvested")
            if cp.seasons_observed:
                lines.append(f"    Seasons: {', '.join(cp.seasons_observed)}")
            if cp.average_yield is not None and cp.yield_unit:
                lines.append(f"    Avg Yield: {cp.average_yield} {cp.yield_unit}")
            if cp.best_yield is not None and cp.yield_unit:
                lines.append(f"    Best Yield: {cp.best_yield} {cp.yield_unit}")
            if cp.worst_yield is not None and cp.yield_unit:
                lines.append(f"    Worst Yield: {cp.worst_yield} {cp.yield_unit}")
            if cp.disease_records > 0:
                lines.append(f"    Disease Records: {cp.disease_records}")
            if cp.confidence is not None:
                lines.append(f"    Confidence: {int(cp.confidence * 100)}%")

    if insights.yield_trends:
        has_data = True
        lines.append("\nYield Trends:")
        for yt in insights.yield_trends:
            lines.append(f"  - {yt.crop_name} ({yt.yield_unit})")
            if yt.trend_direction:
                lines.append(f"    Trend: {yt.trend_direction}")
            lines.append(f"    Observations: {yt.observations}")
            if yt.average_yield is not None:
                lines.append(f"    Avg: {yt.average_yield}")
            if yt.highest_yield is not None:
                lines.append(f"    High: {yt.highest_yield}")
            if yt.lowest_yield is not None:
                lines.append(f"    Low: {yt.lowest_yield}")
            if yt.confidence is not None:
                lines.append(f"    Confidence: {int(yt.confidence * 100)}%")

    if insights.seasonal_performance:
        has_data = True
        lines.append("\nSeasonal Performance:")
        for sp in insights.seasonal_performance:
            lines.append(f"  - Season: {sp.season}")
            lines.append(f"    Observed: {sp.crops_observed} planted, {sp.harvested_crops} harvested")
            if sp.average_yield is not None and sp.yield_unit:
                lines.append(f"    Avg Yield: {sp.average_yield} {sp.yield_unit}")
            if sp.confidence is not None:
                lines.append(f"    Confidence: {int(sp.confidence * 100)}%")

    if insights.disease_patterns:
        has_data = True
        lines.append("\nDisease Patterns:")
        for dp in insights.disease_patterns:
            lines.append(f"  - {dp.disease_name} (on {dp.affected_crop})")
            lines.append(f"    Occurrences: {dp.occurrence_count} ({dp.resolved_count} resolved, {dp.active_count} active)")
            if dp.common_severity:
                lines.append(f"    Common Severity: {dp.common_severity}")
            if dp.treatment_observed:
                lines.append(f"    Common Treatment: {dp.treatment_observed}")
            if dp.confidence is not None:
                lines.append(f"    Confidence: {int(dp.confidence * 100)}%")

    if insights.input_usage:
        has_data = True
        lines.append("\nInput Usage:")
        for iu in insights.input_usage:
            lines.append(f"  - {iu.input_type} on {iu.crop_name}")
            lines.append(f"    Applications: {iu.application_count}")
            if iu.total_quantity is not None and iu.quantity_unit:
                lines.append(f"    Total Quantity: {iu.total_quantity} {iu.quantity_unit}")
            if iu.common_application_method:
                lines.append(f"    Common Method: {iu.common_application_method}")
            if iu.confidence is not None:
                lines.append(f"    Confidence: {int(iu.confidence * 100)}%")

    if not has_data:
        return ""

    lines.append("[/HISTORICAL INSIGHTS]")
    return "\n".join(lines)


def _format_market(context: UnifiedContext) -> str:
    """Format market intelligence for the farmer's active crops."""
    market = context.market
    if not market or not market.prices:
        return ""
        
    lines = ["[MARKET DATA]"]

    if market.last_updated:
        try:
            from zoneinfo import ZoneInfo
            dt = market.last_updated.astimezone(ZoneInfo("Asia/Kolkata"))
            lines.append(f"Last Updated: {dt.strftime('%d %b %Y %H:%M')} IST")
        except Exception:
            lines.append(f"Last Updated: {market.last_updated.strftime('%d %b %Y %H:%M')} UTC")

    for price in market.prices:
        lines.append(f"{price.commodity}:")
        
        price_str = ""
        if price.min_price is not None and price.max_price is not None:
            price_str = f"₹{price.min_price:,.0f}–₹{price.max_price:,.0f}/quintal (modal: ₹{price.modal_price:,.0f})"
        else:
            price_str = f"₹{price.modal_price:,.0f}/quintal"
            
        market_str = f"{price.market_name}: " if price.market_name else ""
        date_str = f" — {price.price_date.strftime('%d %b %Y')}" if price.price_date else ""
        
        lines.append(f"  {market_str}{price_str}{date_str}")
        
        if price.price_change_pct is not None:
            sign = "+" if price.price_change_pct > 0 else ""
            lines.append(f"  Price Change: {sign}{price.price_change_pct:.1f}%")

    status = market.data_status.capitalize() if market.data_status else "Unknown"
    lines.append(f"Data Status: {status}")
    lines.append("[/MARKET DATA]")
    
    return "\n".join(lines)

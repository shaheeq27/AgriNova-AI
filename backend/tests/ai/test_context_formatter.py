"""
Tests for ContextFormatter, focusing on V4 Phase 1 Step 7 historical formatting.
"""

from datetime import date
from app.ai.schemas.context import (
    UnifiedContext,
    FarmHistoryContext,
    CropHistoryEntry,
    FarmContext,
    CropContext,
)
from app.ai.services.context_formatter import format_context


def test_format_context_without_history():
    """Verify UnifiedContext without history produces the exact existing output."""
    farm_ctx = FarmContext(
        name="Sunny Farm",
        location_city="Pune",
        soil_type="Black",
        total_area_acres=10.0,
        crops=[
            CropContext(
                crop_name="Cotton",
                season="Kharif",
                status="active",
                area_acres=5.0
            )
        ]
    )

    context = UnifiedContext(farm=farm_ctx)
    result = format_context(context)

    assert "[FARM CONTEXT]" in result
    assert "Sunny Farm" in result
    assert "[FARM HISTORY]" not in result


def test_format_context_with_empty_history():
    """Verify empty FarmHistoryContext is handled safely."""
    history_ctx = FarmHistoryContext()
    context = UnifiedContext(history=history_ctx)

    result = format_context(context)
    assert "[FARM HISTORY]" in result
    assert "No historical data available." in result
    assert "[/FARM HISTORY]" in result


def test_format_context_with_populated_history():
    """Verify past crop information, yield, counts, diseases, patterns, summary."""
    history_ctx = FarmHistoryContext(
        past_crops=[
            CropHistoryEntry(
                crop_name="Wheat",
                variety="HD-2967",
                season="Rabi",
                planting_date=date(2025, 11, 1),
                harvest_date=date(2026, 3, 15),
                yield_amount=200.0,
                yield_unit="kg",
                status="harvested",
                disease_count=1,
                fertilizer_applications=2,
                irrigation_applications=3
            )
        ],
        recent_diseases=[
            "Rust — high severity — resolved — treatment: Fungicide X",
            "Blight — medium severity — active"
        ],
        seasonal_patterns=[
            "Rabi: Wheat, Maize",
            "Kharif: Rice"
        ],
        performance_summary="3 recorded crops; 1 harvested and 1 abandoned.\nAverage recorded yield: 200 kg across 1 crop."
    )

    context = UnifiedContext(history=history_ctx)
    result = format_context(context)

    # Check section headers
    assert "[FARM HISTORY]" in result
    assert "Past Crops:" in result
    assert "Recent Diseases:" in result
    assert "Seasonal Patterns:" in result
    assert "Performance Summary:" in result

    # Past crops
    assert "- Wheat | Variety: HD-2967 | Season: Rabi" in result
    assert "Status: harvested" in result
    assert "Yield: 200.0 kg" in result
    assert "Disease records: 1" in result
    assert "Fertilizer applications: 2" in result
    assert "Irrigation applications: 3" in result

    # Recent diseases
    assert "- Rust — high severity — resolved" in result
    assert "- Blight — medium severity" in result

    # Seasonal patterns
    assert "- Rabi: Wheat, Maize" in result
    assert "- Kharif: Rice" in result

    # Performance summary
    assert "3 recorded crops; 1 harvested and 1 abandoned." in result
    assert "Average recorded yield: 200 kg across 1 crop." in result


def test_format_context_optional_fields():
    """Verify missing optional fields don't produce 'None' text."""
    history_ctx = FarmHistoryContext(
        past_crops=[
            CropHistoryEntry(
                crop_name="Rice",
                season="Kharif",
                status="active"
            )
        ]
    )
    context = UnifiedContext(history=history_ctx)
    result = format_context(context)

    assert "- Rice | Season: Kharif" in result
    assert "Variety:" not in result
    assert "Planted:" not in result
    assert "Harvested:" not in result
    assert "Yield:" not in result
    assert "None" not in result

from app.ai.schemas.historical_analysis import (
    HistoricalInsightsContext,
    CropPerformanceInsight,
    SeasonalPerformanceInsight,
    DiseasePatternInsight,
    InputUsageInsight,
    YieldTrendInsight
)

def test_format_historical_insights_empty():
    """Verify empty HistoricalInsightsContext does not crash and emits no block."""
    context = UnifiedContext(
        historical_insights=HistoricalInsightsContext()
    )
    result = format_context(context)

    assert result == ""
    assert "[HISTORICAL INSIGHTS]" not in result


def test_format_historical_insights_populated():
    """Verify populated HistoricalInsightsContext is serialized correctly."""
    insights = HistoricalInsightsContext(
        crop_performance=[
            CropPerformanceInsight(
                crop_name="Wheat",
                variety="HD-2967",
                seasons_observed=["Rabi 2025"],
                crops_observed=2,
                harvested_count=2,
                average_yield=200.5,
                yield_unit="kg",
                best_yield=210.0,
                worst_yield=190.0,
                disease_records=1,
                confidence=0.85
            )
        ],
        seasonal_performance=[
            SeasonalPerformanceInsight(
                season="Rabi",
                crops_observed=3,
                harvested_crops=2,
                average_yield=5.5,
                yield_unit="tons",
                confidence=0.9
            )
        ],
        disease_patterns=[
            DiseasePatternInsight(
                disease_name="Rust",
                affected_crop="Wheat",
                occurrence_count=3,
                resolved_count=2,
                active_count=1,
                common_severity="High",
                treatment_observed="Fungicide X",
                confidence=0.75
            )
        ],
        input_usage=[
            InputUsageInsight(
                input_type="Fertilizer",
                crop_name="Wheat",
                application_count=5,
                total_quantity=200.0,
                quantity_unit="liters",
                common_application_method="Spray",
                confidence=0.95
            )
        ],
        yield_trends=[
            YieldTrendInsight(
                crop_name="Wheat",
                yield_unit="kg",
                observations=5,
                average_yield=205.0,
                highest_yield=220.0,
                lowest_yield=190.0,
                trend_direction="Increasing",
                confidence=0.80
            )
        ]
    )

    context = UnifiedContext(historical_insights=insights)
    result = format_context(context)

    assert "[HISTORICAL INSIGHTS]" in result
    assert "[/HISTORICAL INSIGHTS]" in result

    # Crop performance & confidence
    assert "Crop Performance:" in result
    assert "- Wheat (HD-2967)" in result
    assert "Observed: 2 planted, 2 harvested" in result
    assert "Seasons: Rabi 2025" in result
    assert "Avg Yield: 200.5 kg" in result
    assert "Best Yield: 210.0 kg" in result
    assert "Worst Yield: 190.0 kg" in result
    assert "Disease Records: 1" in result
    assert "Confidence: 85%" in result

    # Seasonal performance & unit preservation
    assert "Seasonal Performance:" in result
    assert "- Season: Rabi" in result
    assert "Avg Yield: 5.5 tons" in result
    assert "Confidence: 90%" in result

    # Disease patterns
    assert "Disease Patterns:" in result
    assert "- Rust (on Wheat)" in result
    assert "Occurrences: 3 (2 resolved, 1 active)" in result
    assert "Common Severity: High" in result
    assert "Common Treatment: Fungicide X" in result
    assert "Confidence: 75%" in result

    # Input usage
    assert "Input Usage:" in result
    assert "- Fertilizer on Wheat" in result
    assert "Total Quantity: 200.0 liters" in result
    assert "Common Method: Spray" in result
    assert "Confidence: 95%" in result

    # Yield trends
    assert "Yield Trends:" in result
    assert "Trend: Increasing" in result
    assert "Observations: 5" in result
    assert "Avg: 205.0" in result
    assert "High: 220.0" in result
    assert "Confidence: 80%" in result


def test_format_historical_insights_coexistence():
    """Verify [HISTORICAL INSIGHTS] coexists safely with [FARM HISTORY]."""
    history_ctx = FarmHistoryContext(
        past_crops=[
            CropHistoryEntry(
                crop_name="Rice",
                season="Kharif",
                status="active"
            )
        ]
    )

    insights = HistoricalInsightsContext(
        crop_performance=[
            CropPerformanceInsight(
                crop_name="Rice",
                seasons_observed=["Kharif"],
                confidence=0.5
            )
        ]
    )

    context = UnifiedContext(
        history=history_ctx,
        historical_insights=insights
    )

    result = format_context(context)

    assert "[FARM HISTORY]" in result
    assert "- Rice | Season: Kharif" in result
    assert "[HISTORICAL INSIGHTS]" in result
    assert "- Rice" in result
    assert "Confidence: 50%" in result

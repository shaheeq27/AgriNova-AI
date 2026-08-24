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

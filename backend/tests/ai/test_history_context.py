"""
Tests for V4 Phase 1 Step 4 — AI History Context Schemas.
"""

from datetime import date
import pytest
from app.ai.schemas.context import CropHistoryEntry, FarmHistoryContext, UnifiedContext

def test_crop_history_entry_complete():
    entry = CropHistoryEntry(
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
    
    assert entry.crop_name == "Wheat"
    assert entry.variety == "HD-2967"
    assert entry.season == "Rabi"
    assert entry.planting_date == date(2025, 11, 1)
    assert entry.harvest_date == date(2026, 3, 15)
    assert entry.yield_amount == 200.0
    assert entry.yield_unit == "kg"
    assert entry.status == "harvested"
    assert entry.disease_count == 1
    assert entry.fertilizer_applications == 2
    assert entry.irrigation_applications == 3


def test_crop_history_entry_optional_fields():
    entry = CropHistoryEntry(
        crop_name="Rice",
        season="Kharif",
        status="active"
    )
    
    assert entry.variety is None
    assert entry.planting_date is None
    assert entry.harvest_date is None
    assert entry.yield_amount is None
    assert entry.yield_unit is None
    
    # Defaults
    assert entry.disease_count == 0
    assert entry.fertilizer_applications == 0
    assert entry.irrigation_applications == 0


def test_farm_history_context_accepts_multiple_entries():
    c1 = CropHistoryEntry(crop_name="Wheat", season="Rabi", status="harvested")
    c2 = CropHistoryEntry(crop_name="Rice", season="Kharif", status="active")
    
    history = FarmHistoryContext(
        past_crops=[c1, c2],
        recent_diseases=["Rust", "Blight"],
        seasonal_patterns=["High yield in Rabi"],
        performance_summary="Good performance overall"
    )
    
    assert len(history.past_crops) == 2
    assert history.past_crops[0].crop_name == "Wheat"
    assert len(history.recent_diseases) == 2
    assert len(history.seasonal_patterns) == 1
    assert history.performance_summary == "Good performance overall"


def test_farm_history_context_empty():
    history = FarmHistoryContext()
    
    assert history.past_crops == []
    assert history.recent_diseases == []
    assert history.seasonal_patterns == []
    assert history.performance_summary is None


def test_unified_context_without_history():
    context = UnifiedContext()
    assert context.history is None
    assert context.farm is None
    assert context.weather is None
    assert context.knowledge is None
    assert context.intelligence is None


def test_unified_context_with_history():
    c1 = CropHistoryEntry(crop_name="Wheat", season="Rabi", status="harvested")
    history = FarmHistoryContext(past_crops=[c1])
    
    context = UnifiedContext(history=history)
    assert context.history is not None
    assert len(context.history.past_crops) == 1
    assert context.history.past_crops[0].crop_name == "Wheat"
    
    # Verify serialization works correctly
    dumped = context.model_dump()
    assert dumped["history"]["past_crops"][0]["crop_name"] == "Wheat"

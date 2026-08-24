"""
Tests for HistoricalInsightsService and deterministic insight extraction.
"""

import pytest
from datetime import date
from app.ai.schemas.context import (
    FarmHistoryContext, 
    CropHistoryEntry,
    UnifiedContext,
)
from app.ai.services.historical_insights_service import HistoricalInsightsService
from app.ai.services.context_formatter import _format_historical_insights

def test_generate_insights_empty_history():
    service = HistoricalInsightsService()
    history = FarmHistoryContext()
    
    insights = service.generate_insights(history)
    
    assert not insights.successful_crops
    assert not insights.recurring_diseases
    assert not insights.seasonal_crop_patterns
    assert not insights.historical_yield_observations


def test_generate_insights_successful_crops():
    service = HistoricalInsightsService()
    history = FarmHistoryContext(
        past_crops=[
            # Harvested with yield -> successful
            CropHistoryEntry(crop_name="Wheat", variety="A", season="Rabi", status="harvested", yield_amount=100.0, yield_unit="kg"),
            # Active -> not successful
            CropHistoryEntry(crop_name="Rice", season="Kharif", status="active", yield_amount=0.0),
            # Harvested but no yield -> not successful
            CropHistoryEntry(crop_name="Maize", season="Kharif", status="harvested", yield_amount=None),
        ]
    )
    
    insights = service.generate_insights(history)
    
    assert insights.successful_crops == ["Wheat (A)"]


def test_generate_insights_recurring_diseases():
    service = HistoricalInsightsService()
    history = FarmHistoryContext(
        recent_diseases=[
            "Rust — high severity — resolved",
            "Blight — moderate severity",
            "Rust — low severity",
        ]
    )
    
    insights = service.generate_insights(history)
    
    # Rust appears twice, Blight appears once
    assert "Rust" in insights.recurring_diseases
    assert "Blight" not in insights.recurring_diseases


def test_generate_insights_yield_units_separated():
    service = HistoricalInsightsService()
    history = FarmHistoryContext(
        past_crops=[
            CropHistoryEntry(crop_name="Wheat", season="Rabi", status="harvested", yield_amount=200.0, yield_unit="kg"),
            CropHistoryEntry(crop_name="Wheat", season="Rabi", status="harvested", yield_amount=1.5, yield_unit="tons"),
            CropHistoryEntry(crop_name="Maize", season="Rabi", status="harvested", yield_amount=300.0, yield_unit="kg"),
        ]
    )
    
    insights = service.generate_insights(history)
    
    assert "Wheat: 200.0 kg, 1.5 tons" in insights.historical_yield_observations
    assert "Maize: 300.0 kg" in insights.historical_yield_observations


def test_generate_insights_seasonal_patterns():
    service = HistoricalInsightsService()
    history = FarmHistoryContext(
        seasonal_patterns=["Kharif: Rice", "Rabi: Wheat"]
    )
    
    insights = service.generate_insights(history)
    assert insights.seasonal_crop_patterns == ["Kharif: Rice", "Rabi: Wheat"]


def test_format_historical_insights():
    service = HistoricalInsightsService()
    history = FarmHistoryContext(
        past_crops=[
            CropHistoryEntry(crop_name="Wheat", variety="A", season="Rabi", status="harvested", yield_amount=100.0, yield_unit="kg"),
        ],
        recent_diseases=[
            "Rust — high severity",
            "Rust — low severity",
        ],
        seasonal_patterns=["Rabi: Wheat"]
    )
    
    insights = service.generate_insights(history)
    context = UnifiedContext(historical_insights=insights)
    
    formatted = _format_historical_insights(context)
    
    assert "[HISTORICAL INSIGHTS]" in formatted
    assert "Successfully Harvested Crops:" in formatted
    assert "Wheat (A)" in formatted
    assert "Recurring Diseases (Multiple Occurrences):" in formatted
    assert "Rust" in formatted
    assert "Observed Seasonal Patterns:" in formatted
    assert "Rabi: Wheat" in formatted
    assert "Historical Yield Observations:" in formatted
    assert "Wheat: 100.0 kg" in formatted


def test_format_historical_insights_empty():
    service = HistoricalInsightsService()
    history = FarmHistoryContext()
    
    insights = service.generate_insights(history)
    context = UnifiedContext(historical_insights=insights)
    
    formatted = _format_historical_insights(context)
    
    assert "[HISTORICAL INSIGHTS]" in formatted
    assert "No deterministic insights extracted from history." in formatted
    assert "Successfully Harvested Crops:" not in formatted

"""
Tests for V5.3.2 — Market Context Prompt Integration.
"""

from app.ai.prompts.system import AIRA_SYSTEM_PROMPT

def test_system_prompt_includes_market_safety_rules():
    """Verify that Aira is instructed not to fabricate prices."""
    assert "NEVER invent or estimate market prices" in AIRA_SYSTEM_PROMPT
    assert "do NOT fabricate one" in AIRA_SYSTEM_PROMPT
    assert "Do NOT use speculative future prices or attempt to forecast markets" in AIRA_SYSTEM_PROMPT

def test_system_prompt_includes_market_scope_boundaries():
    """Verify no V6-style prediction/forecasting behavior is introduced."""
    assert "Price prediction, market forecasting, or speculative future prices (state you cannot predict future markets)" in AIRA_SYSTEM_PROMPT
    assert "Profit optimization or selling-price recommendations based on future speculation" in AIRA_SYSTEM_PROMPT

def test_system_prompt_includes_market_grounding():
    """Verify Aira handles stale data and treats market context as relevant context."""
    assert "When [MARKET DATA] is available:" in AIRA_SYSTEM_PROMPT
    assert "Mention market information only when it genuinely helps" in AIRA_SYSTEM_PROMPT
    assert "prioritize farm/weather context over market prices" in AIRA_SYSTEM_PROMPT
    
    assert "When [MARKET DATA] is stale, cached, or unavailable:" in AIRA_SYSTEM_PROMPT
    assert "acknowledge the limitation" in AIRA_SYSTEM_PROMPT
    assert "Never present unavailable or stale information as current live data" in AIRA_SYSTEM_PROMPT

def test_system_prompt_includes_market_context_instructions():
    """Verify Market-aware instruction exists for the data block."""
    assert "Data between [MARKET DATA] and [/MARKET DATA] contains current market" in AIRA_SYSTEM_PROMPT
    assert "authoritative source for current market prices and price changes" in AIRA_SYSTEM_PROMPT

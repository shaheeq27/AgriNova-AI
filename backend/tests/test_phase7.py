"""
Unit tests for Phase 7 — Conversation History Management & Token Budget.
"""

from __future__ import annotations

import pytest

from app.ai.providers.base import AIMessage
from app.ai.services.ai_service import AIService
from app.ai.services.history_manager import _TRUNCATION_NOTE, HistoryManager
from app.ai.services.token_budget import (
    OUTPUT_RESERVE,
    PRACTICAL_CONTEXT_BUDGET,
    estimate_tokens,
)
from app.models.conversation import Message


def test_token_estimation():
    """Verify estimate_tokens heuristic."""
    assert estimate_tokens("") == 0
    assert estimate_tokens("hello") == int(len("hello") / 3.5 + 0.5)
    # Estimate of "A"*350 should be approx 100
    assert estimate_tokens("A" * 350) == 100


def test_turn_pair_building():
    """Verify turn-pair grouping logic."""
    m1 = Message(role="user", content="hello")
    m2 = Message(role="assistant", content="hi there")
    m3 = Message(role="user", content="next question")

    hm = HistoryManager()
    pairs = hm._build_turn_pairs([m1, m2, m3])
    assert len(pairs) == 2
    assert pairs[0] == (m1, m2)
    assert pairs[1] == (m3,)


def test_context_protection_sliding_window():
    """Verify that history gets truncated to fit within the budget."""
    messages = []
    # Create 5 turn pairs of ~100 characters each (~28 tokens per message)
    # Total per pair is ~57 tokens
    for i in range(5):
        messages.append(Message(role="user", content=f"user question {i} " + "A" * 100))
        messages.append(Message(role="assistant", content=f"assistant answer {i} " + "B" * 100))

    hm = HistoryManager()
    # Available budget: 150 tokens.
    # Truncation note ≈ 40 tokens.
    # Remaining: 110 tokens.
    # 1 pair ≈ 57 tokens. 2 pairs ≈ 114 tokens (exceeds 110).
    # So it should fit exactly 1 pair.
    selected = hm.fit_history(messages, available_tokens=150)
    assert len(selected) > 0
    assert selected[0].content == _TRUNCATION_NOTE
    # 1 truncation note + 1 pair (2 messages) = 3 messages total
    assert len(selected) == 3
    assert selected[1].role == "user"
    assert "user question 4" in selected[1].content


def test_minimum_history_fallback():
    """Verify that available budget is never exceeded, even for MIN_HISTORY_TURNS."""
    m1 = Message(role="user", content="A" * 100)  # ~29 tokens
    m2 = Message(role="assistant", content="B" * 100)  # ~29 tokens

    hm = HistoryManager()
    # Available history budget is 10 tokens (less than 1 pair)
    selected = hm.fit_history([m1, m2], available_tokens=10)
    assert len(selected) == 0  # Does not exceed budget, drops all history


def test_context_overflow():
    """Verify that if system content + context exceeds budget, history is 0."""
    new_user_message = "What should I do?"
    # Enormous context string (~18k tokens, exceeds PRACTICAL_CONTEXT_BUDGET=16,384)
    huge_context = "C" * 65000

    m1 = Message(role="user", content="older message")
    m2 = Message(role="assistant", content="older response")

    llm_messages = AIService._build_messages(
        existing_messages=[m1, m2],
        new_user_message=new_user_message,
        context_string=huge_context,
    )

    # Should contain exactly 2 messages: system prompt and current user message.
    # History is truncated to 0.
    assert len(llm_messages) == 2
    assert llm_messages[0].role == "system"
    assert huge_context in llm_messages[0].content
    assert llm_messages[1].role == "user"
    assert llm_messages[1].content == new_user_message


def test_model_independence():
    """Verify that model configuration in provider does not affect token_budget.py."""
    # Changing the Gemini model or configuration shouldn't modify these constants
    assert PRACTICAL_CONTEXT_BUDGET == 16384
    assert OUTPUT_RESERVE == 2048

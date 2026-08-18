"""
AgriNova AI — History Manager.

Manages conversation history to fit within the available token budget
using a sliding-window truncation strategy.

Priority order (context is PROTECTED, history is FLEXIBLE):
  1. Current user message
  2. Safety / system instructions
  3. Relevant farm context
  4. Relevant KB context
  5. Relevant intelligence outputs
  6. Recent conversation turns     ◀── managed here
  7. Old conversation turns        ◀── truncated first

Design principles:
  - History is the LAST thing allocated.  The caller calculates how
    many tokens remain after system + context + new message, and this
    module fits history into that budget.
  - Never splits a turn-pair (user message without its assistant
    response).
  - Never exceeds the available budget, even if ``MIN_HISTORY_TURNS``
    cannot be satisfied.
  - Does NOT use LLM-based summarization (no extra latency/cost).
  - Adds a transparency note when messages are dropped.
"""

from __future__ import annotations

import logging

from app.ai.providers.base import AIMessage
from app.ai.services.token_budget import MIN_HISTORY_TURNS, estimate_tokens

logger = logging.getLogger(__name__)

_TRUNCATION_NOTE = (
    "[Earlier messages in this conversation have been omitted for brevity. "
    "If you need to reference something from earlier, please ask.]"
)


class HistoryManager:
    """Fits conversation history within a token budget.

    Usage::

        hm = HistoryManager()
        history = hm.fit_history(existing_messages, available_tokens=3000)
    """

    def fit_history(
        self,
        messages: list,
        available_tokens: int,
    ) -> list[AIMessage]:
        """Select conversation messages that fit within the token budget.

        Args:
            messages: All existing messages for the conversation
                      (``Message`` ORM objects), ordered chronologically.
            available_tokens: Maximum token budget for history.

        Returns:
            List of ``AIMessage`` objects to include in the LLM request.
            May include a truncation note as the first message if older
            messages were dropped.
        """
        if not messages or available_tokens <= 0:
            return []

        # Build turn-pairs: [(user_msg, assistant_msg), ...]
        # Unpaired trailing messages are included as single-element tuples.
        turn_pairs = self._build_turn_pairs(messages)

        if not turn_pairs:
            return []

        # Work backwards from the most recent turn-pairs.
        # Add turns until the budget is exhausted.
        selected: list[tuple] = []
        tokens_used = 0
        truncation_note_tokens = estimate_tokens(_TRUNCATION_NOTE)

        for pair in reversed(turn_pairs):
            pair_tokens = sum(estimate_tokens(msg.content) for msg in pair)

            # If we've already selected some turns and adding this one
            # would exceed the budget, stop.
            # Reserve space for the truncation note if we'll be truncating.
            budget_for_check = available_tokens
            if selected:
                # We already have some turns — if we skip this one,
                # we need room for the truncation note.
                budget_for_check = available_tokens - truncation_note_tokens

            if tokens_used + pair_tokens > budget_for_check:
                break

            selected.append(pair)
            tokens_used += pair_tokens

        if not selected:
            # Budget too small for even the most recent turn-pair.
            # Try to fit just the last message (might be a single user msg).
            last_pair = turn_pairs[-1]
            last_tokens = sum(estimate_tokens(msg.content) for msg in last_pair)
            if last_tokens <= available_tokens:
                selected.append(last_pair)
            else:
                return []

        # Reverse back to chronological order
        selected.reverse()

        # Build the AIMessage list
        result: list[AIMessage] = []
        was_truncated = len(selected) < len(turn_pairs)

        if was_truncated:
            result.append(AIMessage(role="user", content=_TRUNCATION_NOTE))

        for pair in selected:
            for msg in pair:
                result.append(AIMessage(role=msg.role, content=msg.content))

        total_turns = len(turn_pairs)
        kept_turns = len(selected)

        if was_truncated:
            logger.info(
                "History truncated: kept %d/%d turn-pairs (~%d tokens, budget %d)",
                kept_turns, total_turns, tokens_used, available_tokens,
            )

        return result

    @staticmethod
    def _build_turn_pairs(messages: list) -> list[tuple]:
        """Group messages into (user, assistant) turn-pairs.

        Handles edge cases:
          - Trailing user message without a response → single-element tuple
          - Multiple consecutive same-role messages → grouped with the next
        """
        pairs: list[tuple] = []
        i = 0

        while i < len(messages):
            msg = messages[i]

            if msg.role == "user" and i + 1 < len(messages) and messages[i + 1].role == "assistant":
                # Normal turn-pair
                pairs.append((msg, messages[i + 1]))
                i += 2
            else:
                # Unpaired message (trailing user msg, or consecutive same-role)
                pairs.append((msg,))
                i += 1

        return pairs

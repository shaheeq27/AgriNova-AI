"""
AgriNova AI — Token Budget Constants & Estimator.

Provides a conservative token estimation heuristic and budget constants
for managing the AI request payload.

Design principles:
  - ``PRACTICAL_CONTEXT_BUDGET`` is AgriNova's self-imposed limit,
    NOT the provider's maximum context window.  We intentionally keep
    this smaller to control cost, latency, and response quality.
  - The character-based estimator is a conservative heuristic used
    only for local budget allocation.  It is NOT an exact billing
    or token-count mechanism.
  - History is the last thing allocated.  System prompt, farm context,
    knowledge, and intelligence always get their full space.
"""

from __future__ import annotations

# ── Budget Constants ─────────────────────────────────────────────────────────

# AgriNova's practical request budget.
# This is NOT the provider's maximum context window — it's a deliberate
# quality/cost ceiling.  The underlying model may support much more.
PRACTICAL_CONTEXT_BUDGET: int = 16_384

# Tokens reserved for the model's output response.
OUTPUT_RESERVE: int = 2_048

# Soft target for minimum recent history to include.
# This is a GOAL, not a guarantee — the token budget always wins.
# If the available history budget cannot fit even this many turn-pairs,
# we include as many as the budget allows (possibly zero).
MIN_HISTORY_TURNS: int = 2

# Characters per token — conservative heuristic (slightly overestimates).
_CHARS_PER_TOKEN: float = 3.5


# ── Token Estimator ─────────────────────────────────────────────────────────

def estimate_tokens(text: str) -> int:
    """Estimate token count using a character-based heuristic.

    Uses ``len(text) / 3.5`` which slightly overestimates to keep us
    safely within budget.  This is adequate for budget allocation but
    should not be used for exact billing.

    Args:
        text: The text to estimate.

    Returns:
        Estimated token count (always >= 1 for non-empty text).
    """
    if not text:
        return 0
    return max(1, int(len(text) / _CHARS_PER_TOKEN + 0.5))

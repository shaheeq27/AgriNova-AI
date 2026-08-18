"""
AgriNova AI — Intent Router.

Lightweight, deterministic intent detection for engine selection.
Uses keyword matching to determine which intelligence engines are
relevant to the user's question.

No LLM call — this is a pure rules engine.

Capabilities:
  - irrigation: watering, irrigation, water schedule
  - fertilizer: fertilizer, nutrient, manure, NPK
  - disease: disease symptoms described by user
  - timeline: growth stage, progress, timeline, harvest date
  - general: no specific engine needed
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ── Keyword Sets ─────────────────────────────────────────────────────────────

_IRRIGATION_KEYWORDS = frozenset([
    "irrigat", "water", "watering", "drip", "sprinkler", "flood",
    "moisture", "dry", "drought", "rain enough", "should i water",
    "how much water",
])

_FERTILIZER_KEYWORDS = frozenset([
    "fertiliz", "fertilis", "nutrient", "manure", "compost",
    "npk", "urea", "potash", "phosphat", "nitrogen",
    "feeding", "feed the", "soil amendment", "how much fertilizer",
])

_DISEASE_KEYWORDS = frozenset([
    "disease", "blight", "wilt", "rot", "fungus", "fungal",
    "pest", "insect", "aphid", "mite", "caterpillar",
    "spots", "yellow", "brown", "curling", "wilting", "dying",
    "infected", "infection", "symptom", "sick", "unhealthy",
    "lesion", "mold", "mould", "rust",
])

_TIMELINE_KEYWORDS = frozenset([
    "timeline", "growth stage", "stage", "progress", "harvest",
    "when to harvest", "how long", "schedule", "what stage",
    "current stage", "maturity", "flowering", "germination",
    "vegetative", "fruiting",
])


# ── Intent Result ────────────────────────────────────────────────────────────

@dataclass
class IntentResult:
    """Which engines should be invoked for this user message.

    Multiple capabilities can be True simultaneously.
    For example: "Should I water or fertilize my tomato?" → both.
    """

    irrigation: bool = False
    fertilizer: bool = False
    disease: bool = False
    timeline: bool = False
    symptoms: list[str] = field(default_factory=list)

    @property
    def any_engine(self) -> bool:
        """True if at least one engine should be invoked."""
        return self.irrigation or self.fertilizer or self.disease or self.timeline


# ── Router ───────────────────────────────────────────────────────────────────

def detect_intent(message: str) -> IntentResult:
    """Detect which engines are relevant to the user's message.

    Uses substring matching against keyword sets.  This is intentionally
    simple — a false positive (calling an extra engine) is cheap and
    harmless, while a false negative (missing an engine) degrades the
    response quality.

    Args:
        message: The user's raw message text.

    Returns:
        ``IntentResult`` with boolean flags per engine capability.
    """
    lower = message.lower()
    result = IntentResult()

    # Check each capability
    for keyword in _IRRIGATION_KEYWORDS:
        if keyword in lower:
            result.irrigation = True
            break

    for keyword in _FERTILIZER_KEYWORDS:
        if keyword in lower:
            result.fertilizer = True
            break

    for keyword in _DISEASE_KEYWORDS:
        if keyword in lower:
            result.disease = True
            break

    for keyword in _TIMELINE_KEYWORDS:
        if keyword in lower:
            result.timeline = True
            break

    # Extract symptoms for disease detection
    if result.disease:
        result.symptoms = _extract_symptoms(lower)

    return result


def _extract_symptoms(text: str) -> list[str]:
    """Extract symptom phrases from the user's message.

    Uses a simple approach: look for known symptom indicators.
    The disease engine uses Jaccard similarity, so even rough
    extraction helps matching.
    """
    symptom_indicators = [
        "yellow spots", "brown spots", "black spots", "white spots",
        "yellow leaves", "brown leaves", "wilting", "curling",
        "leaf curl", "leaf drop", "stunted growth", "rotting",
        "mold", "mould", "powdery", "lesions", "holes",
        "dying leaves", "drooping", "discoloration",
        "yellowing", "browning", "drying", "withering",
    ]

    found = []
    for symptom in symptom_indicators:
        if symptom in text:
            found.append(symptom)

    # If no known indicators found but disease intent detected,
    # return the whole message as a single symptom string
    # so the engine can still attempt matching.
    if not found:
        # Clean up the message to a rough symptom description
        found = [text.strip()[:200]]

    return found

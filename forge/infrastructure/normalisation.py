"""Text normalisation utilities for Gherkin parsing."""

# Keyword mapping: raw Gherkin keywords → canonical form
STEP_KEYWORD_MAP = {
    "given": "Given",
    "when": "When",
    "then": "Then",
    "and": "And",
    "but": "But",
    "*": "*",
    # Also handle capitalized variants
    "Given": "Given",
    "When": "When",
    "Then": "Then",
    "And": "And",
    "But": "But",
}


def _norm(text: str) -> str:
    """Normalize text: lowercase and strip whitespace."""
    return text.lower().strip()

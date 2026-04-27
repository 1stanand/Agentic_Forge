"""Screen context inference for Gherkin steps.

Detects navigation anchor steps (e.g., "user navigates to Collateral screen")
and propagates the inferred screen name forward through subsequent steps.
"""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Anchor detection patterns - applied to lowercased step text
_ANCHOR_PATTERNS = [
    # "user opens the collateral screen"
    re.compile(r'\bopens?\s+(?:the\s+)?(.+?)(?:\s+(?:screen|page|tab|accordion|drawer))?\s*$', re.IGNORECASE),
    # "user navigates to the KYC screen"
    re.compile(r'\bnavigates?\s+to\s+(?:the\s+)?(.+?)(?:\s+(?:screen|page|tab|accordion|drawer))?\s*$', re.IGNORECASE),
    # "user moves to the next stage"
    re.compile(r'\bmoves?\s+to\s+(?:the\s+)?(.+?)(?:\s+(?:screen|page|tab|accordion|drawer))?\s*$', re.IGNORECASE),
    # "user selects the Documents tab"
    re.compile(r'\bselects?\s+(?:the\s+)?(.+?)\s+(?:tab|accordion|drawer|screen|page)\s*$', re.IGNORECASE),
    # "user clicks on the Collateral tab"
    re.compile(r'\bclicks?\s+on\s+(?:the\s+)?(.+?)\s+(?:tab|accordion|drawer|screen|page)\s*$', re.IGNORECASE),
    # "user is on the Recommendation screen"
    re.compile(r'\bis\s+on\s+(?:the\s+)?(.+?)(?:\s+(?:screen|page|tab|accordion|drawer))?\s*$', re.IGNORECASE),
]

# Phrases that look like navigation but are NOT screens
_IGNORE_PHRASES = {
    "next stage", "next", "previous stage", "back", "home", "dashboard",
}

# LogicalID prerequisite marker - never treat as navigation
_LOGICAL_ID_PREFIX = "all prerequisite are performed"


def _norm(text: str) -> str:
    """Normalize text: lowercase and strip."""
    return text.lower().strip()


def build_screen_name_map() -> dict:
    """Build SCREEN_NAME_MAP dynamically from unique_steps.

    This runs after each ingest to discover new screen names in the repo.
    Returns {normalized_phrase: canonical_screen_name}.
    """
    try:
        from forge.core.db import get_conn, get_cursor, release_conn

        screen_map = {}
        conn = get_conn()
        try:
            with get_cursor(conn) as cur:
                # Fetch all unique step texts
                cur.execute("SELECT DISTINCT step_text FROM unique_steps WHERE step_text IS NOT NULL")
                for row in cur.fetchall():
                    text = row["step_text"]
                    phrase = _extract_anchor_phrase(text)
                    if phrase:
                        norm_phrase = _norm(phrase)
                        # Use the original phrase as the canonical screen name
                        if norm_phrase not in screen_map:
                            screen_map[norm_phrase] = phrase
        finally:
            release_conn(conn)

        logger.info(f"Built dynamic SCREEN_NAME_MAP with {len(screen_map)} screens")
        return screen_map
    except Exception as e:
        logger.warning(f"Could not build dynamic SCREEN_NAME_MAP: {e}")
        return {}


# Global cache for SCREEN_NAME_MAP (built on first use)
_screen_name_map_cache = None


def get_screen_name_map() -> dict:
    """Get SCREEN_NAME_MAP (cached on first use)."""
    global _screen_name_map_cache
    if _screen_name_map_cache is None:
        _screen_name_map_cache = build_screen_name_map()
    return _screen_name_map_cache


def _extract_anchor_phrase(step_text: str) -> Optional[str]:
    """Extract screen-name phrase from a navigation anchor step."""
    lower = step_text.lower().strip()

    # Skip LogicalID prerequisite steps
    if _LOGICAL_ID_PREFIX in lower:
        return None

    for pattern in _ANCHOR_PATTERNS:
        m = pattern.search(lower)
        if m:
            phrase = m.group(1).strip()
            # Skip short or ignorable phrases
            if len(phrase) < 3:
                continue
            if _norm(phrase) in _IGNORE_PHRASES:
                continue
            return phrase

    return None


def resolve_screen(raw_phrase: str) -> Optional[str]:
    """Look up a raw phrase in SCREEN_NAME_MAP."""
    screen_map = get_screen_name_map()
    key = _norm(raw_phrase)
    return screen_map.get(key)


def infer_screen_contexts(steps: list) -> list:
    """Populate screen_context for all steps by detecting navigation anchors.

    Mutates steps in-place and returns the list.
    """
    if not steps:
        return steps

    current_screen = None

    for step in steps:
        text = step.get("step_text", "")
        phrase = _extract_anchor_phrase(text)

        if phrase is not None:
            resolved = resolve_screen(phrase)
            if resolved is not None:
                current_screen = resolved

        # Propagate current_screen to this step
        step["screen_context"] = current_screen

    return steps


def infer_screen_contexts_strict(steps: list) -> list:
    """Like infer_screen_contexts but only set screen_context on explicit anchors."""
    if not steps:
        return steps

    for step in steps:
        text = step.get("step_text", "")
        phrase = _extract_anchor_phrase(text)

        if phrase is not None:
            resolved = resolve_screen(phrase)
            step["screen_context"] = resolved
        else:
            step["screen_context"] = None

    return steps

"""
JIRA client for fetching stories in two modes: CSV export or PAT (API token).

CSV mode: Parse JIRA CSV exports and extract business-relevant fields.
PAT mode: Fetch story directly from JIRA API using PAT token.

Both modes return the same ParsedStory structure with quality tracking.
"""

import logging
import csv
import re
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field

from forge.core.config import get_settings
from forge.api.auth import decrypt_pat

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Data Model
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class ParsedStory:
    """Parsed JIRA story with quality tracking."""
    issue_key: str
    summary: str
    issue_type: str
    description: str
    legacy_process: str = ""
    system_process: str = ""
    business_scenarios: str = ""
    impacted_areas: str = ""
    key_ui_steps: str = ""
    acceptance_criteria: str = ""
    story_description: str = ""
    supplemental_comments: str = ""
    raw_labels: List[str] = field(default_factory=list)

    # Quality tracking
    parse_quality: str = "unknown"  # "excellent", "good", "fair", "poor"
    missing_fields: List[str] = field(default_factory=list)  # Empty required fields


# ═══════════════════════════════════════════════════════════════════════════════
# CSV Column Names (from JIRA HD Bank export)
# ═══════════════════════════════════════════════════════════════════════════════

_COL_SUMMARY = "Summary"
_COL_KEY = "Issue key"
_COL_TYPE = "Issue Type"
_COL_DESCRIPTION = "Description"
_COL_LABELS = "Labels"
_COL_SYSTEM_PROCESS = "Custom field (System processes)"
_COL_BIZ_SCENARIOS = "Custom field (Business scenarios: Exceptions)"
_COL_BIZ_VALIDATION = "Custom field (Business scenarios: Validations and corner cases)"
_COL_IMPACTED = "Custom field (Impacted Areas/Functionalities)"
_COL_KEY_UI = "Custom field (Key UI steps)"
_COL_ACCEPTANCE = "Custom field (Acceptance Criteria)"
_COL_ACCEPTANCE_ALT = "Custom field (Acceptance)"
_COL_STORY_DESC = "Custom field (Story Description)"

_COMMENT_FIELD_HINTS = (
    "comment",
    "comments from",
    "review comments",
    "assignee's comments",
    "approach",
)


# ═══════════════════════════════════════════════════════════════════════════════
# Text Cleaning & Processing
# ═══════════════════════════════════════════════════════════════════════════════

def _clean(text: str) -> str:
    """Strip JIRA wiki markup and return plain text."""
    if not text:
        return ""

    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')

    # Remove JIRA macros and markup
    text = re.sub(r'\{color[^}]*\}', '', text)  # {color:#hex}text{color}
    text = re.sub(r'\{-\}([^{]*)\{-\}', r'\1', text)  # {-}text{-}
    text = re.sub(r'\{\^?\~?\}([^{]*)\{\^?\~?\}', r'\1', text)  # {^}text{^} / {~}text{~}
    text = re.sub(r'\*\+([^+]+)\+\*', r'\1', text)  # *+text+*
    text = re.sub(r'\+\*+([^*]+)\*+\+', r'\1', text)  # +*text*+
    text = re.sub(r'\*([^*\n]+)\*', r'\1', text)  # *text*
    text = re.sub(r'\+([^+\n]+)\+', r'\1', text)  # +text+
    text = re.sub(r'_([^_\n]+)_', r'\1', text)  # _text_
    text = re.sub(r'\[([^\|\]]+)\|[^\]]+\]', r'\1', text)  # [label|url]
    text = re.sub(r'\[([^\]]+)\]', r'\1', text)  # [label]

    # Table conversions
    text = re.sub(r'^\|\|(.+?)\|\|$',
                  lambda m: ' | '.join(c.strip() for c in m.group(1).split('||')),
                  text, flags=re.MULTILINE)
    text = re.sub(r'^\|(.+?)\|$',
                  lambda m: ' | '.join(c.strip() for c in m.group(1).split('|') if c.strip()),
                  text, flags=re.MULTILINE)

    # Remove emoticons, rules, headings
    text = re.sub(r'\([/\\xX!\*\?]\)', '', text)  # (/) (x) (!) etc.
    text = re.sub(r'^-{4,}$', '', text, flags=re.MULTILINE)  # ----
    text = re.sub(r'^h[1-6]\.\s*', '', text, flags=re.MULTILINE)  # h1. h2.
    text = re.sub(r'^[#\*]+\s+', '- ', text, flags=re.MULTILINE)  # bullet marks

    # Remove code/noformat blocks (contain implementation, not behavior)
    text = re.sub(r'\{code[^}]*\}.*?\{code\}', '', text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r'\{noformat[^}]*\}.*?\{noformat\}', '', text, flags=re.DOTALL | re.IGNORECASE)

    # Keep content of quote/panel blocks, strip wrappers
    text = re.sub(r'\{(?:quote|panel)[^}]*\}(.*?)\{(?:quote|panel)\}', r'\1', text, flags=re.DOTALL)

    # Remove remaining macro tags
    text = re.sub(r'\{[a-zA-Z][^}]*\}', '', text)

    # Collapse excess whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()


def _split_process(raw: str) -> tuple[str, str]:
    """Split 'System processes' field into (legacy_process, system_process)."""
    text = _clean(raw)
    lower = text.lower()

    new_idx = lower.find("new process")
    if new_idx == -1:
        current_idx = lower.find("current process")
        if current_idx == -1:
            return "", text
        body = text[current_idx:]
        body = re.sub(r'^current process[:\-\s]+', '', body, flags=re.I).strip()
        return body, ""

    current_raw = text[:new_idx]
    new_raw = text[new_idx:]

    current_raw = re.sub(r'^current process[:\-\s]+', '', current_raw, flags=re.I).strip()
    new_raw = re.sub(r'^new process[:\-\s]+', '', new_raw, flags=re.I).strip()

    return current_raw, new_raw


def _get(row: dict, *keys: str) -> str:
    """Return first non-empty value for any of the given column names."""
    for k in keys:
        v = row.get(k, "").strip()
        if v:
            return v
    return ""


# ═══════════════════════════════════════════════════════════════════════════════
# CSV Parsing
# ═══════════════════════════════════════════════════════════════════════════════

def _iter_csv_rows(csv_text: str):
    """Iterate CSV text and yield row dicts."""
    lines = csv_text.split('\n')
    reader = csv.DictReader(lines)
    for row in reader:
        if row and any(row.values()):  # Skip empty rows
            yield {k: v.strip() if v else "" for k, v in row.items()}


def _looks_like_useful_comment(text: str) -> bool:
    """Check if text is a useful business comment (not noise)."""
    lowered = text.lower()

    # Must have sufficient words
    if len(re.findall(r"[a-z0-9]+", lowered)) < 6:
        return False

    # Must contain business keywords
    if not re.search(
        r"\b(should|must|will|logic|rule|approach|decision|verdict|status|stage|field|column|"
        r"checkbox|dropdown|screen|grid|move|display|enable|disable|validation|approval)\b",
        lowered
    ):
        return False

    # Exclude status-only comments
    if re.search(r"\b(done|completed|not applicable|review pending|atdd|cw|ut|qa|dev complete)\b", lowered):
        if not re.search(r"\b(should|must|will|rule|logic|approach)\b", lowered):
            return False

    return True


def _collect_supplemental_comments(row: dict) -> str:
    """Extract useful comments from comment fields."""
    values = []
    for key in row.keys():
        if any(hint in key.lower() for hint in _COMMENT_FIELD_HINTS):
            cleaned = _clean(row.get(key, ""))
            if cleaned:
                for chunk in re.split(r"\n{2,}", cleaned):
                    part = chunk.strip()
                    if part and _looks_like_useful_comment(part):
                        values.append(part)
    return "\n\n".join(values)


def parse_csv(csv_raw: str) -> ParsedStory:
    """Parse JIRA CSV export and extract first story."""
    try:
        rows = list(_iter_csv_rows(csv_raw))
        if not rows:
            raise ValueError("No rows found in CSV")

        # Use first data row (skip header)
        row = rows[0]

        # Extract fields
        current, new = _split_process(_get(row, _COL_SYSTEM_PROCESS))
        biz = "\n".join(filter(None, [
            _clean(_get(row, _COL_BIZ_SCENARIOS)),
            _clean(_get(row, _COL_BIZ_VALIDATION)),
        ])).strip()

        labels_raw = _get(row, _COL_LABELS)
        labels = [l.strip() for l in labels_raw.split(",") if l.strip()]

        story = ParsedStory(
            issue_key=_get(row, _COL_KEY),
            summary=_clean(_get(row, _COL_SUMMARY)),
            issue_type=_get(row, _COL_TYPE),
            description=_clean(_get(row, _COL_DESCRIPTION)),
            legacy_process=current,
            system_process=new,
            business_scenarios=biz,
            impacted_areas=_clean(_get(row, _COL_IMPACTED)),
            key_ui_steps=_clean(_get(row, _COL_KEY_UI)),
            acceptance_criteria=_clean(_get(row, _COL_ACCEPTANCE, _COL_ACCEPTANCE_ALT)),
            story_description=_clean(_get(row, _COL_STORY_DESC)),
            supplemental_comments=_collect_supplemental_comments(row),
            raw_labels=labels,
        )

        # Assess quality
        missing = []
        if not story.summary:
            missing.append("summary")
        if not story.system_process and not story.description:
            missing.append("system_process or description")
        if not story.acceptance_criteria:
            missing.append("acceptance_criteria")

        if len(missing) >= 2:
            story.parse_quality = "poor"
        elif len(missing) == 1:
            story.parse_quality = "fair"
        elif story.supplemental_comments and story.business_scenarios:
            story.parse_quality = "excellent"
        else:
            story.parse_quality = "good"

        story.missing_fields = missing
        logger.info(f"Parsed CSV: {story.issue_key} — quality={story.parse_quality}, missing={missing}")

        return story

    except Exception as e:
        logger.error(f"CSV parsing error: {e}")
        raise


# ═══════════════════════════════════════════════════════════════════════════════
# PAT Mode (API Token)
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_via_pat(story_id: str, pat: str, jira_url: str) -> ParsedStory:
    """Fetch story from JIRA using PAT token (API authentication)."""
    try:
        from jira import JIRA
    except ImportError:
        raise ImportError("jira-python library required for PAT mode. Install: pip install jira")

    try:
        # Initialize JIRA client with PAT
        client = JIRA(server=jira_url, token_auth=pat)

        # Fetch issue with all fields
        issue = client.issue(
            story_id,
            fields="*all",
            expand="changelog"
        )

        # Extract fields using JIRA API field names
        story = ParsedStory(
            issue_key=issue.key,
            summary=issue.fields.summary or "",
            issue_type=issue.fields.issuetype.name if issue.fields.issuetype else "",
            description=_clean(issue.fields.description or ""),
            raw_labels=[label.name for label in (issue.fields.labels or [])],
        )

        # Try to extract custom fields (field names vary by instance)
        custom_field_map = {
            "system_process": ["System processes", "customfield_10050", "customfield_10048"],
            "business_scenarios": ["Business scenarios: Exceptions", "customfield_10051"],
            "acceptance_criteria": ["Acceptance Criteria", "Acceptance", "customfield_10052"],
            "story_description": ["Story Description", "customfield_10053"],
            "impacted_areas": ["Impacted Areas", "customfield_10054"],
            "key_ui_steps": ["Key UI steps", "customfield_10055"],
        }

        for field_attr, possible_names in custom_field_map.items():
            for name in possible_names:
                value = getattr(issue.fields, name, None) if hasattr(issue.fields, name) else None
                if value:
                    setattr(story, field_attr, _clean(str(value)))
                    break

        # Collect comments for supplemental info
        comments = []
        if hasattr(issue.fields, "comment") and issue.fields.comment:
            for comment in issue.fields.comment.comments:
                text = _clean(comment.body)
                if text and _looks_like_useful_comment(text):
                    comments.append(text)
        story.supplemental_comments = "\n\n".join(comments)

        # Assess quality
        missing = []
        if not story.summary:
            missing.append("summary")
        if not story.system_process and not story.description:
            missing.append("system_process or description")
        if not story.acceptance_criteria:
            missing.append("acceptance_criteria")

        if len(missing) >= 2:
            story.parse_quality = "poor"
        elif len(missing) == 1:
            story.parse_quality = "fair"
        elif story.supplemental_comments and story.business_scenarios:
            story.parse_quality = "excellent"
        else:
            story.parse_quality = "good"

        story.missing_fields = missing
        logger.info(f"Fetched via PAT: {story.issue_key} — quality={story.parse_quality}, missing={missing}")

        return story

    except Exception as e:
        logger.error(f"PAT fetch error for {story_id}: {e}")
        raise


# ═══════════════════════════════════════════════════════════════════════════════
# Public API - Smart Mode Selection
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_story(
    jira_input_mode: str,
    jira_story_id: Optional[str] = None,
    jira_csv_raw: Optional[str] = None,
    jira_pat_override: Optional[str] = None,
) -> ParsedStory:
    """Fetch story in CSV or PAT mode with automatic PAT precedence.

    PAT precedence (highest to lowest):
    1. jira_pat_override from request
    2. encrypted user PAT from user_settings (requires user context)
    3. JIRA_PAT from environment (.env)

    Args:
        jira_input_mode: "csv" or "pat"
        jira_story_id: Required for PAT mode
        jira_csv_raw: Required for CSV mode
        jira_pat_override: Optional PAT to override environment

    Returns:
        ParsedStory with parse_quality and missing_fields
    """
    settings = get_settings()

    if jira_input_mode == "csv":
        if not jira_csv_raw:
            raise ValueError("CSV mode requires jira_csv_raw")
        return parse_csv(jira_csv_raw)

    elif jira_input_mode == "pat":
        if not jira_story_id:
            raise ValueError("PAT mode requires jira_story_id")

        # Determine which PAT to use (precedence)
        pat = jira_pat_override or settings.jira_pat
        if not pat:
            raise ValueError("No JIRA PAT available (set JIRA_PAT env var or provide jira_pat_override)")

        # Decrypt if it's encrypted
        if pat.startswith("gAAAAA"):  # Fernet encrypted prefix
            try:
                pat = decrypt_pat(pat)
            except Exception:
                # If decrypt fails, assume it's plaintext
                pass

        if not settings.jira_url:
            raise ValueError("JIRA_URL not configured")

        return fetch_via_pat(jira_story_id, pat, settings.jira_url)

    else:
        raise ValueError(f"Unknown jira_input_mode: {jira_input_mode}")

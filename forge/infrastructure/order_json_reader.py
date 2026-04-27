import json
import logging
from pathlib import Path

from forge.core.config import get_settings

logger = logging.getLogger(__name__)

_order_json = None


def load_order_json() -> dict:
    """Load order.json workflow specification."""
    global _order_json
    if _order_json is None:
        settings = get_settings()
        order_path = Path(settings.order_json_path)

        if not order_path.exists():
            logger.warning(f"order.json not found at {order_path}")
            return {"workflow": []}

        with open(order_path, 'r') as f:
            _order_json = json.load(f)

    return _order_json


def match_tags(effective_tags: list) -> str:
    """Match effective tag set against order.json expressions."""
    order_data = load_order_json()
    workflow = order_data.get("WorkFlow", [])

    tag_set = set(tag.lower() for tag in effective_tags)

    for expression in workflow:
        if _match_expression(expression, tag_set):
            return expression

    return None


def _match_expression(expr: str, tags: set) -> bool:
    """Match a single boolean expression against tag set."""
    # Simple expression matching: @tag, @tag AND @other, @tag AND NOT @other
    expr_lower = expr.lower()

    # Remove @ symbols for simpler matching
    tags_normalized = {tag.replace('@', '').lower() for tag in tags}

    # Split on AND and NOT
    parts = expr_lower.replace(' and ', '|').replace(' not ', '~').split('|')

    for part in parts:
        part = part.strip()
        if part.startswith('~'):
            tag = part[1:].strip().replace('@', '')
            if tag in tags_normalized:
                return False
        else:
            tag = part.strip().replace('@', '')
            if tag not in tags_normalized:
                return False

    return True


def detect_stage(query: str) -> str:
    """Detect stage from query text using @Tag matching."""
    order_data = load_order_json()
    stages = ['@Lead', '@CCDE', '@KYC', '@DDE', '@CreditApproval', '@Disbursal']

    query_lower = query.lower()
    for stage in stages:
        if stage.lower() in query_lower:
            return stage

    return None

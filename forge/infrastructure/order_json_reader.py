import json
import logging
import re
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
    """Match a single boolean expression against tag set using proper evaluation."""
    # Normalize tags: remove @ and lowercase
    tags_normalized = {tag.replace('@', '').lower() for tag in tags}

    # Build Python-safe expression by replacing tag references with boolean checks
    expr_eval = expr.lower()

    # Find all @tags and replace with boolean expressions
    for tag in re.findall(r'@?\w+', expr):
        tag_clean = tag.replace('@', '')
        is_present = tag_clean in tags_normalized
        expr_eval = re.sub(r'@?' + re.escape(tag_clean) + r'\b', str(is_present), expr_eval, flags=re.IGNORECASE)

    # Convert AND/OR/NOT to Python operators
    expr_eval = re.sub(r'\band\b', ' and ', expr_eval, flags=re.IGNORECASE)
    expr_eval = re.sub(r'\bor\b', ' or ', expr_eval, flags=re.IGNORECASE)
    expr_eval = re.sub(r'\bnot\b', ' not ', expr_eval, flags=re.IGNORECASE)

    try:
        result = eval(expr_eval, {"__builtins__": {}})
        return bool(result)
    except Exception as e:
        logger.warning(f"Failed to evaluate Order.json expression '{expr}': {e}")
        return False


def detect_stage(query: str) -> str:
    """Detect stage from query text using @Tag matching."""
    order_data = load_order_json()
    stages = ['@Lead', '@CCDE', '@KYC', '@DDE', '@CreditApproval', '@Disbursal']

    query_lower = query.lower()
    for stage in stages:
        if stage.lower() in query_lower:
            return stage

    return None

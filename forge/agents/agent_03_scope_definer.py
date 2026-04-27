"""
Agent 03 — Scope Definer

Defines story scope from JIRA facts. Scope = what JIRA explicitly introduces.
Ambient scope (existing content) gets light touch only — conservative.

Input: jira_facts, domain_brief
Output: scope (dict with explicit vs ambient)
"""

import json
import logging

from forge.core.state import ForgeState
from forge.core.llm import llm_complete, LLMNotLoadedError

logger = logging.getLogger(__name__)

AGENT_03_SYSTEM_PROMPT = """You are the Scope Definer for Forge Agentic.

Your job: Define what this story EXPLICITLY changes vs. what's ambient (existing, not in scope).

## Hard Rule
Ambiguous → Conservative. Only scope what JIRA explicitly mentions. Do not invent scope.

## Output
{
  "explicit_scope": ["List of features/changes JIRA explicitly introduces"],
  "new_fields": ["Field1", "Field2"],
  "modified_rules": ["Rule1", "Rule2"],
  "affected_workflows": ["Workflow1"],
  "ambient_scope": ["Existing content that touches this story but isn't being changed"],
  "scope_confidence": 0.0 to 1.0,
  "assumptions": "Any [ASSUMED] scope decisions"
}

Respond with ONLY valid JSON.
"""

def agent_03_scope_definer(state: ForgeState) -> ForgeState:
    """Define story scope from JIRA facts and domain context."""

    logger.info("=" * 80)
    logger.info("AGENT 03 — SCOPE DEFINER")
    logger.info("=" * 80)

    try:
        jira_facts = state['jira_facts'] or {}
        domain_brief = state['domain_brief'] or {}

        logger.info(f"Story: {jira_facts.get('issue_key', 'UNKNOWN')}")
        logger.info(f"Explicit intent: {jira_facts.get('overall_intent', '')[:80]}")

        # Build LLM input
        llm_input = f"""Story: {jira_facts.get('issue_key')}
Summary: {jira_facts.get('summary')}

Explicit Target State: {jira_facts.get('target_state')}
Acceptance Criteria: {jira_facts.get('acceptance_criteria_raw')}
Business Scenarios: {jira_facts.get('business_scenarios')}

Domain Context:
{json.dumps(domain_brief.get('domain_context', {}), indent=2)[:500]}

Define scope: what does JIRA explicitly change?
Only scope what JIRA says. Be conservative on ambiguous items.
Mark assumptions with [ASSUMED].
"""

        logger.debug(f"LLM input size: {len(llm_input)} chars")

        # Call LLM
        try:
            response = llm_complete(
                prompt=llm_input,
                system=AGENT_03_SYSTEM_PROMPT,
                max_tokens=800
            )
            logger.info(f"LLM response: {len(response)} chars")

        except LLMNotLoadedError:
            logger.error("LLM not loaded")
            raise

        # Parse JSON
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            scope = json.loads(json_str)
            logger.info(f"Parsed scope: {len(scope.get('explicit_scope', []))} explicit items")

        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            raise

        # Update state
        state['scope'] = scope

        logger.info("=" * 80)
        logger.info("AGENT 03 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 03 EXCEPTION: {type(e).__name__}: {e}")
        raise

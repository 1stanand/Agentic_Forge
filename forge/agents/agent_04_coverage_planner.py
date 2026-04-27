"""
Agent 04 — Coverage Planner

Plans complete coverage based on story scope + domain knowledge.
Assigns LogicalIDs, determines thread count for ordered flows, detects gaps.

Input: jira_facts, domain_brief, scope, flow_type
Output: coverage_plan
"""

import json
import logging

from forge.core.state import ForgeState
from forge.core.llm import llm_complete, LLMNotLoadedError

logger = logging.getLogger(__name__)

AGENT_04_SYSTEM_PROMPT = """You are the Coverage Planner for Forge Agentic.

Your job: Plan complete test coverage for this story. Identify all intents/outcomes.
For ordered flows: Assign LogicalIDs and determine thread count.

## LogicalID Format
CAS_{storyID}_{outcome}
Example: CAS_256008_APPROVE (storyID from issue key)

## For Ordered Flows
- Determine how many parallel threads (journeys)
- Assign each scenario a unique LogicalID
- Identify dependencies between threads
- Plan execution order

## For Unordered Flows
- Each scenario is independent
- LogicalID still assigned for traceability
- No cross-scenario dependencies

## Output
{
  "issue_key": "CAS-XXXXX",
  "flow_type": "ordered | unordered",
  "coverage_intents": [
    {
      "intent": "Happy path: Approve application",
      "logical_id": "CAS_256008_APPROVE",
      "thread": 1,
      "triggers": "Conditions that trigger this intent",
      "outcomes": ["Approval decision recorded", "System transitions to next stage"]
    }
  ],
  "thread_count": 1,
  "coverage_gaps": ["Gap 1", "Gap 2"],
  "dependencies": "How scenarios depend on each other (ordered flows only)",
  "coverage_confidence": 0.0 to 1.0
}

Respond with ONLY valid JSON.
"""

def agent_04_coverage_planner(state: ForgeState) -> ForgeState:
    """Plan coverage: intents, LogicalIDs, thread count, gaps."""

    logger.info("=" * 80)
    logger.info("AGENT 04 — COVERAGE PLANNER")
    logger.info("=" * 80)

    try:
        jira_facts = state['jira_facts'] or {}
        domain_brief = state['domain_brief'] or {}
        scope = state['scope'] or {}
        flow_type = state['flow_type'] or "unordered"

        issue_key = jira_facts.get("issue_key", "UNKNOWN")
        logger.info(f"Story: {issue_key}, Flow: {flow_type}")
        logger.info(f"Explicit scope items: {len(scope.get('explicit_scope', []))}")

        # Build LLM input
        llm_input = f"""Story: {issue_key}
Flow Type: {flow_type}
Summary: {jira_facts.get('summary')}

Explicit Scope:
{json.dumps(scope.get('explicit_scope', []), indent=2)[:300]}

Business Scenarios:
{jira_facts.get('business_scenarios', '')}

Domain Context (screens/stages):
{', '.join(domain_brief.get('domain_context', {}).get('screens_involved', []))} screens
{', '.join(domain_brief.get('domain_context', {}).get('stages_involved', []))} stages

Plan coverage:
- What are all possible intents/outcomes?
- For {flow_type} flow, assign LogicalIDs
- Identify coverage gaps (what's NOT explicitly tested)
- For ordered: how many threads needed?
"""

        logger.debug(f"LLM input: {len(llm_input)} chars")

        try:
            response = llm_complete(
                prompt=llm_input,
                system=AGENT_04_SYSTEM_PROMPT,
                max_tokens=1200
            )
            logger.info(f"LLM response: {len(response)} chars")

        except LLMNotLoadedError:
            logger.error("LLM not loaded")
            raise

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            coverage_plan = json.loads(json_str)

            logger.info(f"Coverage plan: {len(coverage_plan.get('coverage_intents', []))} intents, "
                       f"threads={coverage_plan.get('thread_count')}, "
                       f"gaps={len(coverage_plan.get('coverage_gaps', []))}")

        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            raise

        state['coverage_plan'] = coverage_plan

        logger.info("=" * 80)
        logger.info("AGENT 04 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 04 EXCEPTION: {type(e).__name__}: {e}")
        raise

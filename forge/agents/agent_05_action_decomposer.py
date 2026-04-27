"""
Agent 05 — Action Decomposer (CAS Specific)

Translates coverage intents into CAS tester actions using repo vocabulary.
Hard constraints: then[] max 2, no But keyword, ordered: first Given = prerequisite.

Input: coverage_plan, domain_brief, flow_type
Output: action_sequences (dict of intents -> Given/When/Then actions)
"""

import json
import logging

from forge.core.state import ForgeState
from forge.core.llm import llm_complete, LLMNotLoadedError

logger = logging.getLogger(__name__)

AGENT_05_SYSTEM_PROMPT = """You are the Action Decomposer for Forge Agentic — CAS specific.

Your job: Translate each coverage intent into BDD actions using CAS tester vocabulary.

## HARD CONSTRAINTS — NO EXCEPTIONS

1. **Then block max 2 items:** One "Then" + one "And" maximum. No more.
   BAD:  Then X  And Y  And Z
   GOOD: Then X  And Y

2. **Never use "But" keyword.** Period. NOT EVEN ONCE.
   - Check every step for " But " or starts with "But "
   - If found, reject that action sequence
   - BAD:  Then X  But Y
   - GOOD: Then X  (remove But, restructure as separate scenario)

3. **For ordered flows:** First Given = exact prerequisite step text from repo.
   Use EXACT step text from previous scenario, do NOT paraphrase.

## CAS Action Vocabulary

Use these action verbs (from CAS repo):
- Click, Select, Enter, Navigate, Verify, Validate, Approve, Reject, Submit
- Example: "User clicks Apply button", "System displays Recommendation screen"

## Output

{
  "issue_key": "CAS-XXXXX",
  "flow_type": "ordered | unordered",
  "action_sequences": {
    "LogicalID_1": {
      "intent": "Happy path: Approve application",
      "given_steps": ["Given user is on CAS Login Page", "Given user navigates to Credit Approval stage"],
      "when_steps": ["When user selects Approval checkbox", "When user clicks Submit"],
      "then_steps": ["Then system displays Approval Confirmation", "And approval decision is recorded in database"]
    }
  },
  "validation_errors": ["Any hard constraint violations found"],
  "action_confidence": 0.0 to 1.0
}

IMPORTANT:
- given_steps: list (can be multiple Given steps)
- when_steps: list (can be multiple When steps)
- then_steps: list with MAXIMUM 2 ITEMS (one Then + one And)
- No But anywhere
- For ordered flows: first Given must be exact prerequisite step text

Respond with ONLY valid JSON.
"""

def agent_05_action_decomposer(state: ForgeState) -> ForgeState:
    """Decompose coverage intents into CAS actions with hard constraints."""

    logger.info("=" * 80)
    logger.info("AGENT 05 — ACTION DECOMPOSER (CAS SPECIFIC)")
    logger.info("=" * 80)

    try:
        coverage_plan = state['coverage_plan'] or {}
        domain_brief = state['domain_brief'] or {}
        flow_type = state['flow_type'] or "unordered"
        jira_facts = state['jira_facts'] or {}

        issue_key = jira_facts.get("issue_key", "UNKNOWN")
        logger.info(f"Story: {issue_key}, Flow: {flow_type}")

        intents = coverage_plan.get("coverage_intents", [])
        logger.info(f"Decomposing {len(intents)} intents into CAS actions")

        # Build LLM input
        intent_text = json.dumps(intents[:3], indent=2)  # First 3 intents

        llm_input = f"""Story: {issue_key}
Flow Type: {flow_type}

Coverage Intents to Decompose:
{intent_text}

Domain Context (CAS screens/entities):
{json.dumps(domain_brief.get('domain_context', {}).get('entities_and_rules', {}), indent=2)[:300]}

Decompose each intent into Given/When/Then actions:
- Use CAS tester vocabulary (Click, Select, Enter, Verify, Approve, etc.)
- Hard rules: Then max 2 items, no But, no more than 2 conditions
- For {flow_type}: structure appropriately
- Validate against hard constraints
"""

        logger.debug(f"LLM input: {len(llm_input)} chars")

        try:
            response = llm_complete(
                prompt=llm_input,
                system=AGENT_05_SYSTEM_PROMPT,
                max_tokens=1500
            )
            logger.info(f"LLM response: {len(response)} chars")

        except LLMNotLoadedError:
            logger.error("LLM not loaded")
            raise

        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            action_sequences = json.loads(json_str)

            # Validate hard constraints — hard fail if violations found
            errors = action_sequences.get("validation_errors", [])
            if errors:
                logger.error(f"Validation errors detected: {errors}")
                raise ValueError(f"Agent 05: Action decomposition validation failed: {errors}")

            # Validate "But" keyword hard ban
            for seq_id, seq in action_sequences.get("action_sequences", {}).items():
                all_steps = seq.get("given_steps", []) + seq.get("when_steps", []) + seq.get("then_steps", [])
                for step in all_steps:
                    if " But " in step or step.startswith("But "):
                        raise ValueError(f"Agent 05: Sequence {seq_id} contains forbidden 'But' keyword: {step}")

            # For ordered flows: prepend mandatory prerequisite step
            if flow_type == "ordered":
                for seq_id, seq in action_sequences.get("action_sequences", {}).items():
                    given_steps = seq.get("given_steps", [])
                    # Prepend prerequisite if not already present
                    prerequisite = "Given all prerequisite are performed in previous scenario"
                    if given_steps and not given_steps[0].startswith("Given all prerequisite"):
                        seq["given_steps"] = [prerequisite] + given_steps
                    elif not given_steps:
                        seq["given_steps"] = [prerequisite]
                    logger.debug(f"{seq_id}: Prepended prerequisite step")

            logger.info(f"Decomposed {len(action_sequences.get('action_sequences', {}))} action sequences")

        except Exception as e:
            logger.error(f"JSON parse error: {e}")
            raise

        state['action_sequences'] = action_sequences

        logger.info("=" * 80)
        logger.info("AGENT 05 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 05 EXCEPTION: {type(e).__name__}: {e}")
        raise

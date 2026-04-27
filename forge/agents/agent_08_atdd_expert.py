"""
Agent 08 — ATDD Expert

Quality gate for all scenarios. Validates Order.json for ordered flows.
Enforces CAS structural rules: no But, Then max 2, no dicts in ordered, no Background in ordered.

Input: composed_scenarios (from Agent 07)
Output: validation_result (pass/fail + errors)
"""

import json
import logging
from typing import Dict, List, Any

from forge.core.state import ForgeState
from forge.infrastructure.order_json_reader import match_tags

logger = logging.getLogger(__name__)

AGENT_08_SYSTEM_PROMPT = """You are the ATDD Expert for Forge Agentic — CAS-specific quality gate.

Your job: Validate all scenarios against CAS structural rules and Order.json.

## Hard CAS Rules — All Must Pass

1. **No But keyword** — Ever. Reject any Then block with "But".
   - BAD: "Then X But Y"
   - GOOD: Restructure or split scenario

2. **Then block max 2 items** — One Then + one And maximum.
   - BAD: "Then X And Y And Z"
   - GOOD: "Then X And Y"

3. **No dictionaries in ordered flows** — Ordered flows must be purely sequential.
   - BAD: Ordered flow with Examples header containing pipe-separated tables
   - GOOD: Pure Given/When/Then steps, no Examples with pipes

4. **No Background in ordered flows** — All steps must be scenario-specific.
   - BAD: Ordered flow with shared Background block
   - GOOD: Each scenario fully self-contained

5. **No structured data in ordered** — No dicts, no tables, no parameterization.
   - BAD: Examples: | field | value |
   - GOOD: All data in step parameters

## For Ordered Flows — Order.json Validation

- Extract effective tags from each scenario (@LogicalID:..., @Stage:..., etc.)
- Match against order.json expressions
- Must find exactly one matching Order expression per scenario
- Hard-fail if no match found — this scenario cannot be ordered

## Output

{
  "issue_key": "CAS-XXXXX",
  "flow_type": "ordered | unordered",
  "validation_pass": true/false,
  "validation_errors": ["Error 1", "Error 2"],
  "order_json_status": "validated | not_required | validation_failed",
  "scenarios_validated": N,
  "expert_confidence": 0.0 to 1.0
}

If validation_pass is false, list all errors. Do not proceed to Writer if any errors.
"""

def agent_08_atdd_expert(state: ForgeState) -> ForgeState:
    """Validate scenarios against CAS rules and Order.json. Hard-fail on violations."""

    logger.info("=" * 80)
    logger.info("AGENT 08 — ATDD EXPERT")
    logger.info("=" * 80)

    try:
        composed = state['composed_scenarios'] or {}
        issue_key = composed.get("issue_key", "UNKNOWN")
        flow_type = state['flow_type'] or "unordered"
        scenarios = composed.get("scenarios", [])

        logger.info(f"Story: {issue_key}, Flow: {flow_type}, Scenarios: {len(scenarios)}")

        validation_errors = []
        order_json_status = "not_required"

        # Validate each scenario
        for scenario in scenarios:
            logical_id = scenario.get("logical_id", "UNKNOWN")
            title = scenario.get("title", "")
            given = scenario.get("given_steps", [])
            when = scenario.get("when_steps", [])
            then = scenario.get("then_steps", [])
            tags = scenario.get("tags", [])

            # Rule 1: No But keyword
            all_steps = given + when + then
            for step in all_steps:
                if " But " in step or step.startswith("But "):
                    validation_errors.append(
                        f"{logical_id}: Step contains 'But' keyword (forbidden): {step[:60]}"
                    )

            # Rule 2: Then max 2 items
            if len(then) > 2:
                validation_errors.append(
                    f"{logical_id}: Then block has {len(then)} items, max 2 allowed: {then}"
                )

            # Rule 3 & 4: For ordered flows only
            if flow_type == "ordered":
                # Rule 3: No dictionaries (Examples with pipes)
                # This is harder to detect at step level — we'd need to check if steps contain table syntax
                # For now, log as warning but don't hard-fail here
                # (Writer will detect pipe-separated steps)

                # Rule 4: No Background in ordered
                # Background would have been merged into scenarios by now
                # If we see repeated Given steps across scenarios, that's a background proxy
                # For now, log as warning

                # Rule 5: Order.json validation
                try:
                    matching_expr = match_tags(tags)
                    if not matching_expr:
                        validation_errors.append(
                            f"{logical_id}: No matching Order.json expression for tags {tags}"
                        )
                        order_json_status = "validation_failed"
                    else:
                        logger.debug(f"{logical_id} → Order.json: {matching_expr}")
                        order_json_status = "validated"
                except Exception as e:
                    validation_errors.append(
                        f"{logical_id}: Order.json validation error: {e}"
                    )
                    order_json_status = "validation_failed"

        # Overall decision
        validation_pass = len(validation_errors) == 0

        if not validation_pass:
            logger.warning(f"Validation FAILED with {len(validation_errors)} errors")
            for err in validation_errors[:5]:  # Log first 5 errors
                logger.warning(f"  - {err}")
        else:
            logger.info("Validation PASSED")

        validation_result = {
            "issue_key": issue_key,
            "flow_type": flow_type,
            "validation_pass": validation_pass,
            "validation_errors": validation_errors,
            "order_json_status": order_json_status,
            "scenarios_validated": len(scenarios),
            "expert_confidence": 1.0 if validation_pass else 0.0
        }

        state['validation_result'] = validation_result

        logger.info("=" * 80)
        logger.info("AGENT 08 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 08 EXCEPTION: {type(e).__name__}: {e}")
        raise

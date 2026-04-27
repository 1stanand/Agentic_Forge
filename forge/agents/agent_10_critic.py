"""
Agent 10 — Critic

Reviews generated .feature file and decides on loop-back to Composer.
Hard constraint: maximum one loop via is_second_pass flag.

Input: feature_file (from Agent 09)
Output: critic_review (decision: loop_back true/false, feedback)
"""

import json
import logging
from typing import Dict, List, Any

from forge.core.state import ForgeState
from forge.core.llm import llm_complete, LLMNotLoadedError

logger = logging.getLogger(__name__)

AGENT_10_SYSTEM_PROMPT = """You are the Critic for Forge Agentic — final quality review before output.

Your job: Review the .feature file. Decide: loop back to Composer or proceed to Reporter?

## Review Checklist

1. **Scenario titles** — Are they behavior-descriptive? Not just screen names?
   - GOOD: "User approves application and system records decision"
   - BAD: "Credit Approval Screen Happy Path"

2. **Marker presence** — Are markers present on lower-quality steps?
   - [NEW_STEP_NOT_IN_REPO], [LOW_MATCH], [ROLE_GAP] should appear if retrieved steps had confidence issues
   - Missing markers on weak steps = problem (signal quality lost)

3. **Step count per scenario** — Too few or too many?
   - Too few (1-2 steps total): Might be under-specified, consider expanding
   - Too many (>15 steps): Scenario is too complex, should split (but only if within scope)

4. **Logical consistency** — Do Given→When→Then flow logically?
   - Each When should follow naturally from Given
   - Each Then should be a natural result of When

5. **Ordered flow specifics** — If ordered:
   - LogicalID present in title? ✓
   - @OrderedFlow tag present? ✓
   - No dictionaries/Examples with tables? ✓
   - Prerequisite step is first Given? ✓

## Loop-Back Decision

- If ANY of the above 1-5 has a CRITICAL issue → `loop_back: true`
- If quality is acceptable → `loop_back: false` → proceed to Reporter

**HARD RULE: Only one loop allowed.**
If this is a second pass (`is_second_pass=true`), set `loop_back: false` unconditionally.

## Output

{
  "issue_key": "CAS-XXXXX",
  "review_findings": ["Finding 1", "Finding 2"],
  "quality_score": 0.0 to 1.0,
  "loop_back": true/false,
  "feedback": "Why loop back or why proceed",
  "critic_confidence": 0.0 to 1.0
}
"""

def agent_10_critic(state: ForgeState) -> ForgeState:
    """Review feature file and decide on loop-back. Max 1 loop enforced."""

    logger.info("=" * 80)
    logger.info("AGENT 10 — CRITIC")
    logger.info("=" * 80)

    try:
        feature_output = state['feature_file'] or {}
        issue_key = feature_output.get("issue_key", "UNKNOWN")
        feature_file = feature_output.get("feature_file", "")
        scenarios_count = feature_output.get("scenarios_rendered", 0)
        flow_type = state['flow_type'] or "unordered"

        # Check if this is second pass
        is_second_pass = state['is_second_pass'] if hasattr(state, 'is_second_pass') else False

        logger.info(f"Story: {issue_key}, Flow: {flow_type}, Scenarios: {scenarios_count}, Second pass: {is_second_pass}")

        # Build LLM input for review
        llm_input = f"""Story: {issue_key}
Flow Type: {flow_type}
Scenario Count: {scenarios_count}

Feature File (first 1500 chars):
{feature_file[:1500]}

Review this feature file:
1. Are scenario titles behavior-descriptive (not just screen names)?
2. Are markers ([NEW_STEP_NOT_IN_REPO], [LOW_MATCH], [ROLE_GAP]) present where needed?
3. Is step count reasonable (not too sparse, not too verbose)?
4. Does Given→When→Then logic flow naturally?
5. For ordered flows: LogicalID in title? @OrderedFlow tag? Prerequisites correct?

Provide findings and suggest: should we loop back to refine, or proceed to Reporter?
Respond with JSON only.
"""

        logger.debug(f"LLM input: {len(llm_input)} chars")

        try:
            response = llm_complete(
                prompt=llm_input,
                system=AGENT_10_SYSTEM_PROMPT,
                max_tokens=1000
            )
            logger.info(f"LLM response: {len(response)} chars")

        except LLMNotLoadedError:
            logger.error("LLM not loaded, proceeding without review")
            # If LLM unavailable, proceed to Reporter
            review = {
                "issue_key": issue_key,
                "review_findings": ["LLM not available for review"],
                "quality_score": 0.7,
                "loop_back": False,
                "feedback": "LLM unavailable; proceeding to Reporter",
                "critic_confidence": 0.0
            }
            state['critic_review'] = review
            logger.info("=" * 80)
            logger.info("AGENT 10 — COMPLETE (LLM fallback)")
            logger.info("=" * 80)
            return state

        # Parse LLM response
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            review = json.loads(json_str)
        except Exception as e:
            logger.warning(f"Critic review parse failed: {e}, using safe defaults")
            review = {
                "issue_key": issue_key,
                "review_findings": [f"Review parsing failed: {e}"],
                "quality_score": 0.5,
                "loop_back": False,
                "feedback": "Review parse failed, proceeding conservatively",
                "critic_confidence": 0.0
            }

        # HARD RULE: is_second_pass enforces no second loop
        if is_second_pass:
            logger.warning("Second pass detected — forcing loop_back=False (no third loop allowed)")
            review["loop_back"] = False
            review["feedback"] = "Second pass: loop-back hard-stopped, proceeding to Reporter"
            review["critic_confidence"] = 0.5

        # Log decision
        decision = "LOOP BACK to Composer" if review.get("loop_back") else "PROCEED to Reporter"
        logger.info(f"Critic decision: {decision} (quality={review.get('quality_score', 0):.2f})")

        state['critic_review'] = review

        logger.info("=" * 80)
        logger.info("AGENT 10 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 10 EXCEPTION: {type(e).__name__}: {e}")
        raise

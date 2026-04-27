"""
Agent 07 — Composer

Composes BDD scenarios from action sequences and retrieved steps.
Creates behavior-descriptive titles (not stage labels).
Preserves all markers through to final output.

Input: action_sequences (with retrieved_steps from Agent 06)
Output: scenarios (list with titles, steps, tags, markers)
"""

import json
import logging
from typing import Dict, List, Any

from forge.core.state import ForgeState
from forge.core.llm import llm_complete, LLMNotLoadedError

logger = logging.getLogger(__name__)

AGENT_07_SYSTEM_PROMPT = """You are the Composer for Forge Agentic.

Your job: Compose Gherkin scenarios from actions and retrieved steps.
Create behavior-descriptive titles (what the user achieves, not which screen).

## Scenario Naming Rules

Unordered flow:
- Title: Descriptive of outcome/behavior
- Example: "User approves application successfully"
- Example: "System rejects invalid collateral"

Ordered flow:
- Title: LogicalID : behavior description
- Format: "CAS_256008_APPROVE : User approves application and system records decision"
- Include LogicalID for traceability

## Step Composition Process

For each scenario:
1. Use retrieved_steps: match Given → best repo step (highest ce_score)
2. Preserve marker if present: [NEW_STEP_NOT_IN_REPO], [LOW_MATCH], [ROLE_GAP]
3. Compose final step text: "Given {repo_step_text} {marker_if_present}"
4. Repeat for When and Then
5. Collect all step texts with markers

## Markers Travel Intact

If a retrieved step has marker, include it on the final step:
- "Given user is on Login page [NEW_STEP_NOT_IN_REPO]"
- "When user submits form [LOW_MATCH]"
- "Then system displays error [ROLE_GAP]"

Never drop markers. They indicate step quality.

## Output

{
  "issue_key": "CAS-XXXXX",
  "flow_type": "ordered | unordered",
  "scenarios": [
    {
      "logical_id": "CAS_256008_APPROVE",
      "title": "User approves application and system records decision",
      "tags": ["@CAS-256008", "@OrderedFlow", "@LogicalID:CAS_256008_APPROVE"],
      "given_steps": [
        "Given user is on Credit Approval screen",
        "Given user has selected applicant record"
      ],
      "when_steps": [
        "When user clicks Approve button [LOW_MATCH]",
        "When user confirms decision"
      ],
      "then_steps": [
        "Then system displays approval confirmation",
        "And system records decision in database [NEW_STEP_NOT_IN_REPO]"
      ],
      "markers": ["[LOW_MATCH]", "[NEW_STEP_NOT_IN_REPO]"]
    }
  ],
  "composition_confidence": 0.0 to 1.0
}

IMPORTANT:
- Markers must be preserved on the steps that have them
- Extract unique markers list for scenario metadata
- Behavior-descriptive titles are critical for CAS readability
- For ordered: always include LogicalID in title and tags
"""

def agent_07_composer(state: ForgeState) -> ForgeState:
    """Compose scenarios with behavior-descriptive titles. Preserve markers."""

    logger.info("=" * 80)
    logger.info("AGENT 07 — COMPOSER")
    logger.info("=" * 80)

    try:
        retrieved_steps = state['retrieved_steps'] or {}
        issue_key = retrieved_steps.get("issue_key", "UNKNOWN")
        action_sequences = retrieved_steps.get("action_sequences", {})
        flow_type = state['flow_type'] or "unordered"

        logger.info(f"Story: {issue_key}, Flow: {flow_type}, Sequences: {len(action_sequences)}")

        # Build LLM input for title generation + marker preservation
        seq_summaries = []
        for logical_id, seq_data in action_sequences.items():
            intent = seq_data.get("intent", "")
            given = seq_data.get("given_steps", [])
            when = seq_data.get("when_steps", [])
            then = seq_data.get("then_steps", [])

            summary = f"""
LogicalID: {logical_id}
Intent: {intent}
Given ({len(given)}): {given[:1]}
When ({len(when)}): {when[:1]}
Then ({len(then)}): {then[:1]}
"""
            seq_summaries.append(summary)

        llm_input = f"""Story: {issue_key}
Flow Type: {flow_type}

Scenarios to compose:
{''.join(seq_summaries[:3])}

For each scenario:
1. Create a behavior-descriptive title (not a screen name)
2. Title format for ordered flow: "LogicalID : behavior description"
3. Title format for unordered: "behavior description"
4. Keep titles clear, business-focused, concise

Respond with JSON only.
"""

        logger.debug(f"LLM input: {len(llm_input)} chars")

        try:
            response = llm_complete(
                prompt=llm_input,
                system=AGENT_07_SYSTEM_PROMPT,
                max_tokens=1000
            )
            logger.info(f"LLM response: {len(response)} chars")

        except LLMNotLoadedError:
            logger.error("LLM not loaded")
            raise

        # Parse LLM response for titles
        try:
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            json_str = response[json_start:json_end]
            title_map = json.loads(json_str)
        except Exception as e:
            logger.warning(f"LLM title parse failed: {e}, using default titles")
            title_map = {}

        # Convert scenarios list to dict keyed by logical_id
        scenarios_raw = title_map.get("scenarios", [])
        if isinstance(scenarios_raw, list):
            llm_titles = {s.get("logical_id"): s.get("title") for s in scenarios_raw if s.get("logical_id")}
        else:
            llm_titles = scenarios_raw if isinstance(scenarios_raw, dict) else {}

        # Compose scenarios
        scenarios = []
        all_markers = set()

        for logical_id, seq_data in action_sequences.items():
            intent = seq_data.get("intent", "")
            given_actions = seq_data.get("given_steps", [])
            when_actions = seq_data.get("when_steps", [])
            then_actions = seq_data.get("then_steps", [])
            retrieved_dict = seq_data.get("retrieved_steps", {})

            # Get title from LLM or use fallback
            title = llm_titles.get(logical_id)
            if not title:
                if flow_type == "ordered":
                    title = f"{logical_id} : {intent[:50]}"
                else:
                    title = intent or "Unnamed scenario"

            # Compose steps with markers
            final_given = []
            final_when = []
            final_then = []
            markers_in_scenario = []

            # Process Given
            for action in given_actions:
                candidates = retrieved_dict.get(action, [])
                if candidates:
                    top = candidates[0]
                    step_text = top.get("step_text", action)
                    marker = top.get("marker")
                    if marker:
                        step_text = f"{step_text} {marker}"
                        markers_in_scenario.append(marker)
                        all_markers.add(marker)
                    final_given.append(step_text)
                else:
                    final_given.append(action)

            # Process When
            for action in when_actions:
                candidates = retrieved_dict.get(action, [])
                if candidates:
                    top = candidates[0]
                    step_text = top.get("step_text", action)
                    marker = top.get("marker")
                    if marker:
                        step_text = f"{step_text} {marker}"
                        markers_in_scenario.append(marker)
                        all_markers.add(marker)
                    final_when.append(step_text)
                else:
                    final_when.append(action)

            # Process Then
            for action in then_actions:
                candidates = retrieved_dict.get(action, [])
                if candidates:
                    top = candidates[0]
                    step_text = top.get("step_text", action)
                    marker = top.get("marker")
                    if marker:
                        step_text = f"{step_text} {marker}"
                        markers_in_scenario.append(marker)
                        all_markers.add(marker)
                    final_then.append(step_text)
                else:
                    final_then.append(action)

            # Build tags
            tags = [f"@{issue_key}"]
            if flow_type == "ordered":
                tags.append("@OrderedFlow")
                tags.append(f"@LogicalID:{logical_id}")
            else:
                tags.append("@UnorderedFlow")

            scenario = {
                "logical_id": logical_id,
                "title": title,
                "tags": tags,
                "given_steps": final_given,
                "when_steps": final_when,
                "then_steps": final_then,
                "markers": list(set(markers_in_scenario))  # unique markers in this scenario
            }

            scenarios.append(scenario)
            logger.debug(f"Composed scenario: {logical_id} with {len(final_given)}G {len(final_when)}W {len(final_then)}T")

        composition_confidence = 1.0 if scenarios else 0.0

        composed_output = {
            "issue_key": issue_key,
            "flow_type": flow_type,
            "scenarios": scenarios,
            "all_markers": list(all_markers),
            "composition_confidence": composition_confidence
        }

        logger.info(f"Composed {len(scenarios)} scenarios, markers: {len(all_markers)}")

        state['composed_scenarios'] = composed_output

        logger.info("=" * 80)
        logger.info("AGENT 07 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 07 EXCEPTION: {type(e).__name__}: {e}")
        raise

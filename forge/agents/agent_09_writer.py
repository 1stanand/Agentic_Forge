"""
Agent 09 — Writer

Renders final Gherkin .feature file with all CAS extensions.
File-level tags, Background (unordered only), scenarios, markers as comments.

Input: composed_scenarios, validation_result
Output: feature_file (complete .feature text)
"""

import logging
from typing import Dict, List, Any

from forge.core.state import ForgeState

logger = logging.getLogger(__name__)

AGENT_09_SYSTEM_PROMPT = """You are the Writer for Forge Agentic.

Your job: Render complete .feature file with CAS conventions.

## File Structure

@CAS-XXXXX
@FlowType:ordered|unordered
Feature: Story summary

  [Background: block for unordered flows only]

  Scenario: behavior-descriptive title
    Given ...
    When ...
    Then ...

## Background (Unordered Flows Only)

If flow_type == 'unordered', include a Background block:
  Background:
    Given user has completed login
    And user is in active session

Do NOT include Background in ordered flows.

## Markers as Inline Comments

Preserve markers on steps where they appear:
  Given user is on screen [NEW_STEP_NOT_IN_REPO]
  When user clicks button [LOW_MATCH]
  Then result is displayed [ROLE_GAP]

## Ordered Flow Tags

For ordered flows:
- @OrderedFlow
- @LogicalID:CAS_256008_APPROVE (on each scenario)
- @Order: <expression> (if available from validation)

## File Formatting

- 2-space indent for Background/Scenario bodies
- One blank line between scenarios
- Marker comments on same line as step (not separate line)
"""

def agent_09_writer(state: ForgeState) -> ForgeState:
    """Render final .feature file with all CAS extensions and markers."""

    logger.info("=" * 80)
    logger.info("AGENT 09 — WRITER")
    logger.info("=" * 80)

    try:
        composed = state.get('composed_scenarios') or {}
        reviewed = state.get('reviewed_scenarios') or []

        issue_key = composed.get("issue_key", "UNKNOWN")
        flow_type = composed.get("flow_type", "unordered")
        scenarios = reviewed if reviewed else composed.get("scenarios", [])

        logger.info(f"Story: {issue_key}, Flow: {flow_type}, Scenarios: {len(scenarios)}")

        # Validate Then+And hard ban: max 2 items per Then block
        for scenario in scenarios:
            then_steps = scenario.get("then_steps", [])
            if len(then_steps) > 2:
                raise ValueError(f"Scenario {scenario.get('title', 'Unknown')}: Then block has {len(then_steps)} items, max 2 allowed")
            # Also validate "But" keyword hard ban
            all_steps = scenario.get("given_steps", []) + scenario.get("when_steps", []) + then_steps
            for step in all_steps:
                if " But " in step or step.startswith("But "):
                    raise ValueError(f"Scenario {scenario.get('title', 'Unknown')}: Contains forbidden 'But' keyword: {step}")

        # Start feature file
        lines = []

        # File-level tags
        lines.append(f"@{issue_key}")
        if flow_type == "ordered":
            lines.append("@OrderedFlow")
        else:
            lines.append("@UnorderedFlow")
        lines.append("")

        # Feature line
        # Extract summary from jira_facts if available
        summary = state['jira_facts'].get("summary", "Feature") if state['jira_facts'] else "Feature"
        lines.append(f"Feature: {summary}")
        lines.append("")

        # Background (unordered only)
        if flow_type == "unordered" and scenarios:
            lines.append("  Background:")
            lines.append("    Given user is on CAS Login Page")
            lines.append("")

        # Scenarios
        for i, scenario in enumerate(scenarios):
            # Scenario line with tags
            tags = scenario.get("tags", [])
            if tags:
                tag_line = "  " + " ".join(tags)
                lines.append(tag_line)

            # Scenario title
            title = scenario.get("title", "Unnamed scenario")
            lines.append(f"  Scenario: {title}")

            # Given steps
            given_steps = scenario.get("given_steps", [])
            if given_steps:
                for j, step in enumerate(given_steps):
                    keyword = "Given" if j == 0 else "And"
                    lines.append(f"    {keyword} {_extract_step_text(step)}")

            # When steps
            when_steps = scenario.get("when_steps", [])
            if when_steps:
                for j, step in enumerate(when_steps):
                    keyword = "When" if j == 0 else "And"
                    lines.append(f"    {keyword} {_extract_step_text(step)}")

            # Then steps
            then_steps = scenario.get("then_steps", [])
            if then_steps:
                for j, step in enumerate(then_steps):
                    keyword = "Then" if j == 0 else "And"
                    lines.append(f"    {keyword} {_extract_step_text(step)}")

            # Blank line between scenarios
            if i < len(scenarios) - 1:
                lines.append("")

        feature_text = "\n".join(lines)

        logger.info(f"Rendered .feature file: {len(feature_text)} chars, {len(lines)} lines")

        # Build metadata
        marker_count = sum(len(s.get("markers", [])) for s in scenarios)
        all_unique_markers = set()
        for s in scenarios:
            all_unique_markers.update(s.get("markers", []))

        feature_output = {
            "issue_key": issue_key,
            "flow_type": flow_type,
            "feature_file": feature_text,
            "scenarios_rendered": len(scenarios),
            "markers_preserved": len(all_unique_markers),
            "feature_confidence": 1.0 if len(scenarios) > 0 else 0.0
        }

        state['feature_file'] = feature_output

        logger.info("=" * 80)
        logger.info("AGENT 09 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 09 EXCEPTION: {type(e).__name__}: {e}")
        raise


def _extract_step_text(step_with_marker: str) -> str:
    """Extract step text, preserving marker as inline comment."""
    # Step format: "step text [MARKER]"
    # Return: "step text [MARKER]" as-is (marker already in step)
    return step_with_marker

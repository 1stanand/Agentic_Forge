"""
Agent 01 — Reader

Reads JIRA content (CSV export or PAT fetch) and assembles complete business facts.
Handles messy CAS JIRAs: missing acceptance criteria, scattered content, custom fields.

Input: jira_input_mode, JIRA content (CSV raw or story_id), three_amigos_notes
Output: jira_facts (comprehensive story assembly)
"""

import json
import logging
from typing import Optional

from forge.core.state import ForgeState
from forge.core.llm import llm_complete, LLMNotLoadedError
from forge.infrastructure.jira_client import fetch_story

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_01_SYSTEM_PROMPT = """You are the JIRA Reader for Forge Agentic — a specialized agent for assembling complete business facts from CAS (Core Application Suite) JIRA stories.

## YOUR ROLE

You receive raw JIRA data (parsed from CSV export or JIRA API). Your job is to synthesize this into a coherent narrative that downstream agents can understand and act on.

## WHAT YOU RECEIVE

1. **JIRA Story Fields** (from CSV or API):
   - Summary, Description
   - System Process (current/new), Business Scenarios
   - Acceptance Criteria (if present)
   - Key UI Steps, Impacted Areas
   - Story Description (custom field)
   - Supplemental Comments (from comments/review)
   - Labels, Issue Type

2. **Parse Quality Metadata**:
   - parse_quality: excellent | good | fair | poor (based on field completeness)
   - missing_fields: list of required fields that are empty
   - raw_labels: all JIRA labels

3. **Three-Amigos Notes** (optional, from pre-generation meeting):
   - Additional context, scope notes, clarifications

## YOUR JOB

1. **Synthesize** all available information into a single coherent narrative
2. **Resolve** conflicts (e.g., summary vs. description disagreements)
3. **Flag** ambiguities and assumptions (mark with [ASSUMED] or [UNCLEAR])
4. **Preserve** all business signal — nothing is noise (even comments matter)
5. **Assess** overall clarity: if acceptance_criteria is missing, explicitly note this
6. **Ground** everything in what the JIRA actually says — no inference beyond the story

## OUTPUT FORMAT

You MUST respond with ONLY a valid JSON object (no markdown, no preamble):

{
  "issue_key": "CAS-XXXXX",
  "summary": "One-line summary",
  "story_type": "Story | Bug | Task",
  "overall_intent": "2-3 sentence business outcome",
  "current_state": "What exists today (if documented)",
  "target_state": "What the story changes to",
  "acceptance_criteria_raw": "Exact acceptance criteria from JIRA or [MISSING]",
  "business_scenarios": "Edge cases, exceptions, validations",
  "ui_navigation": "Key UI steps (path through CAS)",
  "impacted_areas": "Stages, modules, roles affected",
  "parse_quality": "excellent | good | fair | poor",
  "missing_fields": ["list", "of", "fields"],
  "assumptions_and_flags": "Any [ASSUMED], [UNCLEAR], or [DOMAIN_DEPENDENT] notes",
  "three_amigos_impact": "How three-amigos notes changed interpretation (if relevant)",
  "confidence_score": 0.0 to 1.0 based on field completeness
}

## HARD RULES

1. Always include issue_key and summary
2. If acceptance_criteria is missing, put "[MISSING]" — do NOT fabricate
3. Preserve exact JIRA text in direct quotes where possible
4. Flag ambiguities with [ASSUMED] — do not hide them
5. parse_quality comes from input metadata — use it as-is
6. confidence_score = 1.0 if all fields present and clear, decrease for missing/ambiguous fields
7. Respond with ONLY valid JSON — no extra text

## When Acceptance Criteria Is Missing

CAS JIRAs sometimes lack explicit acceptance criteria. This is normal. In this case:
- Set acceptance_criteria_raw to "[MISSING — infer from System Process and Scenarios]"
- Use System Process and Business Scenarios to infer the intended behavior
- Mark this explicitly in assumptions_and_flags
- Set confidence_score < 0.8 to signal downstream that this story has risk

## Context: CAS ATDD Structure

You are feeding into a formal CAS ATDD test generation pipeline. The CAS system is:
- Large legacy application (18 LOBs, 7 stages, ~200 screens)
- Heavy on field validation, conditional logic, state transitions
- Uses custom dictionary expansion and ordered flow execution
- Domain experts will refine your output with CAS-specific knowledge

Your job is to be faithful to what JIRA says, not to interpret it.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# Agent Implementation
# ═══════════════════════════════════════════════════════════════════════════════

def agent_01_reader(state: ForgeState) -> ForgeState:
    """
    Agent 01 — Reader: Fetch JIRA story and assemble business facts.

    Input from state:
    - jira_input_mode: "csv" or "pat"
    - jira_csv_raw: raw CSV content (CSV mode)
    - jira_story_id: story ID (PAT mode)
    - jira_pat_override: optional PAT token override
    - three_amigos_notes: optional context from pre-generation meeting

    Output to state:
    - jira_facts: dict with complete story assembly
    """

    logger.info("=" * 80)
    logger.info("AGENT 01 — READER")
    logger.info("=" * 80)

    try:
        # ─────────────────────────────────────────────────────────────────────────────
        # Log Input State
        # ─────────────────────────────────────────────────────────────────────────────

        logger.info(f"Input mode: {state['jira_input_mode']}")
        logger.info(f"Story ID: {state['jira_story_id'] or 'N/A'}")
        logger.info(f"CSV raw: {len(state['jira_csv_raw'] or '')} chars")
        logger.info(f"Three-amigos notes: {bool(state['three_amigos_notes'])}")

        # ─────────────────────────────────────────────────────────────────────────────
        # Fetch Story
        # ─────────────────────────────────────────────────────────────────────────────

        try:
            story = fetch_story(
                jira_input_mode=state['jira_input_mode'],
                jira_story_id=state['jira_story_id'],
                jira_csv_raw=state['jira_csv_raw'],
                jira_pat_override=state['jira_pat_override'],
            )
            logger.info(f"Fetched story: {story.issue_key} — {story.summary[:60]}")
            logger.info(f"Parse quality: {story.parse_quality}, Missing fields: {story.missing_fields}")

        except Exception as e:
            logger.error(f"Failed to fetch story: {e}")
            raise

        # ─────────────────────────────────────────────────────────────────────────────
        # Prepare LLM Input
        # ─────────────────────────────────────────────────────────────────────────────

        jira_data_text = f"""Issue Key: {story.issue_key}
Summary: {story.summary}
Type: {story.issue_type}

Description:
{story.description}

Current Process:
{story.legacy_process or '[Not provided]'}

Target / New Process:
{story.system_process or '[Not provided]'}

Business Scenarios & Validations:
{story.business_scenarios or '[Not provided]'}

Acceptance Criteria:
{story.acceptance_criteria or '[MISSING]'}

Story Description (Custom Field):
{story.story_description or '[Not provided]'}

Key UI Steps:
{story.key_ui_steps or '[Not provided]'}

Impacted Areas/Functionalities:
{story.impacted_areas or '[Not provided]'}

Additional Comments:
{story.supplemental_comments or '[None]'}

Labels: {', '.join(story.raw_labels) if story.raw_labels else '[None]'}

Parse Quality: {story.parse_quality}
Missing Fields: {story.missing_fields if story.missing_fields else 'None'}
"""

        if state['three_amigos_notes']:
            jira_data_text += f"\n\nThree-Amigos Notes from Pre-Generation Meeting:\n{state['three_amigos_notes']}"

        logger.debug(f"LLM input (first 500 chars):\n{jira_data_text[:500]}")

        # ─────────────────────────────────────────────────────────────────────────────
        # Call LLM
        # ─────────────────────────────────────────────────────────────────────────────

        try:
            response = llm_complete(
                prompt=jira_data_text,
                system=AGENT_01_SYSTEM_PROMPT,
                max_tokens=1500
            )
            logger.info(f"LLM response received ({len(response)} chars)")

        except LLMNotLoadedError:
            logger.error("LLM not loaded — cannot continue")
            raise

        # ─────────────────────────────────────────────────────────────────────────────
        # Parse LLM Output
        # ─────────────────────────────────────────────────────────────────────────────

        try:
            # Extract JSON from response (may contain preamble, extract JSON block)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in LLM response")

            json_str = response[json_start:json_end]
            jira_facts = json.loads(json_str)

            logger.info(f"Parsed LLM JSON: issue_key={jira_facts.get('issue_key')}, "
                       f"confidence={jira_facts.get('confidence_score')}")

        except json.JSONDecodeError as e:
            logger.error(f"LLM output is not valid JSON: {e}")
            logger.error(f"LLM response:\n{response}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise

        # ─────────────────────────────────────────────────────────────────────────────
        # Enrich with Story Metadata
        # ─────────────────────────────────────────────────────────────────────────────

        jira_facts["raw_story_data"] = {
            "parse_quality": story.parse_quality,
            "missing_fields": story.missing_fields,
            "raw_labels": story.raw_labels,
        }

        # ─────────────────────────────────────────────────────────────────────────────
        # Update State
        # ─────────────────────────────────────────────────────────────────────────────

        state['jira_facts'] = jira_facts

        logger.info("Output summary:")
        logger.info(f"  - Issue: {jira_facts.get('issue_key')}")
        logger.info(f"  - Confidence: {jira_facts.get('confidence_score')}")
        logger.info(f"  - Assumptions/flags: {len(str(jira_facts.get('assumptions_and_flags', '')))}")

        logger.info("=" * 80)
        logger.info("AGENT 01 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 01 EXCEPTION: {type(e).__name__}: {e}")
        logger.error("Agent 01 failed — unable to continue")
        raise

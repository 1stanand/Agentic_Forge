"""
Agent 02 — Domain Expert (CAS Specific)

Fetches relevant CAS domain knowledge using RAG engine.
Contextualizes story facts with domain constraints, field rules, conditional behavior.

Input: jira_facts
Output: domain_brief
"""

import json
import logging

from forge.core.state import ForgeState
from forge.core.llm import llm_complete, LLMNotLoadedError
from forge.infrastructure.rag_engine import get_context

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# System Prompt
# ═══════════════════════════════════════════════════════════════════════════════

AGENT_02_SYSTEM_PROMPT = """You are the CAS Domain Expert for Forge Agentic — a specialized agent for contextualizing JIRA stories with CAS domain knowledge.

## YOUR ROLE

You have access to CAS domain documentation (via RAG). Your job is to fetch relevant knowledge and synthesize it into a comprehensive domain brief that explains the constraints, rules, and field behaviors that apply to this story.

## WHAT YOU RECEIVE

1. **JIRA Facts** (from Agent 01):
   - issue_key, summary, story_type
   - current_state, target_state
   - acceptance_criteria (may be [MISSING])
   - business_scenarios, ui_navigation
   - impacted_areas (stages, modules)
   - parse_quality, missing_fields

## YOUR JOB

1. **Identify** key entities mentioned in the story (screens, fields, stages, LOBs)
2. **Query** CAS domain knowledge base for each entity and its constraints
3. **Synthesize** domain rules into a brief that explains:
   - Field validation rules and mandatory flags
   - Stage transitions and state dependencies
   - LOB-specific variations
   - Screen navigation rules
   - Conditional logic and exceptions
4. **Flag** areas where domain knowledge is uncertain or incomplete
5. **Ground** everything in CAS documentation — never invent domain rules

## OUTPUT FORMAT

You MUST respond with ONLY a valid JSON object:

{
  "issue_key": "CAS-XXXXX",
  "domain_context": {
    "screens_involved": ["Screen1", "Screen2"],
    "stages_involved": ["Stage1", "Stage2"],
    "lobs_mentioned": ["LOB1", "LOB2"],
    "entities_and_rules": {
      "Entity1": "Domain rules, validation, constraints...",
      "Field1": "Mandatory/optional, valid values, conditional rules..."
    },
    "state_dependencies": "How state flows across stages (if applicable)",
    "validation_summary": "Key validation rules that apply to this story"
  },
  "domain_gaps": ["Area where domain is unclear"],
  "uncertain_fields": ["Field1 — [DOMAIN_UNCERTAIN]", "Field2 — [DOMAIN_UNCERTAIN]"],
  "confidence_score": 0.0 to 1.0 based on domain knowledge completeness,
  "summary": "2-3 sentence synthesis of domain context"
}

## HARD RULES

1. If domain knowledge is missing, use [DOMAIN_UNCERTAIN] flag — do NOT fabricate
2. Only report rules that are explicitly in CAS documentation
3. Mark any assumptions or inferences with [INFERRED]
4. confidence_score = 1.0 if all domain knowledge found and clear, decrease if gaps exist
5. Respond with ONLY valid JSON — no extra text

## Context: Why Domain Matters

CAS is a complex financial system:
- 18 Lines of Business with different field requirements
- 7 stages (Lead, CCDE, KYC, DDE, CreditApproval, Disbursal) with state transitions
- ~200 screens with nested navigation
- Heavy field-level conditional logic
- Multi-level approval workflows

Your domain brief helps downstream agents understand what's possible and what's constrained.
"""


# ═══════════════════════════════════════════════════════════════════════════════
# Agent Implementation
# ═══════════════════════════════════════════════════════════════════════════════

def agent_02_domain_expert(state: ForgeState) -> ForgeState:
    """
    Agent 02 — Domain Expert: Fetch CAS domain knowledge and contextualize story.

    Input from state:
    - jira_facts: dict with issue_key, summary, impacted_areas, ui_navigation

    Output to state:
    - domain_brief: dict with domain context, rules, gaps
    """

    logger.info("=" * 80)
    logger.info("AGENT 02 — DOMAIN EXPERT")
    logger.info("=" * 80)

    try:
        # ─────────────────────────────────────────────────────────────────────────────
        # Log Input State
        # ─────────────────────────────────────────────────────────────────────────────

        jira_facts = state['jira_facts'] or {}
        issue_key = jira_facts.get("issue_key", "UNKNOWN")
        impacted_areas = jira_facts.get("impacted_areas", "")
        ui_navigation = jira_facts.get("ui_navigation", "")

        logger.info(f"Story: {issue_key}")
        logger.info(f"Impacted areas: {impacted_areas[:100] if impacted_areas else 'N/A'}")
        logger.info(f"UI navigation: {ui_navigation[:100] if ui_navigation else 'N/A'}")

        # ─────────────────────────────────────────────────────────────────────────────
        # Query RAG Engine for Domain Knowledge
        # ─────────────────────────────────────────────────────────────────────────────

        try:
            # Extract screen and stage hints from story
            screen = None
            stage = None
            lob = None

            # Try to infer from impacted_areas or ui_navigation
            areas_text = (impacted_areas + " " + ui_navigation).lower()

            stages_list = ["lead", "ccde", "kyc", "dde", "creditapproval", "disbursal"]
            for s in stages_list:
                if s in areas_text:
                    stage = s.title()
                    break

            screens_list = ["collateral", "applicant", "guarantor", "property", "creditbureau"]
            for sc in screens_list:
                if sc in areas_text:
                    screen = sc.title()
                    break

            lobs_list = ["hl", "pl", "bl", "gl"]
            for lo in lobs_list:
                if lo in areas_text:
                    lob = lo.upper()
                    break

            # Build RAG query from story summary and impacted areas
            query = f"{jira_facts.get('summary', '')} {impacted_areas} {ui_navigation}"

            logger.info(f"Querying RAG: screen={screen}, stage={stage}, lob={lob}")

            domain_context = get_context(
                screen=screen,
                stage=stage,
                lob=lob,
                query=query[:500],
                top_k=5
            )

            logger.info(f"RAG context received ({len(domain_context)} chars)")

        except Exception as e:
            logger.error(f"RAG engine error: {e}")
            raise ValueError(f"Agent 02: RAG engine failed to retrieve domain context: {e}")

        # ─────────────────────────────────────────────────────────────────────────────
        # Prepare LLM Input
        # ─────────────────────────────────────────────────────────────────────────────

        lLM_input = f"""Story: {issue_key}
Summary: {jira_facts.get('summary', '')}

Impacted Areas: {impacted_areas or '[Not specified]'}
UI Navigation: {ui_navigation or '[Not specified]'}

Target State: {jira_facts.get('target_state', '')}
Acceptance Criteria: {jira_facts.get('acceptance_criteria_raw', '[MISSING]')}

Business Scenarios: {jira_facts.get('business_scenarios', '[None]')}

=== CAS DOMAIN CONTEXT (from RAG) ===
{domain_context}

=== YOUR TASK ===
Extract domain knowledge that applies to this story. Identify:
1. Screens, stages, and LOBs involved
2. Key entities (fields, roles, workflows)
3. Validation rules and constraints
4. State dependencies and transitions
5. Areas where domain knowledge is missing or unclear

Mark uncertain knowledge with [DOMAIN_UNCERTAIN].
"""

        logger.debug(f"LLM input (first 500 chars):\n{lLM_input[:500]}")

        # ─────────────────────────────────────────────────────────────────────────────
        # Call LLM
        # ─────────────────────────────────────────────────────────────────────────────

        try:
            response = llm_complete(
                prompt=lLM_input,
                system=AGENT_02_SYSTEM_PROMPT,
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
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in LLM response")

            json_str = response[json_start:json_end]
            domain_brief = json.loads(json_str)

            logger.info(f"Parsed domain brief: {domain_brief.get('issue_key')}, "
                       f"confidence={domain_brief.get('confidence_score')}")

            if domain_brief.get("uncertain_fields"):
                logger.warning(f"Uncertain fields: {domain_brief.get('uncertain_fields')}")

        except json.JSONDecodeError as e:
            logger.error(f"LLM output is not valid JSON: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            raise

        # ─────────────────────────────────────────────────────────────────────────────
        # Update State
        # ─────────────────────────────────────────────────────────────────────────────

        state['domain_brief'] = domain_brief

        logger.info("Output summary:")
        logger.info(f"  - Screens: {domain_brief.get('domain_context', {}).get('screens_involved', [])}")
        logger.info(f"  - Stages: {domain_brief.get('domain_context', {}).get('stages_involved', [])}")
        logger.info(f"  - Confidence: {domain_brief.get('confidence_score')}")
        logger.info(f"  - Gaps: {len(domain_brief.get('domain_gaps', []))}")

        logger.info("=" * 80)
        logger.info("AGENT 02 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 02 EXCEPTION: {type(e).__name__}: {e}")
        raise

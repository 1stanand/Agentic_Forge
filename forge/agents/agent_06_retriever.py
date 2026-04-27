"""
Agent 06 — Retriever

Retrieves matching CAS test steps for each action decomposed by Agent 05.
Calls step_retriever with rich context, preserves markers through to output.

Input: action_sequences (intents → Given/When/Then actions)
Output: retrieved_steps (dict mapping actions to step candidates with markers)
"""

import json
import logging
from typing import Dict, List, Any

from forge.core.state import ForgeState
from forge.core.llm import llm_complete, LLMNotLoadedError
from forge.infrastructure.step_retriever import retrieve

logger = logging.getLogger(__name__)

AGENT_06_SYSTEM_PROMPT = """You are the Retriever for Forge Agentic.

Your job: For each Given/When/Then action, retrieve matching CAS test steps from the repo.
Steps come with ce_score, marker, and screen context — pass through exactly as received.

## Markers (Never Drop)

- [NEW_STEP_NOT_IN_REPO]: ce_score < 0.3, no repo match
- [LOW_MATCH]: 0.3 <= ce_score < 0.7, weak match
- [ROLE_GAP]: step role does not match domain requirements
- No marker: ce_score >= 0.7, confident repo match

## Per-Action Process

For each action:
1. Extract action text (e.g., "Given user is on Login Page")
2. Call retriever (implicit in this agent)
3. Collect top-5 candidates with ce_score and marker
4. Return: action → [step1 (ce_score, marker), step2, ...]

## Output

{
  "issue_key": "CAS-XXXXX",
  "action_sequences": {
    "LogicalID_1": {
      "intent": "...",
      "given_steps": [...],
      "when_steps": [...],
      "then_steps": [...],
      "retrieved_steps": {
        "Given user is on Login Page": [
          {"step_text": "Given user navigates to Login screen", "ce_score": 0.92, "marker": null},
          {"step_text": "Given user opens browser and enters URL", "ce_score": 0.71, "marker": null}
        ],
        ...
      }
    }
  },
  "retrieval_confidence": 0.0 to 1.0,
  "retrieval_gaps": ["actions with no match above LOW_MATCH threshold"]
}

IMPORTANT:
- Never drop markers — they indicate step quality
- Top-5 per action, sorted by ce_score descending
- Include screen_context and stage_hint if available
- Mark gaps where ce_score < 0.3 across all candidates
"""

def agent_06_retriever(state: ForgeState) -> ForgeState:
    """Retrieve matching CAS steps for each action. Preserve all markers."""

    logger.info("=" * 80)
    logger.info("AGENT 06 — RETRIEVER")
    logger.info("=" * 80)

    try:
        action_sequences = state['action_sequences'] or {}
        issue_key = action_sequences.get("issue_key", "UNKNOWN")
        logical_seqs = action_sequences.get("action_sequences", {})

        logger.info(f"Story: {issue_key}, Sequences: {len(logical_seqs)}")

        # Build retrieval index: collect all unique actions
        all_actions = set()
        action_to_seq = {}  # action_text -> list of (logical_id, phase)

        for logical_id, seq_data in logical_seqs.items():
            intent = seq_data.get("intent", "")
            given = seq_data.get("given_steps", [])
            when = seq_data.get("when_steps", [])
            then = seq_data.get("then_steps", [])

            for action_text in given + when + then:
                all_actions.add(action_text)
                if action_text not in action_to_seq:
                    action_to_seq[action_text] = []
                action_to_seq[action_text].append((logical_id, intent))

        logger.info(f"Retrieving for {len(all_actions)} unique actions across {len(logical_seqs)} sequences")

        # Retrieve for each action
        retrieved_map = {}  # action_text -> [candidate1, candidate2, ...]

        for action_text in all_actions:
            try:
                candidates = retrieve(action_text, top_k=5)
                retrieved_map[action_text] = candidates

                # Log sample
                if candidates:
                    top = candidates[0]
                    logger.debug(
                        f"Action '{action_text[:50]}...' → "
                        f"top: '{top.get('step_text', '')[:60]}...' "
                        f"ce_score={top.get('ce_score'):.2f} "
                        f"marker={top.get('marker')}"
                    )
            except Exception as e:
                logger.warning(f"Retrieval failed for '{action_text[:50]}...': {e}")
                retrieved_map[action_text] = []

        # Build output with markers preserved
        result_sequences = {}
        retrieval_gaps = []

        for logical_id, seq_data in logical_seqs.items():
            given = seq_data.get("given_steps", [])
            when = seq_data.get("when_steps", [])
            then = seq_data.get("then_steps", [])

            retrieved_by_phase = {}

            # Given
            for action_text in given:
                candidates = retrieved_map.get(action_text, [])
                if not candidates or all(float(c.get("ce_score", 0)) < 0.3 for c in candidates):
                    retrieval_gaps.append(f"{logical_id} Given: {action_text[:50]}")
                retrieved_by_phase[action_text] = candidates

            # When
            for action_text in when:
                candidates = retrieved_map.get(action_text, [])
                if not candidates or all(float(c.get("ce_score", 0)) < 0.3 for c in candidates):
                    retrieval_gaps.append(f"{logical_id} When: {action_text[:50]}")
                retrieved_by_phase[action_text] = candidates

            # Then
            for action_text in then:
                candidates = retrieved_map.get(action_text, [])
                if not candidates or all(float(c.get("ce_score", 0)) < 0.3 for c in candidates):
                    retrieval_gaps.append(f"{logical_id} Then: {action_text[:50]}")
                retrieved_by_phase[action_text] = candidates

            result_sequences[logical_id] = {
                "intent": seq_data.get("intent"),
                "given_steps": given,
                "when_steps": when,
                "then_steps": then,
                "retrieved_steps": retrieved_by_phase
            }

        # Compute confidence: percent of actions with ce_score >= 0.7
        confident_count = 0
        for action_text, candidates in retrieved_map.items():
            if candidates and float(candidates[0].get("ce_score", 0)) >= 0.7:
                confident_count += 1

        confidence = confident_count / len(retrieved_map) if retrieved_map else 0.0

        retrieved_output = {
            "issue_key": issue_key,
            "action_sequences": result_sequences,
            "retrieval_confidence": confidence,
            "retrieval_gaps": retrieval_gaps
        }

        logger.info(f"Retrieved: confidence={confidence:.2f}, gaps={len(retrieval_gaps)}")

        state['retrieved_steps'] = retrieved_output

        logger.info("=" * 80)
        logger.info("AGENT 06 — COMPLETE")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 06 EXCEPTION: {type(e).__name__}: {e}")
        raise

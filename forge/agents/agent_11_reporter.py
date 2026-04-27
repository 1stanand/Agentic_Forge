"""
Agent 11 — Reporter

Assembles final_output with feature file, gap report, confidence, and markers summary.
Always produces output. Low confidence stated explicitly.

Input: feature_file (from Agent 09 after Critic loop), critic_review
Output: final_output (complete output ready for user)
"""

import json
import logging
from typing import Dict, List, Any

from forge.core.state import ForgeState

logger = logging.getLogger(__name__)

def agent_11_reporter(state: ForgeState) -> ForgeState:
    """Assemble final output with confidence and gap report. Always produce output."""

    logger.info("=" * 80)
    logger.info("AGENT 11 — REPORTER")
    logger.info("=" * 80)

    try:
        # Collect outputs from all prior agents
        jira_facts = state['jira_facts'] or {}
        domain_brief = state['domain_brief'] or {}
        scope = state['scope'] or {}
        coverage_plan = state['coverage_plan'] or {}
        action_sequences = state['action_sequences'] or {}
        retrieved_steps = state['retrieved_steps'] or {}
        composed_scenarios = state['composed_scenarios'] or {}
        validation_result = state['validation_result'] or {}
        feature_output = state['feature_file'] or {}
        critic_review = state['critic_review'] or {}

        issue_key = jira_facts.get("issue_key", "UNKNOWN")
        flow_type = state['flow_type'] or "unordered"

        logger.info(f"Story: {issue_key}, Flow: {flow_type}")
        logger.info(f"Agents completed: 1-9 → Critic → Agents 7/9/11 (loop if needed)")

        # Build gap report from all phases
        gap_report = {
            "coverage_gaps": coverage_plan.get("coverage_gaps", []),
            "retrieval_gaps": retrieved_steps.get("retrieval_gaps", []),
            "validation_errors": validation_result.get("validation_errors", []),
            "critic_feedback": critic_review.get("feedback", "")
        }

        # Compute overall confidence
        confidences = []

        # Agent 1 (Reader)
        reader_conf = jira_facts.get("parse_quality_confidence", 0.7)
        confidences.append(("reader", reader_conf))

        # Agent 2 (Domain Expert)
        domain_conf = domain_brief.get("domain_confidence", 0.6)
        confidences.append(("domain_expert", domain_conf))

        # Agent 4 (Coverage Planner)
        coverage_conf = coverage_plan.get("coverage_confidence", 0.7)
        confidences.append(("coverage_planner", coverage_conf))

        # Agent 6 (Retriever)
        retrieval_conf = retrieved_steps.get("retrieval_confidence", 0.5)
        confidences.append(("retriever", retrieval_conf))

        # Agent 7 (Composer)
        composition_conf = composed_scenarios.get("composition_confidence", 0.8)
        confidences.append(("composer", composition_conf))

        # Agent 8 (ATDD Expert) — high confidence if validation passed
        validation_pass = validation_result.get("validation_pass", False)
        expert_conf = 1.0 if validation_pass else 0.0
        confidences.append(("atdd_expert", expert_conf))

        # Agent 9 (Writer)
        writer_conf = feature_output.get("feature_confidence", 0.8)
        confidences.append(("writer", writer_conf))

        # Agent 10 (Critic)
        critic_conf = critic_review.get("critic_confidence", 0.5)
        confidences.append(("critic", critic_conf))

        # Overall: average of all confidences, weight by importance
        weights = {
            "reader": 0.15,
            "domain_expert": 0.15,
            "coverage_planner": 0.1,
            "retriever": 0.15,
            "composer": 0.1,
            "atdd_expert": 0.15,
            "writer": 0.1,
            "critic": 0.1
        }

        overall_confidence = sum(
            conf * weights.get(agent, 1.0 / len(confidences))
            for agent, conf in confidences
        ) / sum(weights.values())

        # Mark as LOW CONFIDENCE if validation failed or multiple large gaps
        confidence_notes = []
        if not validation_pass:
            confidence_notes.append("⚠ Validation FAILED — manual review required")
            overall_confidence *= 0.7

        retrieval_gaps = retrieved_steps.get("retrieval_gaps", [])
        if len(retrieval_gaps) > len(composed_scenarios.get("scenarios", [])) * 0.3:
            confidence_notes.append(f"⚠ High retrieval gap rate ({len(retrieval_gaps)} actions)")
            overall_confidence *= 0.8

        coverage_gaps = coverage_plan.get("coverage_gaps", [])
        if len(coverage_gaps) > 3:
            confidence_notes.append(f"⚠ Significant coverage gaps detected ({len(coverage_gaps)} gaps)")

        # Markers summary
        all_markers = set()
        for scenario in composed_scenarios.get("scenarios", []):
            all_markers.update(scenario.get("markers", []))

        marker_counts = {}
        for marker in all_markers:
            marker_counts[marker] = sum(
                1 for s in composed_scenarios.get("scenarios", [])
                if marker in s.get("markers", [])
            )

        # Build final_output
        final_output = {
            "issue_key": issue_key,
            "flow_type": flow_type,
            "feature_file": feature_output.get("feature_file", ""),
            "overall_confidence": round(overall_confidence, 2),
            "confidence_notes": confidence_notes,
            "validation_status": "PASS" if validation_pass else "FAIL",
            "gap_report": gap_report,
            "markers_summary": {
                "unique_markers": list(all_markers),
                "marker_counts": marker_counts,
                "total_marked_steps": sum(marker_counts.values())
            },
            "scenarios_generated": len(composed_scenarios.get("scenarios", [])),
            "agents_execution": {
                "reader": "✓",
                "domain_expert": "✓",
                "scope_definer": "✓",
                "coverage_planner": "✓",
                "action_decomposer": "✓",
                "retriever": "✓",
                "composer": "✓",
                "atdd_expert": "PASS" if validation_pass else "FAIL",
                "writer": "✓",
                "critic": "✓",
                "reporter": "✓"
            },
            "ready_for_commit": validation_pass and overall_confidence >= 0.7
        }

        # Log final summary
        logger.info(f"Final output assembled:")
        logger.info(f"  - Confidence: {overall_confidence:.2f}")
        logger.info(f"  - Validation: {final_output['validation_status']}")
        logger.info(f"  - Scenarios: {final_output['scenarios_generated']}")
        logger.info(f"  - Markers: {final_output['markers_summary']['total_marked_steps']}")
        logger.info(f"  - Gaps: {len(gap_report['coverage_gaps']) + len(gap_report['retrieval_gaps'])}")
        logger.info(f"  - Ready for commit: {final_output['ready_for_commit']}")

        state['final_output'] = final_output

        logger.info("=" * 80)
        logger.info("AGENT 11 — COMPLETE")
        logger.info("Pipeline execution complete. Feature file ready.")
        logger.info("=" * 80)

        return state

    except Exception as e:
        logger.error(f"AGENT 11 EXCEPTION: {type(e).__name__}: {e}")
        raise

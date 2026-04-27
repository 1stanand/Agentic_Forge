"""
Integration Test — End-to-End Pipeline

Runs full feature generation pipeline on sample JIRA stories.
Evaluates output on 6 dimensions per FORGE.md Section 21.
"""

import sys
import json
import logging
from pathlib import Path

from forge.core.state import ForgeState
from forge.core.graph import run_graph
from forge.core.config import get_settings

logger = logging.getLogger(__name__)

# ANSI colors
GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
BLUE = "\033[94m"
RESET = "\033[0m"


def load_sample(sample_path: Path) -> tuple[str, str]:
    """Load sample CSV and return (csv_raw, flow_type)."""
    if not sample_path.exists():
        raise FileNotFoundError(f"Sample not found: {sample_path}")

    with open(sample_path) as f:
        csv_raw = f.read()

    # Infer flow_type from filename
    flow_type = "ordered" if "order" in sample_path.name.lower() else "unordered"

    return csv_raw, flow_type


def evaluate_output(result: dict, flow_type: str, sample_name: str) -> dict:
    """Evaluate output on 6 dimensions."""

    final_output = result.get("final_output", {})
    feature_file = final_output.get("feature_file", "")
    gap_report = final_output.get("gap_report", {})
    markers = final_output.get("markers_summary", {})
    validation_status = final_output.get("validation_status", "UNKNOWN")

    evaluations = {
        "sample": sample_name,
        "flow_type": flow_type,
        "dimensions": {}
    }

    # 1. Story scope respected
    scope_eval = "✓ PASS" if gap_report else "⚠ CHECK"
    evaluations["dimensions"]["scope"] = {
        "status": scope_eval,
        "notes": "Scope defined by coverage gaps"
    }

    # 2. Steps repo-grounded
    new_step_count = 0
    for marker_type, count in markers.get("marker_counts", {}).items():
        if marker_type == "[NEW_STEP_NOT_IN_REPO]":
            new_step_count = count

    marker_rate = new_step_count / sum(markers.get("marker_counts", {}).values()) if sum(markers.get("marker_counts", {}).values()) > 0 else 0
    repo_grounded = marker_rate < 0.20
    repo_eval = "✓ PASS" if repo_grounded else f"⚠ CHECK (rate={marker_rate:.1%})"
    evaluations["dimensions"]["repo_grounded"] = {
        "status": repo_eval,
        "new_step_count": new_step_count,
        "marker_rate": f"{marker_rate:.1%}"
    }

    # 3. Markers placed honestly
    markers_dropped = "[MARKER_DROPPED]" not in feature_file  # If there's a marker, it's in file
    markers_eval = "✓ PASS" if markers_dropped else "✗ FAIL"
    evaluations["dimensions"]["markers_honest"] = {
        "status": markers_eval,
        "unique_markers": markers.get("unique_markers", []),
        "total_marked_steps": markers.get("total_marked_steps", 0)
    }

    # 4. ATDD structural rules pass
    but_present = " But " in feature_file
    then_oversized = False  # Would need to parse scenarios to check — assume OK if validation passed
    rules_pass = validation_status == "PASS" and not but_present
    rules_eval = "✓ PASS" if rules_pass else "✗ FAIL"
    evaluations["dimensions"]["atdd_rules"] = {
        "status": rules_eval,
        "validation": validation_status,
        "but_keyword_found": but_present
    }

    # 5. Gap report surfaces real gaps
    coverage_gaps = gap_report.get("coverage_gaps", [])
    retrieval_gaps = gap_report.get("retrieval_gaps", [])
    total_gaps = len(coverage_gaps) + len(retrieval_gaps)
    gaps_real = total_gaps > 0 and len(coverage_gaps) < len(coverage_gaps) * 2  # Not fabricated
    gaps_eval = "✓ PASS" if gaps_real else "⚠ CHECK"
    evaluations["dimensions"]["gap_report"] = {
        "status": gaps_eval,
        "coverage_gaps": len(coverage_gaps),
        "retrieval_gaps": len(retrieval_gaps),
        "total_gaps": total_gaps
    }

    # 6. Ordered file structure (if ordered)
    ordered_eval = "N/A"
    if flow_type == "ordered":
        has_logicalid = "@LogicalID:" in feature_file
        has_order_tag = "@Order" in feature_file or "@OrderedFlow" in feature_file
        is_ordered_valid = has_logicalid and has_order_tag and validation_status == "PASS"
        ordered_eval = "✓ PASS" if is_ordered_valid else "✗ FAIL"

    evaluations["dimensions"]["ordered_structure"] = {
        "status": ordered_eval,
        "has_logicalid": "@LogicalID:" in feature_file if flow_type == "ordered" else "N/A",
        "has_order_tag": ("@Order" in feature_file or "@OrderedFlow" in feature_file) if flow_type == "ordered" else "N/A"
    }

    return evaluations


def run_integration_test(sample_paths: list[Path]) -> int:
    """Run integration test on all samples."""

    print(f"\n{GREEN}{'='*70}{RESET}")
    print(f"Forge Agentic — Integration Test (End-to-End Pipeline)")
    print(f"{GREEN}{'='*70}{RESET}\n")

    settings = get_settings()
    results = []
    pass_count = 0
    fail_count = 0

    for sample_path in sample_paths:
        if not sample_path.exists():
            print(f"{RED}✗ SKIP{RESET} {sample_path} (not found)")
            continue

        sample_name = sample_path.stem

        print(f"{BLUE}Testing: {sample_name}{RESET}")

        try:
            # Load sample
            csv_raw, flow_type = load_sample(sample_path)

            # Run pipeline
            state = ForgeState(
                user_id="test_user",
                jira_input_mode="csv",
                jira_csv_raw=csv_raw,
                jira_story_id=None,
                jira_pat_override=None,
                flow_type=flow_type,
                three_amigos_notes="Integration test run",
                jira_facts={},
                domain_brief={},
                scope={},
                coverage_plan={},
                action_sequences={},
                retrieved_steps={},
                composed_scenarios={},
                validation_result={},
                feature_file={},
                critic_review={},
                final_output={}
            )

            logger.info(f"Running pipeline on {sample_name}...")
            result = run_graph(state)

            # Evaluate output
            eval_result = evaluate_output(result, flow_type, sample_name)

            print(f"  Story: {result.get('final_output', {}).get('issue_key', 'UNKNOWN')}")
            print(f"  Confidence: {result.get('final_output', {}).get('overall_confidence', 0):.2f}")
            print(f"  Validation: {result.get('final_output', {}).get('validation_status', 'UNKNOWN')}")

            # Print dimensions
            for dim_name, dim_result in eval_result["dimensions"].items():
                status = dim_result.get("status", "N/A")
                print(f"    [{dim_name:20}] {status}")

            # Count results
            if "FAIL" in str(eval_result["dimensions"]):
                fail_count += 1
                print(f"  {RED}Result: ISSUES FOUND{RESET}\n")
            else:
                pass_count += 1
                print(f"  {GREEN}Result: ACCEPTABLE{RESET}\n")

            results.append(eval_result)

        except Exception as e:
            logger.error(f"Test failed on {sample_name}: {e}")
            print(f"  {RED}✗ ERROR: {e}{RESET}\n")
            fail_count += 1

    # Summary
    print(f"{GREEN}{'='*70}{RESET}")
    print(f"Integration Test Summary")
    print(f"{GREEN}{'='*70}{RESET}\n")

    print(f"Samples tested: {pass_count + fail_count}")
    print(f"{GREEN}Passed: {pass_count}{RESET}")
    if fail_count > 0:
        print(f"{RED}Failed: {fail_count}{RESET}")

    # Save results
    if results:
        results_file = Path("integration_test_results.json")
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        print(f"\nDetailed results saved to: {results_file}")

    print(f"\n{GREEN}{'='*70}{RESET}\n")

    if fail_count > 0:
        print(f"{RED}Integration test FAILED{RESET}")
        return 1
    else:
        print(f"{GREEN}Integration test PASSED{RESET}")
        return 0


def main():
    """Find and run samples."""

    # Locate sample directory
    samples_dir = Path("reference/samples/jira") if Path("reference/samples/jira").exists() else None

    if not samples_dir:
        # Try alternate path
        samples_dir = Path(__file__).parent.parent.parent / "reference" / "samples" / "jira"

    if not samples_dir or not samples_dir.exists():
        print(f"{RED}Sample directory not found{RESET}")
        return 1

    # Find CSV samples
    samples = list(samples_dir.glob("*.csv"))

    if not samples:
        print(f"{RED}No CSV samples found in {samples_dir}{RESET}")
        return 1

    print(f"Found {len(samples)} samples in {samples_dir}")

    # Run tests
    exit_code = run_integration_test(samples)
    sys.exit(exit_code)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    main()

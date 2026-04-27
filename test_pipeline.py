#!/usr/bin/env python
"""End-to-end test of feature file generation pipeline."""

import sys
import json
import logging
from pathlib import Path
from datetime import datetime

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)-7s %(message)s'
)
logger = logging.getLogger(__name__)

def test_pipeline():
    """Run pipeline on all sample JIRA files."""

    # Create output directory
    output_dir = Path("D:\\Code\\Agentic_Forge\\generated_features")
    output_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Sample files to test
    sample_dir = Path("D:\\Code\\Agentic_Forge\\data\\Sample_JIRA\\Jira Samples")
    samples = sorted(sample_dir.glob("*.csv"))

    logger.info(f"Found {len(samples)} sample JIRA files")

    # Import after path setup
    try:
        from forge.core.graph import run_graph
        from forge.core.state import ForgeState
    except ImportError as e:
        logger.error(f"Import error: {e}")
        return False

    results = []

    for sample_path in samples:
        sample_name = sample_path.stem
        logger.info(f"\n{'='*60}")
        logger.info(f"Testing: {sample_name}")
        logger.info('='*60)

        try:
            # Read CSV
            with open(sample_path, encoding='utf-8-sig') as f:
                csv_raw = f.read()

            logger.info(f"CSV size: {len(csv_raw)} bytes")

            # Determine flow type from filename
            flow_type = "ordered" if "256008" in sample_name or "271059" in sample_name else "unordered"

            # Create state
            state = ForgeState(
                user_id="test_user",
                jira_input_mode="csv",
                jira_csv_raw=csv_raw,
                flow_type=flow_type,
                three_amigos_notes="",
                jira_story_id=None,
                jira_pat_override=None
            )

            logger.info(f"State created: flow_type={flow_type}")

            # Run pipeline
            logger.info("Running pipeline...")
            result = run_graph(state)

            # Check output
            feature_file = result.get('feature_file', '')
            gap_report = result.get('final_output', {}).get('gap_report', {})

            if feature_file:
                logger.info(f"✓ Feature file generated ({len(feature_file)} bytes)")

                # Save to file
                output_file = output_dir / f"{sample_name}.feature"
                output_file.write_text(feature_file, encoding='utf-8')
                logger.info(f"✓ Saved to {output_file}")

                # Count key elements
                scenarios = feature_file.count("Scenario:")
                steps = feature_file.count("\n  ")
                logger.info(f"  Scenarios: {scenarios}, Steps: {steps}")

                results.append({
                    'sample': sample_name,
                    'status': 'SUCCESS',
                    'file_size': len(feature_file),
                    'scenarios': scenarios,
                    'steps': steps
                })
            else:
                logger.warning("✗ No feature file generated")
                results.append({
                    'sample': sample_name,
                    'status': 'FAILED',
                    'reason': 'No feature_file in result'
                })

            if gap_report:
                logger.info(f"Gap report: {json.dumps(gap_report, indent=2)[:200]}...")

        except Exception as e:
            logger.error(f"✗ Pipeline failed: {e}", exc_info=True)
            results.append({
                'sample': sample_name,
                'status': 'ERROR',
                'error': str(e)
            })

    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("TEST SUMMARY")
    logger.info('='*60)

    success_count = sum(1 for r in results if r['status'] == 'SUCCESS')
    logger.info(f"Successful: {success_count}/{len(results)}")

    for r in results:
        if r['status'] == 'SUCCESS':
            logger.info(f"  ✓ {r['sample']}: {r['file_size']} bytes, {r['scenarios']} scenarios")
        else:
            logger.info(f"  ✗ {r['sample']}: {r['status']} - {r.get('reason', r.get('error', ''))}")

    return success_count > 0

if __name__ == "__main__":
    success = test_pipeline()
    sys.exit(0 if success else 1)

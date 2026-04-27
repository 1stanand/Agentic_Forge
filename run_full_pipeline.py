"""
Full 11-agent pipeline execution with output capture.
"""
import json
import sys
from pathlib import Path
from datetime import datetime
from forge.core.graph import run_graph
from forge.core.state import ForgeState

# Read the JIRA CSV sample
csv_path = Path("D:\Code\Agentic_Forge\reference\samples\jira\CAS-254473.csv")
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    csv_raw = f.read()

# Create output directory
output_dir = Path("D:\Code\Agentic_Forge\pipeline_output")
output_dir.mkdir(exist_ok=True)

# Prepare state
state = ForgeState(
    user_id="demo_user",
    jira_input_mode="csv",
    jira_csv_raw=csv_raw,
    flow_type="unordered",
    three_amigos_notes="",
    jira_story_id=None,
    jira_pat_override=None,
    module="cas"
)

print("=" * 70)
print("FORGE AGENTIC — FULL 11-AGENT PIPELINE EXECUTION")
print("=" * 70)
print(f"\nInput: CAS-254473.csv")
print(f"Flow Type: unordered")
print(f"Module: cas")
print(f"Start Time: {datetime.now().isoformat()}")
print("\nRunning 11-agent pipeline...")
print("-" * 70)

# Run the graph
try:
    result = run_graph(state)
    print("\n✓ Pipeline completed successfully")
except Exception as e:
    print(f"\n✗ Pipeline failed: {str(e)}")
    result = {"error": str(e)}
    import traceback
    traceback.print_exc()

print("-" * 70)
print(f"End Time: {datetime.now().isoformat()}\n")

# Save feature file
feature_file = result.get('feature_file', '')
if feature_file:
    feature_path = output_dir / "CAS-254473.feature"
    with open(feature_path, 'w', encoding='utf-8') as f:
        f.write(feature_file)
    print(f"✓ Feature file saved: {feature_path}")
    print(f"  Size: {len(feature_file)} characters")
else:
    print("✗ No feature file generated")

# Save gap report
gap_report = result.get('final_output', {}).get('gap_report', {})
if gap_report:
    gap_path = output_dir / "gap_report.json"
    with open(gap_path, 'w', encoding='utf-8') as f:
        json.dump(gap_report, f, indent=2)
    print(f"✓ Gap report saved: {gap_path}")
else:
    print("⚠ No gap report generated")

# Save full result for reference
result_path = output_dir / "full_result.json"
try:
    # Remove non-serializable items for JSON
    safe_result = {
        'feature_file': result.get('feature_file', '')[:500] + "..." if result.get('feature_file') else None,
        'final_output': result.get('final_output'),
        'agent_trace': result.get('agent_trace'),
    }
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(safe_result, f, indent=2)
    print(f"✓ Full result metadata saved: {result_path}")
except Exception as e:
    print(f"⚠ Could not save full result: {e}")

# Display preview
print("\n" + "=" * 70)
print("GENERATED FEATURE FILE PREVIEW")
print("=" * 70)
if feature_file:
    preview = feature_file[:2000]
    print(preview)
    if len(feature_file) > 2000:
        print(f"\n... ({len(feature_file) - 2000} more characters)")
else:
    print("(No feature file generated)")

print("\n" + "=" * 70)
print("GAP REPORT PREVIEW")
print("=" * 70)
if gap_report:
    print(json.dumps(gap_report, indent=2)[:1000])
    if len(json.dumps(gap_report)) > 1000:
        print("\n... (see gap_report.json for full report)")
else:
    print("(No gap report generated)")

print("\n" + "=" * 70)
print("OUTPUT FILES LOCATION")
print("=" * 70)
print(f"Directory: {output_dir}")
print(f"\nFiles:")
for f in sorted(output_dir.glob("*")):
    if f.is_file():
        size = f.stat().st_size
        print(f"  - {f.name} ({size:,} bytes)")


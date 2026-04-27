"""Audit for missing function calls and integration gaps."""
import os
import re
from pathlib import Path

issues = []

# 1. Check feature_parser.py calls infer_screen_contexts
print("=== AUDIT: Integration Gaps ===\n")

# Check 1: feature_parser.py should call screen_context inference
parser_file = Path("forge/infrastructure/feature_parser.py")
if parser_file.exists():
    content = parser_file.read_text()
    if "infer_screen_contexts" not in content:
        issues.append({
            "file": "feature_parser.py",
            "missing_call": "infer_screen_contexts()",
            "should_be_called": "After each scenario is parsed, to populate step.screen_context",
            "severity": "HIGH"
        })
    if "stage_hint" not in content:
        issues.append({
            "file": "feature_parser.py",
            "missing_call": "stage_hint population",
            "should_be_called": "During parsing if any stage markers detected",
            "severity": "MEDIUM"
        })

# Check 2: repo_indexer.py should call screen_context enrichment after indexing
indexer_file = Path("forge/infrastructure/repo_indexer.py")
if indexer_file.exists():
    content = indexer_file.read_text()
    if "infer_screen" not in content and "screen_context" not in content:
        issues.append({
            "file": "repo_indexer.py",
            "missing_call": "screen_context enrichment pass",
            "should_be_called": "After all features indexed, to backfill screen_context on steps",
            "severity": "HIGH"
        })

# Check 3: build_knowledge.py should extract PDF structure
knowledge_file = Path("forge/scripts/build_knowledge.py")
if knowledge_file.exists():
    content = knowledge_file.read_text()
    if "section" not in content.lower() or "heading" not in content.lower():
        issues.append({
            "file": "build_knowledge.py",
            "missing_call": "PDF section/heading detection",
            "should_be_called": "To extract stage_hint and screen_hint from PDF structure",
            "severity": "HIGH"
        })

# Check 4: step_retriever.py - verify it calls all retrieval channels
retriever_file = Path("forge/infrastructure/step_retriever.py")
if retriever_file.exists():
    content = retriever_file.read_text()
    channels = ["faiss", "fts", "trigram", "cross_encoder"]
    missing = [ch for ch in channels if ch not in content.lower()]
    if missing:
        issues.append({
            "file": "step_retriever.py",
            "missing_call": f"Retrieval channels: {missing}",
            "should_be_called": "5-channel hybrid retrieval (FAISS + FTS + trigram + cross-encoder + Self-RAG)",
            "severity": "CRITICAL" if len(missing) > 1 else "HIGH"
        })

# Check 5: rag_engine.py - verify it calls distillation and caching
rag_file = Path("forge/infrastructure/rag_engine.py")
if rag_file.exists():
    content = rag_file.read_text()
    if "rag_cache" not in content:
        issues.append({
            "file": "rag_engine.py",
            "missing_call": "rag_cache table query",
            "should_be_called": "Before distillation, check cache with key={screen}_{stage}_{lob}",
            "severity": "HIGH"
        })

# Check 6: Verify all 11 agents exist and are wired
agents_dir = Path("forge/agents")
if agents_dir.exists():
    agent_files = sorted(agents_dir.glob("agent_*.py"))
    expected_count = 11
    if len(agent_files) < expected_count:
        issues.append({
            "file": "forge/agents/",
            "missing_call": f"Missing agents ({len(agent_files)}/{expected_count})",
            "should_be_called": "All 11 agents should exist and be wired in graph.py",
            "severity": "CRITICAL"
        })

# Check 7: graph.py should wire all agents
graph_file = Path("forge/core/graph.py")
if graph_file.exists():
    content = graph_file.read_text()
    agent_count = content.count(".add_node(")
    if agent_count < 11:
        issues.append({
            "file": "graph.py",
            "missing_call": f"Agent wiring (only {agent_count} nodes, expected 11+)",
            "should_be_called": "All 11 agents must be added as nodes and edges wired",
            "severity": "CRITICAL"
        })

# Check 8: Verify query_expander functions are all present
expander_file = Path("forge/infrastructure/query_expander.py")
if expander_file.exists():
    content = expander_file.read_text()
    functions = ["normalise_query_text", "expand_for_vector", "expand_for_fts", "expand_for_trigram"]
    missing = [fn for fn in functions if fn not in content]
    if missing:
        issues.append({
            "file": "query_expander.py",
            "missing_call": f"Functions: {missing}",
            "should_be_called": "HyDE pattern requires all 4 expansion functions",
            "severity": "HIGH"
        })

# Check 9: Verify order_json_reader exists and is imported where needed
order_reader = Path("forge/infrastructure/order_json_reader.py")
step_ret = Path("forge/infrastructure/step_retriever.py")
if order_reader.exists() and step_ret.exists():
    step_ret_content = step_ret.read_text()
    if "order_json" not in step_ret_content.lower():
        issues.append({
            "file": "step_retriever.py",
            "missing_call": "order_json_reader import/usage",
            "should_be_called": "For stage detection and boost in retrieval",
            "severity": "MEDIUM"
        })

# Check 10: graph_rag.py for role validation
graph_rag = Path("forge/infrastructure/graph_rag.py")
if graph_rag.exists():
    content = graph_rag.read_text()
    if "validate_step" not in content or "ROLE_GAP" not in content:
        issues.append({
            "file": "graph_rag.py",
            "missing_call": "validate_step() / ROLE_GAP marker",
            "should_be_called": "For assigning [ROLE_GAP] markers in step_retriever",
            "severity": "MEDIUM"
        })

# Print results
if issues:
    print(f"Found {len(issues)} potential integration gaps:\n")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. [{issue['severity']}] {issue['file']}")
        print(f"   Missing: {issue['missing_call']}")
        print(f"   Should be called: {issue['should_be_called']}")
        print()
else:
    print("No obvious integration gaps found.")

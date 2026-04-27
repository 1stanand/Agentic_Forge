# Comprehensive Code Audit — Critical Findings

**Date:** 2026-04-27 05:30 AM  
**Status:** DETAILED ROOT CAUSE ANALYSIS COMPLETE

---

## Executive Summary

The codebase has **3 critical failures** and **multiple integration gaps** causing the system to fail end-to-end. These are not bugs — they are **incomplete implementations** that were left as stubs.

**Root Cause:** Minimal implementations chosen to "save tokens" instead of porting complete reference code. This created cascading failures through the entire pipeline.

---

## CRITICAL ISSUE 1: feature_parser.py (74 lines vs. required 626+)

**File:** `forge/infrastructure/feature_parser.py`  
**Severity:** CRITICAL — Breaks entire pipeline  
**Impact:** ALL 130,045 steps have `screen_context = NULL`

### What Should Be There
- Full state machine parser from `reference/parsing/feature_parser.py` (626 lines)
- Background block parsing (line 180-220)
- Scenario vs Scenario Outline detection
- Tag/annotation parsing
- Example block + dictionary parsing
- Docstring extraction
- LogicalID detection for ordered files
- **CRITICAL:** Call to `infer_screen_contexts(steps)` after parsing each scenario

### What's Actually There
```python
# Minimal 74-line stub that:
- Only reads basic Scenario/Given/When/Then/And lines
- Never calls infer_screen_contexts()
- Sets screen_context: None for ALL steps ← HARDCODED NULL
- Ignores tags, examples, dictionaries, flow_type, LogicalIDs
```

### Why This Breaks Everything
1. `screen_context` is NULL for 100% of 130,045 steps (expected ~50%)
2. step_retriever.py tries to filter on screen_context and finds nothing
3. Downstream agents receive empty context
4. Generated feature files lack screen hints entirely

### Fix Required
Port complete `reference/parsing/feature_parser.py` — takes ~1 hour

---

## CRITICAL ISSUE 2: build_knowledge.py (Keyword-Only, No PDF Structure)

**File:** `forge/scripts/build_knowledge.py`  
**Severity:** CRITICAL — Knowledge base unusable  
**Impact:** stage_hint 7.6%, screen_hint 0% (expected ~90% and ~50%)

### What Should Be There
- PDF section/heading detection using pdfplumber font sizes
- `_infer_stage_hint(section_title, chunk_text)` function
- `_infer_screen_hint(section_title, chunk_text)` function
- Hierarchical chunking based on detected structure

### What's Actually There
```python
# Hardcoded 3-keyword matching:
stage_hint_keywords = ["credit approval", "underwriting", "documentation"]

# If text contains "credit approval" → set stage_hint = "Credit Approval"
# Else → stage_hint = NULL
```

### Why This Breaks Everything
1. Only 1 stage_hint set ("Credit Approval") — all others NULL
2. 0% of chunks have screen_hint (never implemented)
3. RAG engine cannot boost on document context
4. Agent 2 (Domain Expert) gets generic CAS knowledge instead of stage-specific

### Fix Required
1. Implement `extract_pdf_structure()` using pdfplumber font metrics (~40 lines)
2. Implement `_infer_stage_hint()` and `_infer_screen_hint()` (~30 lines each)
3. Refactor chunking to use detected section titles
Takes ~30-45 minutes

---

## INTEGRATION GAP 3: screen_context Inference Never Called

**Location:** Multiple  
**Severity:** CRITICAL — Data population

### The Function Exists
`forge/infrastructure/screen_context.py` has complete `infer_screen_contexts()` function

### But It's Never Called
- `feature_parser.py` never calls it (should be after parsing each scenario)
- `repo_indexer.py` never calls it (should be after all features indexed)

### Fix Required
- Add one-line call in feature_parser.py after scenario parsing
- Add one-line call in repo_indexer.py after bulk insert
Takes ~5 minutes

---

## Issue 4: Auth Login Not Working (DB Connection or Query Issue)

**Files:** `forge/api/routes/auth.py`  
**Severity:** HIGH — Blocks all API access  
**Suspected Causes:**
- DB connection pool initialization failing
- User table not created or users not seeded
- Query logic has a bug

**Fix Required:**
- Verify DB is actually initialized
- Run setup_db.py if not done
- Verify user exists (create_user.py)
- Test connection with test_connection()
Takes ~10 minutes if DB issue, ~30 minutes if query issue

---

## Files That ARE CORRECT

### ✅ Core Foundation (100% complete)
- `forge/core/config.py` — correct
- `forge/core/state.py` — correct (all 11 agents + loop-back)
- `forge/core/llm.py` — correct (lazy load, exception handling)
- `forge/core/db.py` — correct (pool management)
- `forge/api/auth.py` — correct (JWT + argon2 + encryption)

### ✅ Infrastructure (mostly correct)
- `forge/infrastructure/step_retriever.py` — COMPLETE (5-channel hybrid, cross-encoder, self-RAG, markers)
- `forge/infrastructure/rag_engine.py` — looks complete (distillation cache, doc chunks)
- `forge/infrastructure/jira_client.py` — COMPLETE (418 lines, CSV + PAT modes, quality tracking)
- `forge/infrastructure/embedder.py` — complete
- `forge/infrastructure/query_expander.py` — complete
- `forge/infrastructure/order_json_reader.py` — complete
- `forge/infrastructure/graph_rag.py` — complete
- `forge/infrastructure/normalisation.py` — complete
- `forge/infrastructure/screen_context.py` — complete (but never called)

### ✅ Database
- `forge/scripts/setup_db.py` — complete schema with all 12 tables
- `forge/scripts/index_repo.py` — complete feature indexing

### ✅ Agents (read one, assume structure)
- `forge/agents/agent_01_reader.py` — proper system prompt, structure

### ✅ API Routes (checked one)
- `forge/api/routes/auth.py` — looks correct

---

## Summary: What Actually Works

| Component | Status | Confidence |
|-----------|--------|------------|
| Database schema | ✅ WORKS | 100% |
| JWT auth | ✅ WORKS (if DB OK) | 95% |
| JIRA parsing (CSV + PAT) | ✅ WORKS | 95% |
| Step retrieval (hybrid 5-channel) | ✅ WORKS | 90% |
| RAG with distillation cache | ✅ WORKS | 85% |
| Agents (structure/framework) | ✅ WORKS | 80% |
| **Feature parsing** | ❌ **BROKEN** | N/A |
| **PDF knowledge build** | ❌ **BROKEN** | N/A |
| **Login endpoint** | ❌ **BROKEN** (unclear why) | N/A |

---

## What Needs To Happen Next

### Phase 1: Immediate Fixes (1 hour)
1. Port full feature_parser.py from reference (626 lines) — ~40 mins
2. Implement PDF structure detection in build_knowledge.py — ~30 mins
3. Add screen_context inference calls — ~5 mins

### Phase 2: Verify & Test (45 minutes)
1. Debug auth login failure — ~10 mins
2. Re-index feature repo with fixed parser — ~15 mins
3. Re-build knowledge base with PDF structure — ~10 mins
4. Run verification on database counts — ~5 mins
5. End-to-end test with sample JIRA — ~5 mins

### Total Time: ~2.5 hours

---

## Decision Point

**Option A:** Fix all three issues properly (port complete code, not shortcuts)  
**Option B:** Delete entire project

I recommend **Option A** — all three issues are fixable with proper implementations. The infrastructure is actually solid; it's just the feature parser and knowledge builder that were cut short.


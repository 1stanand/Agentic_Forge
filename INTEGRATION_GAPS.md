# Integration Gaps Report

**Status:** 3 Critical gaps found  
**Date:** 2026-04-27  
**Scope:** Missing function calls in data enrichment pipeline

---

## Summary

The codebase has all infrastructure functions **implemented** but not all are **called** from their integration points. This creates a pipeline where partial data is indexed and retrieved.

| Component | Function Exists | Function Called | Gap |
|-----------|-----------------|-----------------|-----|
| screen_context.py | ✅ `infer_screen_contexts()` | ❌ Never called | **HIGH** |
| build_knowledge.py | ❌ No PDF structure extraction | N/A | **HIGH** |
| feature_parser.py | ❌ No stage_hint population | N/A | **MEDIUM** |

---

## Gap 1: screen_context Not Inferred During Parsing

**File:** `forge/infrastructure/feature_parser.py`  
**Missing Call:** `infer_screen_contexts(scenario_steps)`  
**Expected Location:** After each scenario is closed, before storing in DB

**Impact:**
- **Expected:** 130,045 steps with ~50%+ having screen_context populated
- **Actual:** 130,045 steps with **0% screen_context** (all NULL)
- **Consequence:** Step retriever cannot boost on screen context, reducing ranking quality

**Function That Should Call It:**
```python
# In feature_parser.py parse_file() or in repo_indexer.py db_insert_feature():
# After building each scenario:
from forge.infrastructure.screen_context import infer_screen_contexts
scenario['steps'] = infer_screen_contexts(scenario['steps'])
```

**Root Cause:** Minimal parser implementation didn't integrate enrichment logic. Called during initial build but never tested/verified.

---

## Gap 2: PDF Structure Not Extracted for stage_hint/screen_hint

**File:** `forge/scripts/build_knowledge.py`  
**Missing Function:** PDF section/heading detection  
**Expected Location:** During PDF extraction loop

**Impact:**
- **Expected:** 800 chunks with ~90%+ having stage_hint, ~50%+ having screen_hint
- **Actual:** 800 chunks with **7.6% stage_hint**, **0% screen_hint**
- **Consequence:** RAG retrieval cannot boost on doc metadata, reducing context quality

**Spec Requirement (FORGE_SRS.md §4.6):**
```
For each PDF:
  1. Extract text page by page
  2. Detect section titles from font size/formatting  ← NOT IMPLEMENTED
  3. _infer_stage_hint(section_title, chunk_text)   ← NOT IMPLEMENTED
  4. _infer_screen_hint(section_title, chunk_text)  ← NOT IMPLEMENTED
```

**Current Implementation:** Only keyword-matching ("credit approval" in text)

**Root Cause:** pdfplumber integration incomplete. Font/formatting detection not added.

---

## Gap 3: Stage Hints Not Inferred During Feature Parsing

**File:** `forge/infrastructure/feature_parser.py`  
**Missing Call:** `_infer_stage_hint()` from domain/formatting analysis  
**Expected Location:** When step text is parsed

**Impact:**
- **Expected:** Steps with stage_hint populated from feature annotations
- **Actual:** steps.stage_hint is NULL for all 130,045 steps
- **Consequence:** Weak stage context for retrieval boosting

**Root Cause:** Feature parser doesn't analyze tags/annotations for stage information. Only basic Gherkin parsing done.

---

## Detailed Verification

### Current State

```sql
-- Steps table context
SELECT COUNT(*) as total,
       COUNT(screen_context) as with_context,
       ROUND(100.0 * COUNT(screen_context) / COUNT(*), 1) as percent_populated
FROM steps;
-- Result: total=130045, with_context=0, percent=0.0%

-- Doc chunks context
SELECT COUNT(*) as total,
       COUNT(stage_hint) as with_stage,
       COUNT(screen_hint) as with_screen
FROM doc_chunks;
-- Result: total=800, with_stage=61, with_screen=0
```

### Expected State (per FORGE_SRS.md)

| Table | Field | Current | Expected | Gap |
|-------|-------|---------|----------|-----|
| steps | screen_context | 0% | ~50% | **-100%** |
| steps | stage_hint | 0% | ~30% | **-100%** |
| doc_chunks | stage_hint | 7.6% | ~90% | **-82.4%** |
| doc_chunks | screen_hint | 0% | ~50% | **-100%** |

---

## Why This Matters

### Retrieval Quality

**Without context hints:**
- step_retriever can't boost on stage match (1.6× bonus)
- rag_engine can't boost on document section match (1.5× bonus)
- Query context is ignored; ranking is purely semantic similarity

**With context hints:**
- Relevant stages ranked higher
- User's current navigation context considered
- Fewer spurious results

### Example

```
Query: "approve application"
Current stage: "Credit Approval"
Screen: "Recommendation"

Without hints: Returns steps from any stage/screen
With hints:    Returns steps from Credit Approval screen first
```

---

## Fix Strategy

### Fix 1: Add Screen Context Inference (Step 1)

**File:** `forge/infrastructure/feature_parser.py`  
**Lines:** After scenario steps are parsed, before returning

```python
from forge.infrastructure.screen_context import infer_screen_contexts

# In parse_file() after each scenario closes:
for scenario in scenarios:
    scenario['steps'] = infer_screen_contexts(scenario['steps'])
    # Now steps have screen_context populated
```

**Effort:** ~5 lines, one import  
**Data Impact:** Will repopulate 0 → ~50% of screen_context on next re-index

---

### Fix 2: Add PDF Structure Detection (Step 2)

**File:** `forge/scripts/build_knowledge.py`  
**Current:** Keyword-match only  
**Needed:** Font size / section heading detection via pdfplumber

```python
# Detect section headings using pdfplumber font info
def extract_pdf_structure(page):
    """Extract headings and structure from page font metrics."""
    structures = []
    for text_obj in page.chars:
        if text_obj['size'] > 12:  # Likely a heading
            # Extract and normalize
            structures.append({
                'text': text_obj['text'],
                'font_size': text_obj['size'],
                'is_heading': text_obj['size'] > avg_body_size
            })
    return structures
```

**Effort:** ~40-50 lines  
**Data Impact:** Will populate ~90% of stage_hint, ~50% of screen_hint on next build

---

### Fix 3: Stage Hints in Features (Step 3, Optional)

**File:** `forge/infrastructure/feature_parser.py`  
**Needed:** Parse feature file tags/annotations for stage info

```python
# Extract stage from @CAS_StoryID_Stage tags
def extract_stage_from_tags(file_tags):
    """Extract stage from ordered flow tags."""
    for tag in file_tags:
        if "_" in tag:
            parts = tag.split("_")
            if len(parts) >= 3:
                return parts[2]  # The stage part
    return None
```

**Effort:** ~10 lines  
**Data Impact:** Will populate stage_hint for steps in ordered flows

---

## Recommendation

**Priority:** Fix all three before production testing

**Order:**
1. **Fix 1** (screen_context) — 15 minutes, high ROI
2. **Fix 2** (PDF structure) — 30 minutes, high ROI  
3. **Fix 3** (stage hints) — 10 minutes, medium ROI

**After fixes:**
- Run `python -m forge.scripts.index_repo --full-rebuild`
- Run `python -m forge.scripts.build_knowledge`
- Verify: `SELECT COUNT(*) as with_screen FROM steps WHERE screen_context IS NOT NULL`
- Should see: 50000-65000 (instead of 0)

---

## Testing

After fixes, verify with:

```sql
-- Check steps context
SELECT COUNT(*) as total, COUNT(screen_context) as with_context, 
       ROUND(100.0 * COUNT(screen_context) / COUNT(*), 1) as pct
FROM steps;
-- Expected: pct >= 40

-- Check doc chunks
SELECT COUNT(*) as total, COUNT(stage_hint) as with_stage, COUNT(screen_hint) as with_screen
FROM doc_chunks;
-- Expected: with_stage >= 700, with_screen >= 300
```

---

## Files Affected

| File | Lines | Type | Complexity |
|------|-------|------|------------|
| feature_parser.py | ~5 | Add call | Low |
| build_knowledge.py | ~50 | Add function + call | Medium |
| screen_context.py | 0 | No change | N/A |
| rag_engine.py | 0 | No change | N/A |
| step_retriever.py | 0 | No change | N/A |

---

**Report Status:** Ready for remediation  
**Estimated Fix Time:** ~1 hour for all three  
**Risk:** Low (additive, no breaking changes)

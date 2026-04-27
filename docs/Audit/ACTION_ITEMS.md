# AUDIT ACTION ITEMS — PRIORITIZED FIX LIST

**Audit Date:** April 27, 2026  
**Owner:** Anand (Domain Expert) + Claude Code (Implementation)  
**Target Date:** May 10, 2026 (2 weeks)

---

## PHASE 1: CRITICAL FIXES (2-3 days) — BLOCKING DEPLOYMENT

### [ ] CRITICAL-1: Fix Database Cursor Transaction Safety
**File:** `forge/core/db.py` (lines 44-60)  
**Owner:** Claude Code  
**Effort:** 1-2 hours  
**Why:** Data corruption risk on transaction failure

**Action:**
```python
# Replace get_cursor() context manager with:
@contextmanager
def get_cursor(conn, dict_cursor=True):
    cursor = None
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor if dict_cursor else None)
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        if cursor:
            cursor.close()
```

**Verification:** Run unit test on transaction failure path

---

### [ ] CRITICAL-2: PAT Encryption Key Validation at Startup
**File:** `forge/core/config.py` + `forge/api/main.py`  
**Owner:** Claude Code  
**Effort:** 2-3 hours  
**Why:** Missing keys crash on first use; no clear error message

**Action:**
1. Add `validate_encryption_key()` function to config.py
2. Call validation in `app.on_event("startup")` 
3. Raise clear ValueError if key invalid
4. Provide key generation instructions in error message

**Verification:** Test with invalid key in .env, verify error is clear

---

### [ ] CRITICAL-3: Remove Plaintext PAT Fallback
**File:** `forge/infrastructure/jira_client.py` (lines 399-409)  
**Owner:** Claude Code  
**Effort:** 2-3 hours  
**Why:** **SECURITY VIOLATION** — PAT must never be plaintext

**Action:**
1. Remove fallback to `settings.jira_pat` (plaintext)
2. Require encrypted PAT from user_settings table only
3. Create `forge/scripts/encrypt_pat.py` for one-time key generation
4. Update `.env.example` to remove `JIRA_PAT` field
5. Document in `docs/SETUP.md`

**Verification:** Test PAT flow with encrypted storage only

---

### [ ] CRITICAL-4: Create run_acceptance_tests.py
**File:** `forge/scripts/run_acceptance_tests.py` (NEW)  
**Owner:** Claude Code  
**Effort:** 4-5 hours  
**Why:** No demo validation; no way to verify before deployment

**Action:**
Create script with 10 golden tests:
1. Valid login returns JWT
2. Invalid JWT returns 401
3. CSV unordered generation (check Background, dicts, no @Order)
4. CSV ordered generation (check @Order, LogicalID, no Background)
5. Marker preservation: [NEW_STEP_NOT_IN_REPO]
6. Marker preservation: [LOW_MATCH]
7. Marker preservation: [ROLE_GAP]
8. Order.json validation failure (Agent 8 hard fail)
9. Missing LLM model (clear error, server up)
10. SSE stream authentication + valid JSON

**Verification:** Run script, all 10 tests pass

---

### [ ] CRITICAL-5: Remove Debug Print Statements
**File:** `forge/api/routes/auth.py` (lines 16-45)  
**Owner:** Claude Code  
**Effort:** 30 minutes  
**Why:** **SECURITY VIOLATION** — Credentials logged to stdout

**Action:**
1. Find all `print()` statements in auth.py
2. Remove them
3. Use `logger.debug()` if debug logging needed (respects log level)
4. Audit entire codebase for debug prints in other routes

**Verification:** Run grep for `print(` in forge/, verify none remain

---

### [ ] CRITICAL-6: Fix State TypedDict Mismatch
**File:** `forge/core/state.py` (entire)  
**Owner:** Claude Code  
**Effort:** 2-3 hours  
**Why:** LangGraph execution fails between agents; type validation breaks

**Action:**
1. Read FORGE.md Section 6 again carefully
2. Align state.py field names and types exactly:
   - Agent 1 → `jira_facts: Dict[str, Any]`
   - Agent 2 → `domain_brief: Dict[str, Any]`
   - ... (all 11)
   - Agent 9 → `feature_file: str` (NOT Dict!)
   - Agent 10 → `critique: Dict[str, Any]` (NOT critic_review)
   - Agent 11 → `final_output: Dict[str, Any]`
3. Verify all type hints match

**Verification:** Run state.py validation test, pass all type checks

---

### [ ] CRITICAL-7: Fix SSE Stream JSON Escaping
**File:** `forge/api/routes/generate.py` (lines 136, 143, 163, 171)  
**Owner:** Claude Code  
**Effort:** 1-2 hours  
**Why:** Invalid JSON breaks client-side parsing

**Action:**
```python
import json

# Replace all: yield f'data: {{"status": "...", "reason": "{error}"}}\n\n'
# With: event = json.dumps({...})
#       yield f'data: {event}\n\n'
```

**Verification:** Run with error conditions, verify client JSON.parse() succeeds

---

### [ ] CRITICAL-8: Stub Check — Agent Implementations
**File:** `forge/agents/agent_01.py` through `agent_11.py`  
**Owner:** Claude Code  
**Effort:** 15-20 hours (parallelizable — work on 2-3 agents in parallel)  
**Why:** Without all 11 agents, no generation jobs succeed

**Action for each agent:**
1. Verify exists and is not a stub
2. Has complete system prompt (ROLE, CONTEXT, JOB, OUTPUT, RULES, HARD BANS)
3. Calls LLM with `llm_complete()`
4. Validates JSON response with try-except
5. Logs input summary and output summary
6. Never silently swallows exceptions
7. Returns best attempt with markers on failure
8. Matches state output key from FORGE.md Section 6

**Verification:** Run graph.py end-to-end, all agents execute

---

## PHASE 2: HIGH SEVERITY FIXES (4-5 days) — SPEC COMPLIANCE

### [ ] HIGH-1: Config Validation at Startup
**File:** `forge/api/main.py` (add startup event)  
**Owner:** Claude Code  
**Effort:** 2-3 hours  
**Why:** Missing paths/keys fail silently at runtime

**Action:**
1. Create `validate_configuration()` function
2. Check all required paths exist
3. Check SECRET_KEY is non-default
4. Check PAT_ENCRYPTION_KEY is valid
5. Check MAX_CONCURRENT_JOBS >= 1
6. Log warnings (not errors) for LLM model if not found
7. Raise RuntimeError if critical check fails

**Verification:** .env with missing FEATURES_REPO_PATH → clear error message

---

### [ ] HIGH-2: Agent JSON Validation
**File:** All agents (agent_01.py through agent_11.py)  
**Owner:** Claude Code  
**Effort:** 3-4 hours  
**Why:** Silent JSON parse failures → empty state → silent downstream failures

**Action:**
Every agent must wrap LLM response in try-except:
```python
try:
    result = json.loads(response)
except json.JSONDecodeError as e:
    logger.error(f"Agent XX: LLM returned invalid JSON:\n{response[:500]}")
    raise ValueError(f"Agent XX: JSON parse failed") from e

# Validate required fields exist
required = ["field1", "field2"]
missing = [f for f in required if f not in result]
if missing:
    raise ValueError(f"Agent XX: Missing required fields: {missing}")
```

**Verification:** Test with LLM returning invalid JSON, verify error is raised

---

### [ ] HIGH-3: SCREEN_NAME_MAP Dynamic Builder
**File:** `forge/infrastructure/screen_context.py`  
**Owner:** Claude Code  
**Effort:** 2-3 hours  
**Why:** Static map becomes stale as repo grows

**Action:**
1. Remove any static SCREEN_NAME_MAP dictionary
2. Implement `build_screen_name_map()` that queries unique_steps
3. Call after each index_repo.py run
4. Cache in session memory (not file)

**Verification:** Run index_repo, verify new screens added to map

---

### [ ] HIGH-4: Create forge/core/crypto.py
**File:** `forge/core/crypto.py` (NEW)  
**Owner:** Claude Code  
**Effort:** 1-2 hours  
**Why:** PAT crypto scattered across files; inconsistent handling

**Action:**
```python
# forge/core/crypto.py
def get_cipher() -> Fernet:
    """Get Fernet cipher from PAT_ENCRYPTION_KEY."""

def encrypt_pat(pat: str) -> str:
    """Encrypt PAT for storage."""

def decrypt_pat(encrypted: str) -> str:
    """Decrypt PAT from storage."""

def mask_pat(pat: Optional[str]) -> Optional[str]:
    """Return masked PAT for display."""
```

**Verification:** Use in auth.py and jira_client.py, test encrypt/decrypt

---

### [ ] HIGH-5: Agent 8 Order.json Validation
**File:** `forge/agents/agent_08_atdd_expert.py`  
**Owner:** Claude Code  
**Effort:** 3-4 hours  
**Why:** Silent test skip — if scenario tags don't match Order.json, scenario is skipped at runtime

**Action:**
1. Load Order.json at startup
2. For each scenario in composed_scenarios (ordered flow):
   - Get effective_tags (file + scenario + example level)
   - Check if tags match any Order.json expression
   - If no match: hard ATDD failure (not warning)
3. Also validate:
   - No "But" keyword
   - Then + max 1 And
   - Scenario Outline if Examples present
   - Scenario titles describe behavior, not stages

**Verification:** Test with unmatched tags, verify Agent 8 fails with clear error

---

### [ ] HIGH-6: Verify Feature Parser Completeness
**File:** `forge/infrastructure/feature_parser.py` (complete port from V2)  
**Owner:** Claude Code  
**Effort:** 4-6 hours  
**Why:** Incomplete parsing → bad indexing → retrieval failures

**Checklist:**
- [ ] Background step accumulation (prepend to all subsequent scenarios)
- [ ] Doc string capture (append to preceding step)
- [ ] Header-based Examples parsing (not generic col_0/col_1)
- [ ] Dictionary parsing (`#${Key:["v1","v2"]}`)
- [ ] Conflict detection (`@Order` + dicts → error)
- [ ] Screen context inference via `_ANCHOR_PATTERNS`
- [ ] LogicalID marker detection
- [ ] BOM + non-UTF-8 encoding handling
- [ ] Skip `PickApplication.feature` and `OpenApplication.feature`

**Verification:** Run index_repo.py on test feature repo, verify all 9 extensions work

---

### [ ] HIGH-7: Standardize LLM Error Handling
**File:** All routes, all agents  
**Owner:** Claude Code  
**Effort:** 2-3 hours  
**Why:** Inconsistent error propagation; some endpoints crash on missing LLM

**Action:**
Every place that calls `llm_complete()` must:
```python
from forge.core.llm import LLMNotLoadedError

try:
    result = llm_complete(...)
except LLMNotLoadedError as e:
    logger.error(f"LLM not loaded")
    return {"error": "LLM model not loaded. Check LLM_MODEL_PATH in .env and restart."}
```

**Verification:** Test with LLM path invalid, verify all endpoints return clear error

---

### [ ] HIGH-8: Marker Preservation Validation
**File:** `forge/agents/agent_07.py`, `agent_09.py`, `agent_10.py`, `agent_11.py`  
**Owner:** Claude Code  
**Effort:** 2-3 hours  
**Why:** Markers drop silently → final output lacks gap signals

**Action:**
1. Agent 7 (Composer): preserve marker from Agent 6 in scenarios
2. Agent 9 (Writer): embed marker as inline comment in Gherkin
3. Agent 10 (Critic): preserve marker in critique output
4. Agent 11 (Reporter): preserve marker in final_output gap report

**Verification:** Generate feature file, verify markers appear as comments

---

### [ ] HIGH-9: Verify Admin Routes
**File:** `forge/api/routes/admin.py`  
**Owner:** Claude Code  
**Effort:** 1-2 hours  
**Why:** Admin functionality unclear

**Checklist:**
- [ ] POST /admin/users — create user (admin JWT required)
- [ ] GET /admin/users — list users (admin JWT required)
- [ ] DELETE /admin/users/{id} — deactivate user (admin JWT required)
- [ ] Proper response schemas
- [ ] Soft delete (deactivate, don't drop)

**Verification:** Test all 3 endpoints with admin token

---

### [ ] HIGH-10: Verify Chat Routes & Context Routing
**File:** `forge/api/routes/chat.py` + `forge/chat/router.py`  
**Owner:** Claude Code  
**Effort:** 2-3 hours  
**Why:** Chat context routing unclear; may be incomplete

**Checklist:**
- [ ] Router classifies message as cas | atdd | general
- [ ] CAS: calls rag_engine.get_context(), injects into prompt
- [ ] ATDD: loads CAS_ATDD_Context.md, injects into prompt
- [ ] General: uses Gemma knowledge only
- [ ] Returns response + context_type + session_title
- [ ] All 4 chat endpoints working (POST, GET list, GET one, DELETE)

**Verification:** Test message classification, verify context injected

---

## PHASE 3: MEDIUM SEVERITY FIXES (2-3 days) — QUALITY

### [ ] MEDIUM-1: Connection Pool Sizing
**File:** `forge/core/db.py` (line 12)  
**Owner:** Claude Code  
**Effort:** 1 hour  
**Action:** `maxconn = get_settings().max_concurrent_jobs * 2`

---

### [ ] MEDIUM-2: Step Retriever Complete Stack
**File:** `forge/infrastructure/step_retriever.py`  
**Owner:** Claude Code  
**Effort:** 4-5 hours  
**Action:** Verify all 9 steps implemented per FORGE_SRS.md 4.2

---

### [ ] MEDIUM-3: RAG Engine Stage/Screen Boosting
**File:** `forge/infrastructure/rag_engine.py`  
**Owner:** Claude Code  
**Effort:** 1-2 hours  
**Action:** Add boosting logic per FORGE_SRS.md 4.3 Step 5

---

### [ ] MEDIUM-4: Cross-Encoder Error Handling
**File:** `forge/infrastructure/step_retriever.py`  
**Owner:** Claude Code  
**Effort:** 30 minutes  
**Action:** Raise exception on cross-encoder load failure (not silent)

---

### [ ] MEDIUM-5: Job Runner Cleanup/TTL
**File:** `forge/core/job_runner.py`  
**Owner:** Claude Code  
**Effort:** 2-3 hours  
**Action:** Add 24-hour TTL on _active_jobs, cleanup task

---

### [ ] MEDIUM-6: Test Fixtures
**File:** `tests/fixtures/` (NEW)  
**Owner:** Anand + Claude Code  
**Effort:** 3-4 hours  
**Action:** Create CSV samples + expected outputs for golden tests

---

### [ ] MEDIUM-7: Feature Parser Encoding Handling
**File:** `forge/infrastructure/feature_parser.py`  
**Owner:** Claude Code  
**Effort:** 1-2 hours  
**Action:** Add BOM + encoding fallback per FORGE_SRS.md 4.5

---

## PHASE 4: VERIFICATION & DEPLOYMENT (2-3 days)

### [ ] Run verify_setup.py
**Command:** `python -m forge.scripts.verify_setup`  
**Expected:** All checks pass (18 items)

---

### [ ] Run acceptance tests
**Command:** `python -m forge.scripts.run_acceptance_tests`  
**Expected:** All 10 tests pass

---

### [ ] Run integration test
**Command:** `python -m forge.scripts.integration_test`  
**Expected:** Full CSV → feature file workflow succeeds

---

### [ ] Manual security audit
**Focus areas:**
- [ ] No plaintext PATs anywhere
- [ ] No credentials in logs
- [ ] All secrets validated at startup
- [ ] CORS configured (not "*")
- [ ] Input validation on CSV parsing

---

### [ ] Load testing
**Test:** 5 concurrent generation jobs  
**Verify:** Connection pool doesn't exhaust, jobs complete successfully

---

## TRACKING

### When Each Phase Completes, Update:
1. `CONTEXT.md` — current status
2. `CHANGELOG.md` — append handoff log entry
3. This file — mark items as complete

### Sign-Off Criteria:
- [ ] All CRITICAL issues fixed
- [ ] All HIGH issues fixed
- [ ] All tests pass (acceptance + integration)
- [ ] Security audit passed
- [ ] Load test successful
- [ ] Ready for demo deployment

---

**Last Updated:** April 27, 2026  
**Next Review:** May 3, 2026 (Phase 1 completion)

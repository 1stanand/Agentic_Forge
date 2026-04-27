# AUDIT COMPLIANCE STRATEGIC PLAN

**Date Created:** April 27, 2026  
**Audit Scope:** 44 issues (8 CRITICAL, 12 HIGH, 15 MEDIUM, 9 LOW)  
**Target:** 70% → 100% specification compliance  
**Timeline:** 2 weeks (parallelizable)

---

## QUICK STATUS

| Phase | Issues | Status | Effort | Target |
|-------|--------|--------|--------|--------|
| **CRITICAL** | 8 | 🔴 Not started | 2–3 days | Blocks deployment |
| **HIGH** | 12 | 🔴 Not started | 4–5 days | Spec compliance |
| **MEDIUM** | 15 | 🔴 Not started | 2–3 days | Quality |
| **LOW** | 9 | 🔴 Not started | 1–2 days | Style/minor |
| **VERIFICATION** | — | 🔴 Not started | 2–3 days | Test all fixes |

**Total Effort:** ~13 hours dev + ~2 weeks including testing

---

## PHASE 1 — CRITICAL FIXES (MUST DO FIRST)

These 8 issues **block deployment**. One breaks the pipeline, one opens a security hole.

### Blockers (Will Crash)

| # | Issue | File | Effort | Status | Notes |
|---|-------|------|--------|--------|-------|
| **CRIT-1** | State TypedDict keys mismatch | `forge/core/state.py` | 30 min | ⬜ | Agent 8→9 handoff crashes on KeyError |
| **CRIT-2** | DB cursor no rollback on failure | `forge/core/db.py` | 1 hr | ⬜ | Data corruption risk; add try-except-finally |
| **CRIT-3** | Agent 8 writes wrong state keys | `forge/agents/agent_08_atdd_expert.py` | 30 min | ⬜ | Writes `validation_result` instead of `reviewed_scenarios` |
| **CRIT-4** | Agent 9 type error on state access | `forge/agents/agent_09_writer.py` | 30 min | ⬜ | Expects List, gets Dict; .get() on List crashes |
| **CRIT-5** | Background generation violates spec | `forge/agents/agent_09_writer.py` | 20 min | ⬜ | Must generate hardcoded "Given user is on CAS Login Page" |

### Security (Will Expose Data)

| # | Issue | File | Effort | Status | Notes |
|---|-------|------|--------|--------|-------|
| **CRIT-6** | Debug print statements logging credentials | `forge/api/routes/auth.py` | 30 min | ⬜ | Remove all `print()` in auth routes |
| **CRIT-7** | Plaintext JIRA PAT fallback | `forge/infrastructure/jira_client.py` | 1 hr | ⬜ | Remove plaintext, require encrypted only |
| **CRIT-8** | PAT encryption key not validated at startup | `forge/core/config.py` + `forge/api/main.py` | 1 hr | ⬜ | Add startup validation, clear error message |

### PHASE 1 Dependencies

```
CRIT-1 (State) ──┐
                 ├─→ CRIT-3, CRIT-4 (Agents depend on state structure)
                 └─→ Graph pipeline end-to-end test

CRIT-2 (DB) ────→ All generation jobs (transaction safety)

CRIT-5 (Background) ────→ Feature file output correctness

CRIT-6, CRIT-7, CRIT-8 (Security) ────→ Production readiness
```

**Phase 1 Completion Criteria:**
- [ ] All 8 fixes committed
- [ ] Graph end-to-end test passes (all agents execute)
- [ ] No debug print output
- [ ] Startup validation rejects invalid PAT key
- [ ] Generated feature files contain correct Background step

---

## PHASE 2 — HIGH SEVERITY FIXES (SPEC COMPLIANCE)

These 12 issues violate specification or create security/quality gaps.

| # | Issue | File | Effort | Category | Status | Notes |
|---|-------|------|--------|----------|--------|-------|
| **HIGH-1** | Missing prerequisite step in ordered flows | `forge/agents/agent_05_action_decomposer.py` | 1 hr | Spec | ⬜ | HARD RULE: "Given all prerequisite are performed in previous scenario..." |
| **HIGH-2** | "But" keyword hard ban not enforced | All agents | 1 hr | Spec | ⬜ | Agents must explicitly ban "But" in prompts + validate output |
| **HIGH-3** | Then+And hard ban not enforced | `forge/agents/agent_09_writer.py` | 1 hr | Spec | ⬜ | Max 1 And per Then block; hard fail if violated |
| **HIGH-4** | Agent 5 validation errors not enforced | `forge/agents/agent_05_action_decomposer.py` | 1 hr | Quality | ⬜ | Log warning but continue — should RAISE |
| **HIGH-5** | Agent 2 RAG silent failure | `forge/agents/agent_02_domain_expert.py` | 30 min | Quality | ⬜ | Downgrades gracefully; should surface error |
| **HIGH-6** | Agent 8 Order.json validation not hard-fail | `forge/agents/agent_08_atdd_expert.py` | 2 hr | Spec | ⬜ | Unmatched tags = agent hard failure |
| **HIGH-7** | Order.json boolean matching broken | `forge/infrastructure/order_json_reader.py` | 1 hr | Critical bug | ⬜ | String replace doesn't handle boolean logic; use proper eval |
| **HIGH-8** | Config validation at startup missing | `forge/api/main.py` | 1 hr | Quality | ⬜ | Check all required paths, keys, SCREEN_NAME_MAP |
| **HIGH-9** | SSE stream JSON not properly escaped | `forge/api/routes/generate.py` | 1 hr | Quality | ⬜ | Events must be valid JSON; use `json.dumps()` |
| **HIGH-10** | Admin routes unclear | `forge/api/routes/admin.py` | 1 hr | Quality | ⬜ | Verify POST/GET/DELETE user endpoints |
| **HIGH-11** | Chat context routing incomplete | `forge/chat/router.py` | 1 hr | Quality | ⬜ | Verify CAS/ATDD/general classification |
| **HIGH-12** | Missing run_acceptance_tests.py | `forge/scripts/run_acceptance_tests.py` | 3 hr | Verification | ⬜ | 10 golden tests; no way to verify before demo |

**Phase 2 Completion Criteria:**
- [ ] All 12 fixes implemented
- [ ] Acceptance tests pass (all 10)
- [ ] Generated ordered flows include prerequisite step
- [ ] Order.json expressions correctly evaluate
- [ ] SSE stream produces valid JSON events

---

## PHASE 3 — MEDIUM SEVERITY FIXES (CODE QUALITY)

These 15 issues are maintainability, best practices, error handling.

| # | Issue | File | Effort | Status |
|---|-------|------|--------|--------|
| MEDIUM-1 | Connection pool sizing | `forge/core/db.py` | 30 min | ⬜ |
| MEDIUM-2 | Step retriever complete stack | `forge/infrastructure/step_retriever.py` | 3 hr | ⬜ |
| MEDIUM-3 | RAG engine stage/screen boosting | `forge/infrastructure/rag_engine.py` | 1 hr | ⬜ |
| MEDIUM-4 | Cross-encoder error handling | `forge/infrastructure/step_retriever.py` | 30 min | ⬜ |
| MEDIUM-5 | Job runner cleanup/TTL | `forge/core/job_runner.py` | 2 hr | ⬜ |
| MEDIUM-6 | Test fixtures | `tests/fixtures/` | 2 hr | ⬜ |
| MEDIUM-7 | Feature parser encoding handling | `forge/infrastructure/feature_parser.py` | 1 hr | ⬜ |
| MEDIUM-8 | Agent JSON validation | All agents | 2 hr | ⬜ |
| MEDIUM-9 | Marker preservation validation | `forge/agents/agent_07,09,10,11.py` | 1 hr | ⬜ |
| MEDIUM-10 | Chat routes verification | `forge/api/routes/chat.py` | 1 hr | ⬜ |
| MEDIUM-11 | SCREEN_NAME_MAP dynamic builder | `forge/infrastructure/screen_context.py` | 1 hr | ⬜ |
| MEDIUM-12 | LLM error handling standardized | All routes/agents | 1 hr | ⬜ |
| MEDIUM-13 | Settings routes complete | `forge/api/routes/settings.py` | 1 hr | ⬜ |
| MEDIUM-14 | Verify feature parser completeness | `forge/infrastructure/feature_parser.py` | 2 hr | ⬜ |
| MEDIUM-15 | Plaintext secrets cleanup | All files | 30 min | ⬜ |

**Phase 3 Effort:** ~20 hours (low risk, good for parallelization)

---

## PHASE 4 — VERIFICATION & DEPLOYMENT (2–3 days)

| # | Task | Command | Status |
|---|------|---------|--------|
| **V-1** | Startup validation | `python -m forge.scripts.verify_setup` | ⬜ |
| **V-2** | Acceptance tests | `python -m forge.scripts.run_acceptance_tests` | ⬜ |
| **V-3** | Integration test (CSV → feature file) | Manual CSV test | ⬜ |
| **V-4** | Manual security audit | Code review + grep scans | ⬜ |
| **V-5** | Load test (5 concurrent jobs) | Custom script | ⬜ |
| **V-6** | Demo readiness sign-off | All above pass | ⬜ |

---

## DEPENDENCIES & BLOCKING RELATIONSHIPS

```
PHASE 1 (CRITICAL) must complete before PHASE 2
├─ CRIT-1 (State) unlocks CRIT-3, CRIT-4
├─ CRIT-2 (DB) unlocks generation pipeline
├─ CRIT-5 (Background) unlocks feature file output
└─ CRIT-6,7,8 (Security) unlocks production readiness

    ↓

PHASE 2 (HIGH) can run in parallel with rest of PHASE 1
├─ HIGH-1 (Prerequisite step) unlocks ordered flow validation
├─ HIGH-6,7 (Order.json) unlock ordered flow generation
└─ HIGH-8 (Startup validation) unlocks verify_setup

    ↓

PHASE 3 (MEDIUM) runs in parallel with PHASE 2
└─ No hard blockers; best-effort quality improvements

    ↓

PHASE 4 (VERIFICATION) runs only after PHASE 1,2,3 complete
└─ All acceptance tests must pass before demo
```

---

## TRACKING & STATUS UPDATES

### Session Progress Template

At end of each session, update this file:

```markdown
## Session [N] — [Date] — [Status]

### What Was Fixed
- CRIT-1: State TypedDict
- CRIT-2: DB cursor
- ...

### What Passed Verification
- Graph end-to-end test ✓
- Acceptance tests (7/10 pass)
- ...

### Blockers
- Agent 8 output format unclear — clarified
- ...

### Next Session
- Start PHASE 2 fixes
- Estimated: 2 days remaining
```

### Sign-Off Checklist

**Ready for demo when:**
- [ ] All CRITICAL (8) fixed
- [ ] All HIGH (12) fixed
- [ ] All acceptance tests pass (10/10)
- [ ] Security audit passed
- [ ] Load test successful (5 concurrent)
- [ ] Anand approves output against spec

**Current Score:** 0/44 fixed (0%)

---

## KEY REFERENCES

| Document | Use For |
|----------|---------|
| `ACTION_ITEMS.md` | Detailed task breakdown + code snippets |
| `CODE_LEVEL_AUDIT.md` | Exact file:line + before/after code |
| `SECURITY_VULNERABILITIES.md` | Security fixes + attack scenarios |
| `SECURITY_AND_QUALITY_AUDIT.md` | Full architectural context |
| `FINDINGS_SUMMARY.txt` | Executive overview |

---

## STRATEGIC NOTES

1. **Start with PHASE 1.** Do not move to PHASE 2 until all 8 blockers fixed.
2. **State.py first.** CRIT-1 unlocks everything downstream.
3. **Parallel in PHASE 2.** HIGH-1, HIGH-6, HIGH-7 can work in parallel with different developers.
4. **Acceptance tests after PHASE 2.** Don't run them until prerequisite step + Order.json are fixed.
5. **Security audit before demo.** All CRITICAL-6,7,8 must be verified.
6. **Keep this file updated.** It's the single source of truth for progress.

---

## NEXT SESSION CHECKLIST

When you start the next session:

- [ ] Read this file first (5 min)
- [ ] Read CONTEXT.md to see previous progress
- [ ] Pick next unfinished item from PHASE 1
- [ ] Reference CODE_LEVEL_AUDIT.md for exact code changes
- [ ] After each fix: run relevant acceptance test
- [ ] Update this file with checkbox before moving to next item
- [ ] Append to CHANGELOG.md with what was completed

---

**Status:** READY FOR PHASE 1 FIXES  
**Last Updated:** April 27, 2026  
**Next Review:** Start of next session


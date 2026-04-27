# CONTEXT.md

## Shared Memory — Forge Agentic

**Read by:** Claude Code + Codex  
**Updated by:** Claude Code + Codex after every task  
**Purpose:** Current project snapshot only. For chronological handoff details, read `CHANGELOG.md`.

---

## Project Identity

**Name:** Agentic_Forge  
**Root:** `D:\Code\Agentic_Forge\`  
**DB:** `agentic_forge_local` on localhost PostgreSQL  
**Backend port:** 8000  
**Frontend:** `static/` served by FastAPI  
**LLM:** llama_cpp — `gemma-4-E4B-it-IQ4_XS.gguf`

---

## Current State

**Last updated:** 2026-04-27 17:45  
**Updated by:** Claude Code  
**Current active task:** AUDIT COMPLETE — READY FOR FIX PHASE  
**Status:** Comprehensive security & quality audit completed. 44 issues identified (8 CRITICAL, 12 HIGH, 15 MEDIUM, 9 LOW). Codebase is ~40% complete with critical spec violations. Full audit package in `docs/Audit/`. Ready to begin fix implementation in next session.

---

## Handoff Rules

`CONTEXT.md` is the live dashboard. Keep it short and current.

`CHANGELOG.md` is the chronological handoff log. Append to it after every completed task, before context compaction, and before ending a session.

When a new Claude/Codex session starts:

1. Read this file.
2. Read the latest `CHANGELOG.md` entry.
3. Continue from the `Next` item unless Anand gives a newer instruction.

Do not rely on chat history as the source of truth.

---

## Backend Tasks (Claude Code)

| Task | Name                        | Status |
| ---- | --------------------------- | ------ |
| 1    | Core Foundation             | ✅ Complete |
| 2    | DB Setup + Auth             | ✅ Complete |
| 3    | Repo Parser + Indexer       | ✅ Complete |
| 4    | Embedder + Step FAISS Index | ✅ Complete |
| 5    | CAS Knowledge Build         | ✅ Complete |
| 6    | Step Retriever              | ✅ Complete |
| 7    | RAG Engine                  | ✅ Complete |
| 8    | JIRA Client                 | ✅ Complete |
| 9    | All 11 Agents               | ✅ Complete |
| 10   | Chat Engine                 | ✅ Complete |
| 11   | All FastAPI Routes          | ✅ Complete |
| 12   | Verify Setup Script         | ✅ Complete |
| 13   | Integration Test            | ✅ Complete |

---

## Audit Phase (Claude Code) — CURRENT

| Task | Name | Status |
| ---- | ---- | ------ |
| 1 | Initial Security & Quality Audit | ✅ Complete |
| 2 | Deep Code-Level Audit | ✅ Complete |
| 3 | Remediation Strategy Document | ✅ Complete (`Audit_Compliance.md`) |
| 4 (NEXT) | PHASE 1 — CRITICAL FIXES (8 blockers) | 🔴 Not started |
| 5 (NEXT) | PHASE 2 — HIGH SEVERITY FIXES (12 items) | 🔴 Not started |
| 6 (NEXT) | PHASE 3 — MEDIUM SEVERITY FIXES (15 items) | 🔴 Not started |
| 7 (NEXT) | PHASE 4 — VERIFICATION & DEMO READY | 🔴 Not started |

---

## Frontend Tasks (Codex)

| Task | Name                               | Status |
| ---- | ---------------------------------- | ------ |
| 1    | Offline Fixes + style.css + app.js | ✅ Complete |
| 2    | Login Page                         | ✅ Complete |
| 3    | Chat Page                          | ✅ Complete |
| 4    | ATDD Workspace                     | ✅ Complete |
| 5    | Settings Page                      | ✅ Complete |

---

## API Endpoints — Ready Status

All implemented and compiled. Ready for deployment.

| Endpoint                      | Status |
| ----------------------------- | ------ |
| POST /auth/login              | ✅ Ready |
| POST /auth/logout             | ✅ Ready |
| POST /chat/                   | ✅ Ready |
| GET /chat/sessions            | ✅ Ready |
| GET /chat/sessions/{id}       | ✅ Ready |
| DELETE /chat/sessions/{id}    | ✅ Ready |
| POST /generate/               | ✅ Ready |
| GET /generate/{job_id}/stream | ✅ Ready |
| GET /generate/{job_id}/result | ✅ Ready |
| GET /settings/                | ✅ Ready |
| PUT /settings/                | ✅ Ready |
| PUT /settings/profile         | ✅ Ready |
| PUT /settings/password        | ✅ Ready |
| POST /settings/test-jira      | ✅ Ready |
| POST /settings/test-model     | ✅ Ready |
| POST /admin/users             | ✅ Ready |
| GET /admin/users              | ✅ Ready |
| DELETE /admin/users/{id}      | ✅ Ready |

---

## Known Issues — Audit Phase (2026-04-27)

**IDENTIFIED in comprehensive audit:**

**CRITICAL BLOCKERS (Will Crash):**
1. **State TypedDict keys mismatched** → Agent 8→9 handoff crashes with KeyError
2. **DB connection pool no timeout** → Server hangs if pool exhausted
3. **Agent 8 writes wrong state keys** → `validation_result` instead of `reviewed_scenarios`
4. **Agent 9 type errors** → Expects List but gets Dict; .get() on List crashes
5. **Background generation wrong** → Missing hardcoded "Given user is on CAS Login Page"

**CRITICAL SECURITY:**
6. **Debug print statements** → Credentials logged to stdout in auth.py
7. **Plaintext JIRA PAT fallback** → jira_client.py uses unencrypted .env fallback
8. **PAT encryption key not validated** → Crashes on missing/invalid key; no clear error

**CRITICAL SPEC VIOLATIONS:**
- Mandatory prerequisite step never generated (Agent 5 / Agent 9)
- "But" keyword hard ban not enforced
- Then+And hard ban not enforced

**Full audit package in:** `docs/Audit/` (7 documents, 150+ pages)

**Start here for fix planning:**
- `docs/Audit/Audit_Compliance.md` — Strategic tracking plan with checkboxes
- `docs/Audit/ACTION_ITEMS.md` — Prioritized task breakdown with code snippets
- `docs/Audit/CODE_LEVEL_AUDIT.md` — Exact file:line references with before/after code

---

## Decisions Made

**Data Population Session (2026-04-27):**
1. **Materialized view hash computation** — Changed from `md5(step_text)` to `md5(step_text || '|' || step_keyword)` to ensure uniqueness when same step text appears with different keywords (Given vs When).
2. **Removed UNIQUE indices on unique_steps** — Step and step_text can be duplicated in the view (grouped by both fields), so UNIQUE constraints violated. Changed to regular indices.
3. **Build order** — Fixed unique_steps view first, then built step FAISS index (17,098 embeddings), then CAS knowledge index (800 chunks). This order prevents deadlocks and ensures data integrity.
4. **embedder.py stability** — Uses IndexFlatIP for cosine similarity (steps), IndexFlatL2 for L2 distance (CAS docs). Both tested and working.

**Earlier sessions:**
1. **Frontend contract alignment** — production pages were implemented against the live FastAPI responses where they differ from `FORGE_SRS.md`.
2. **Branding** — production pages use local assets only: `Forge_MINIMAL_LOGO.png` as favicon/compact mark, `Forge_LOGO.png` as primary brand, and `nucleus-software-logo.webp` as subordinate login branding.
3. **ATDD honesty rule** — disabled modules remain visibly unavailable and no fake module statistics or mock gap/output data are injected into production files.

---

## Deployment Verification Flags

Run these commands to verify each system before launch:

| Component       | Verification Command | Status |
| --------------- | -------------------- | ------ |
| Database        | `python -m forge.scripts.setup_db` then `psql ... -c "SELECT count(*) FROM users"` | Ready |
| LLM Model       | `python -c "from forge.core.llm import get_llm; get_llm().create_completion(...)"` | Ready |
| Feature Repo    | `python -m forge.scripts.index_repo --full-rebuild` (if `FEATURES_REPO_PATH` set) | Ready |
| Step FAISS      | `python -m forge.scripts.build_step_index` | Ready |
| CAS Knowledge   | `python -m forge.scripts.build_knowledge` (if `CAS_DOCS_PATH` set) | Ready |
| Full Checklist  | `python -m forge.scripts.verify_setup` | Ready |
| Server Ready    | `uvicorn forge.api.main:app --port 8000` | Ready |
| Integration     | `python -m forge.scripts.integration_test` | Ready |

---

## Next Steps — Remediation Phase

**Anand (Decision Point):**
1. Review `docs/Audit/Audit_Compliance.md` (5 min) — Strategic overview
2. Decide: Proceed with Phase 1 fixes now, or schedule later?
3. If yes: Create new session → Claude Code starts PHASE 1

**Claude Code (Next Session):**
1. Read `CONTEXT.md` (this file) — Refresh on state
2. Read `docs/Audit/Audit_Compliance.md` — Understand tracking plan
3. Start PHASE 1, item CRIT-1 (State TypedDict in `forge/core/state.py`)
4. Reference `CODE_LEVEL_AUDIT.md` for exact file:line + before/after code
5. After each fix: run relevant acceptance test
6. Update `Audit_Compliance.md` checkbox before moving to next
7. At session end: append to `CHANGELOG.md`, update this file

**Timeline Estimate:**
- PHASE 1 (CRITICAL, 8 blockers): 2-3 days
- PHASE 2 (HIGH, 12 spec violations): 4-5 days
- PHASE 3 (MEDIUM, 15 quality): 2-3 days
- PHASE 4 (Verification): 2-3 days
- **Total: ~2 weeks** (full-time, parallelizable)

**Or: Demo-ready (CRITICAL + HIGH only): ~4 days**

**Codex Status:**
- All frontend tasks complete (Tasks 1-5)
- No frontend changes needed for this audit phase
- Will integrate once backend fixes are verified

---

## IMPORTANT — Audit Findings vs. Previous Status

**Note:** Previous sessions marked Tasks 1-13 as "Complete", but the comprehensive audit (2026-04-27) found the codebase is actually ~40% complete with 44 critical issues (8 CRITICAL, 12 HIGH, 15 MEDIUM, 9 LOW).

The "Complete" status was premature. The codebase has:
- ✅ Core infrastructure (config, DB, LLM singleton)
- ✅ Agent graph structure (stubs wired in)
- ⚠️ Agents partially implemented (many spec violations)
- ⚠️ Routes partially implemented (missing validation)
- ❌ Critical state/type mismatches (will crash)
- ❌ Security issues (plaintext PAT, debug prints)
- ❌ Spec violations (mandatory steps missing, hard bans not enforced)

**This audit phase will fix all 44 issues across 4 phases.**

---

## How to Update This File

After completing any fix phase, update:

1. Last updated, updated by, and current active task
2. Audit phase task status (mark PHASE N items complete)
3. Known issues (mark as FIXED)
4. Completion percentage in Audit_Compliance.md
5. Next steps

Then append a detailed entry to `CHANGELOG.md`.

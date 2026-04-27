# FORGE.md

## Complete Build Specification — Forge Agentic

**Project:** Agentic_Forge  
**From:** Anand (Domain Expert) + Claude (AI/ML Engineer)  
**Date:** April 2026  
**Status:** Final — Build from here

---

## READ THIS FIRST

This is the single source of architectural truth for Forge Agentic. Read it completely before writing a single line of code. Every decision here was made deliberately after a full build cycle. Do not improvise around it.

Companion documents in `docs/`:

- `CAS_ATDD_Context.md` — CAS domain knowledge. Agent system prompts depend on it.
- `FORGE_SRS.md` — Every API endpoint, DB table, and agent contract in detail.
- `HOW_TO_RUN.md` — Setup and run instructions per machine profile.

Reference code in `reference/` — V2 codebase. **Port the logic directly. Do not rewrite from scratch.** "Study and rewrite" produces downgrades. The reference files are the correct implementation — adapt imports and config references to V3, keep the logic faithful.

---

## 1. What Forge Is

Forge is the internal AI platform for Nucleus Software QA. Two capabilities:

**Forge Chat** — A domain-aware AI assistant. Testers ask CAS questions, paste JIRAs, get explanations. Fully offline. CAS-aware via the same document library that powers the ATDD agents. Conversation memory within and across sessions.

**Forge ATDD** — An 11-agent system that converts JIRA stories into ATDD feature files grounded in the real test repository. CAS module is active. LMS and Collections are Coming Soon placeholders.

Forge runs on a shared server. Multiple testers access it over the network. Every user has their own login, chat history, and sessions.

**North star:** As close to final draft as possible. Not replacing tester judgment. Handling mechanical thinking so tester domain knowledge goes where it actually matters.

### What Forge Is Not

- Not a generic Gherkin generator
- Not a pipeline — generation is a multi-agent system
- Not a replacement for the tester — a first-draft accelerator
- Not connected to the internet — fully offline, fully private
- Not using cloud APIs — ever

---

## 2. Three Machine Profiles

All configuration lives in `.env` only. The codebase is identical across machines. Only `.env` changes.

|             | Personal (Dev)   | Work (Demo)      | Future (Prod)    |
| ----------- | ---------------- | ---------------- | ---------------- |
| RAM         | 8GB              | 32GB             | 128GB            |
| GPU         | None             | None             | RTX 4090 24GB    |
| JIRA Access | No               | Yes              | Yes              |
| Node.js     | Yes              | No (restricted)  | Yes              |
| LLM         | Gemma 4 E4B GGUF | Gemma 4 E4B GGUF | Gemma 4 31B GGUF |
| LLM Runtime | llama_cpp        | llama_cpp        | llama_cpp        |
| Role        | Build + Test     | Demo             | Production       |

**No Ollama anywhere.** llama_cpp is the runtime on all three machines. This is final.

On Personal (dev) — JIRA mode unavailable. CSV mode is how generation is tested.  
On Work (demo) — JIRA PAT available. CSV mode also available.  
On Prod — Full capabilities.

---

## 3. Tech Stack — Locked

| Component         | Technology                           | Notes                                           |
| ----------------- | ------------------------------------ | ----------------------------------------------- |
| LLM (dev/demo)    | Gemma 4 E4B via llama_cpp            | GGUF format, CPU only                           |
| LLM (prod)        | Gemma 4 31B via llama_cpp            | GGUF format, RTX 4090                           |
| Orchestration     | LangGraph                            | Offline, open source                            |
| Vector Search     | FAISS                                | Step index + doc chunk index — built by scripts |
| Full Text Search  | PostgreSQL FTS + pg_trgm             | Schema built by setup scripts                   |
| Embeddings        | all-MiniLM-L6-v2                     | Offline, sentence-transformers                  |
| Reranker          | cross-encoder/ms-marco-MiniLM-L-6-v2 | CPU-friendly, offline                           |
| Knowledge Graph   | NetworkX                             | Stage → Screen → Entity → Rule                  |
| Backend           | FastAPI                              | Async REST API                                  |
| Auth              | JWT + argon2                         | Per-user sessions                               |
| Database          | PostgreSQL                           | DB name: agentic_forge_local                    |
| Frontend          | Vanilla HTML + CSS + JS              | No build step. No npm on server.                |
| JIRA Client       | jira-python                          | PAT auth + CSV fallback                         |
| Code Intelligence | CodeGraph (npm)                      | Initialized in repo root on dev machine         |

### Models Required — Download Before First Run

| Model                                  | Purpose    | Size   | Location                         |
| -------------------------------------- | ---------- | ------ | -------------------------------- |
| `gemma-4-E4B-it-IQ4_XS.gguf`           | LLM        | ~2.5GB | `D:\LLM_MODEL\`                  |
| `all-MiniLM-L6-v2`                     | Embeddings | ~90MB  | `D:\LLM_MODEL\all-MiniLM-L6-v2\` |
| `cross-encoder/ms-marco-MiniLM-L-6-v2` | Reranker   | ~80MB  | `D:\LLM_MODEL\cross-encoder\`    |

Download embedding and reranker models once:

```python
from sentence_transformers import SentenceTransformer, CrossEncoder
SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2").save(r"D:\LLM_MODEL\all-MiniLM-L6-v2")
CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2").save(r"D:\LLM_MODEL\cross-encoder")
```

---

## 4. Project Structure — Production Grade

```
D:\Code\Agentic_Forge\
│
├── CLAUDE.md                  ← Claude Code behaviour rules (root, always)
├── AGENTS.md                  ← Codex UI rules (root, always)
├── CONTEXT.md                 ← Shared memory — both Claude Code and Codex read/update this
├── .env                       ← Single source of truth for ALL config. Always.
├── .env.example               ← Safe template with placeholder values. Commit this, never real .env.
├── requirements.txt           ← Python dependencies
│
├── docs/                      ← All documentation
│   ├── FORGE.md               ← This file
│   ├── FORGE_SRS.md           ← Detailed specs: endpoints, tables, contracts
│   ├── CAS_ATDD_Context.md    ← CAS domain knowledge
│   ├── HOW_TO_RUN.md          ← Setup per machine profile
│   ├── HOW_TO_SCALE.md        ← Add modules, swap LLM, scale users
│   ├── ACCEPTANCE_TESTS.md    ← Golden test matrix for demo readiness
│   └── MAINTAINER.md          ← Operational guide for non-builders
│
├── reference/                 ← V2 codebase — PORT logic, do not rewrite
│   ├── retrieval/             ← retrieval.py, embedder.py, query_expander.py, cas_knowledge_retrieval.py
│   ├── parsing/               ← feature_parser.py, jira_parser.py, screen_context.py
│   ├── storage/               ← schema.sql, connection.py
│   ├── config/
│   │   ├── domain/            ← *.toml CAS domain config
│   │   └── workflow/          ← order.json
│   ├── tools/                 ← ingest.py, build_index.py, build_pdf_chunk_corpus.py
│   ├── templates/             ← ordered.feature, unordered.feature
│   └── samples/
│       ├── jira/              ← *.csv test inputs
│       ├── features/          ← *.feature reference outputs
│       └── docs/              ← CAS PDF source
│
├── data/                      ← Runtime data — never committed to git
│   ├── knowledge/
│   │   ├── cas/               ← CAS PDF documents live here
│   │   ├── lms/               ← LMS PDFs (future)
│   │   └── collections/       ← Collections PDFs (future)
│   └── indices/               ← FAISS indices built here
│       ├── faiss_index.bin    ← Step embeddings
│       ├── step_id_map.npy    ← Step ID mapping
│       └── cas_knowledge.faiss ← CAS doc chunk embeddings
│
├── logs/
│   └── forge.log              ← Application log
│
├── static/                    ← Frontend — vanilla HTML/CSS/JS
│   ├── index.html             ← Login
│   ├── chat.html              ← Forge Chat
│   ├── atdd.html              ← ATDD selector + generation + progress + output
│   ├── settings.html          ← User settings
│   ├── style.css              ← Custom styles + design tokens
│   ├── app.js                 ← Shared auth, API helpers, navigation
│   └── fonts/                 ← Self-hosted Inter + JetBrains Mono TTF files
│
├── forge/
│   ├── core/
│   │   ├── state.py           ← ForgeState TypedDict — shared LangGraph state
│   │   ├── graph.py           ← LangGraph orchestrator — wires all 11 agents
│   │   ├── job_runner.py      ← In-process generation queue + job lifecycle updates
│   │   ├── llm.py             ← llama_cpp LLM client — single instance, lazy load
│   │   ├── db.py              ← PostgreSQL connection pool — port from reference/storage/connection.py
│   │   └── config.py          ← Reads .env — single place, always via get_settings()
│   │
│   ├── agents/
│   │   ├── agent_01_reader.py
│   │   ├── agent_02_domain_expert.py
│   │   ├── agent_03_scope_definer.py
│   │   ├── agent_04_coverage_planner.py
│   │   ├── agent_05_action_decomposer.py
│   │   ├── agent_06_retriever.py
│   │   ├── agent_07_composer.py
│   │   ├── agent_08_atdd_expert.py
│   │   ├── agent_09_writer.py
│   │   ├── agent_10_critic.py
│   │   └── agent_11_reporter.py
│   │
│   ├── infrastructure/
│   │   ├── feature_parser.py      ← Port reference/parsing/feature_parser.py
│   │   ├── repo_indexer.py        ← Port reference/tools/ingest.py
│   │   ├── screen_context.py      ← Port reference/parsing/screen_context.py — DYNAMIC map only
│   │   ├── normalisation.py       ← Port reference/parsing normalisation — no static SCREEN_NAME_MAP
│   │   ├── embedder.py            ← Port reference/retrieval/embedder.py
│   │   ├── step_retriever.py      ← Port reference/retrieval/retrieval.py + cross-encoder + self-RAG
│   │   ├── query_expander.py      ← Port reference/retrieval/query_expander.py
│   │   ├── rag_engine.py          ← Port reference/retrieval/cas_knowledge_retrieval.py + distillation cache
│   │   ├── graph_rag.py           ← NetworkX knowledge graph validator
│   │   ├── order_json_reader.py   ← Order.json validator for Agent 8
│   │   └── jira_client.py         ← PAT auth + CSV fallback
│   │
│   ├── chat/
│   │   ├── router.py              ← Context classifier: CAS | ATDD | General
│   │   ├── chat_engine.py         ← Conversation loop + RAG grounding
│   │   └── session_store.py       ← PostgreSQL chat persistence
│   │
│   ├── modules/
│   │   └── cas/
│   │       └── config.py          ← CAS module config
│   │
│   ├── api/
│   │   ├── main.py                ← FastAPI app — mounts static/, registers routes
│   │   ├── auth.py                ← JWT + argon2 helpers
│   │   ├── models.py              ← All Pydantic request/response models
│   │   └── routes/
│   │       ├── auth.py            ← /auth/login, /auth/logout
│   │       ├── chat.py            ← /chat/, /chat/sessions, /chat/sessions/{id}
│   │       ├── generate.py        ← /generate/, /generate/{job_id}/stream, /generate/{job_id}/result
│   │       ├── settings.py        ← /settings/, /settings/test-jira, /settings/test-model
│   │       └── admin.py           ← /admin/users — create, list, deactivate users
│   │
│   └── scripts/
│       ├── setup_db.py            ← Creates all tables from schema. Run once on fresh DB.
│       ├── index_repo.py          ← Parses feature repo, builds FAISS step index + PostgreSQL tables
│       ├── build_knowledge.py     ← Ingests CAS PDFs, builds doc chunk FAISS index
│       ├── create_user.py         ← CLI: python -m forge.scripts.create_user --username anand --display "Anand"
│       ├── verify_setup.py        ← Checks all paths, models, DB — prints pass/fail per item
│       └── run_acceptance_tests.py ← Runs golden API/generation checks before demo
```

---

## 5. Environment Configuration — .env

`.env` lives in root. It is the ONLY place any path or config value is defined. Code reads exclusively via `get_settings()` in `forge/core/config.py`. No hardcoded paths anywhere. No exceptions.

```env
# ─────────────────────────────────────────────
# MACHINE PROFILE
# dev | demo | prod
# ─────────────────────────────────────────────
MACHINE_PROFILE=dev

# ─────────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────────
DB_NAME=agentic_forge_local
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432

# ─────────────────────────────────────────────
# LLM
# llama_cpp on all machines. No Ollama.
# ─────────────────────────────────────────────
LLM_BACKEND=llama_cpp
LLM_MODEL_PATH=D:\LLM_MODEL\gemma-4-E4B-it-IQ4_XS.gguf
LLM_GPU_LAYERS=0
LLM_CONTEXT_SIZE=8192
LLM_THREADS=4

# ─────────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────────
EMBEDDING_MODEL=D:\LLM_MODEL\all-MiniLM-L6-v2
CROSS_ENCODER_MODEL=D:\LLM_MODEL\cross-encoder

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
FEATURES_REPO_PATH=D:\Path\To\CAS\Feature\Repo
ORDER_JSON_PATH=D:\Code\Agentic_Forge\reference\config\workflow\order.json
CAS_DOCS_PATH=D:\Code\Agentic_Forge\data\knowledge\cas
FAISS_INDEX_DIR=D:\Code\Agentic_Forge\data\indices
LOG_PATH=D:\Code\Agentic_Forge\logs\forge.log

# ─────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────
SECRET_KEY=generate-this-once-with-openssl-rand-hex-32
JWT_EXPIRE_HOURS=12
PAT_ENCRYPTION_KEY=generate-this-once-with-fernet-or-openssl

# ─────────────────────────────────────────────
# JIRA
# Leave blank on personal machine — use CSV mode
# ─────────────────────────────────────────────
JIRA_URL=https://your-jira-instance.com
JIRA_PAT=

# ─────────────────────────────────────────────
# RETRIEVAL TUNING
# ─────────────────────────────────────────────
LOW_MATCH_THRESHOLD=0.3
SELF_RAG_MAX_RETRIES=1
CRITIC_MAX_LOOPS=1

# ─────────────────────────────────────────────
# GENERATION JOBS
# Keep low on dev/demo CPU machines. Increase only after load testing.
# ─────────────────────────────────────────────
MAX_CONCURRENT_JOBS=1
```

**Work laptop** — copy `.env`, update `LLM_MODEL_PATH`, `FEATURES_REPO_PATH`, `JIRA_PAT`, and `PAT_ENCRYPTION_KEY`. Nothing else changes.  
**Prod** — copy `.env`, update `LLM_MODEL_PATH` to 31B GGUF, set `LLM_GPU_LAYERS=35`, update `JIRA_PAT`, and generate a fresh `PAT_ENCRYPTION_KEY`.

---

## 6. LangGraph State Schema

Every agent reads from and writes to this single State object. Nothing is passed agent-to-agent directly.

```python
from typing import TypedDict, Optional, List, Dict, Any

class ForgeState(TypedDict):

    # ── USER INPUT ──────────────────────────────────────
    user_id: str
    jira_input_mode: str          # "jira_id" | "csv"
    jira_story_id: Optional[str]
    jira_pat_override: Optional[str]   # per-session PAT override
    jira_csv_raw: Optional[str]
    flow_type: str                # "ordered" | "unordered"
    three_amigos_notes: str

    # ── AGENT 1 — Reader ────────────────────────────────
    jira_facts: Dict[str, Any]
    # story_id, summary, description, acceptance_criteria[],
    # business_scenarios[], comments_content[], custom_fields{},
    # product_types[], affected_stages[], affected_screens[],
    # affected_entities[], notes, parse_quality, missing_fields[]

    # ── AGENT 2 — Domain Expert ─────────────────────────
    domain_brief: Dict[str, Any]
    # screens[], stages[], lobs[], fields[], conditional_rules[],
    # entity_rules{}, subtype_variations[], confidence: float

    # ── AGENT 3 — Scope Definer ─────────────────────────
    scope: Dict[str, Any]
    # story_scope[], ambient_scope[], excluded[]

    # ── AGENT 4 — Coverage Planner ──────────────────────
    coverage_plan: Dict[str, Any]
    # intents[], logical_ids[], thread_count, coverage_gaps[]

    # ── AGENT 5 — Action Decomposer ─────────────────────
    action_sequences: List[Dict[str, Any]]
    # per intent: given[], when[], then[] (MAX 2), logical_id, stage, screen

    # ── AGENT 6 — Retriever ─────────────────────────────
    retrieved_steps: Dict[str, Any]
    # per intent_id: given[], when[], then[]
    # each: {step_text, score, marker, ce_score}

    # ── AGENT 7 — Composer ──────────────────────────────
    composed_scenarios: List[Dict[str, Any]]

    # ── AGENT 8 — ATDD Expert ───────────────────────────
    reviewed_scenarios: List[Dict[str, Any]]
    # + atdd_issues[], atdd_passed: bool

    # ── AGENT 9 — Writer ────────────────────────────────
    feature_file: str

    # ── AGENT 10 — Critic ───────────────────────────────
    critique: Dict[str, Any]
    # coverage_gaps[], structural_issues[], confidence_score: float,
    # loop_back: bool, loop_reason: str, is_second_pass: bool

    # ── AGENT 11 — Reporter ─────────────────────────────
    final_output: Dict[str, Any]
    # feature_file, gap_report{story_id, coverage_gaps[],
    # markers_summary{}, atdd_issues[], confidence_score, recommendation}
```

---

## 7. Infrastructure — Port Rules

Every infrastructure file has a V2 source in `reference/`. Port directly. Adapt only import paths and config references. Do not rewrite logic.

| V3 File                                  | Port From                                        | What to Adapt                                  |
| ---------------------------------------- | ------------------------------------------------ | ---------------------------------------------- |
| `forge/core/db.py`                       | `reference/storage/connection.py`                | Import `get_settings()` instead of V2 settings |
| `forge/infrastructure/feature_parser.py` | `reference/parsing/feature_parser.py`            | Import paths only                              |
| `forge/infrastructure/repo_indexer.py`   | `reference/tools/ingest.py`                      | Import paths + DB table names                  |
| `forge/infrastructure/screen_context.py` | `reference/parsing/screen_context.py`            | Make SCREEN_NAME_MAP dynamic (see below)       |
| `forge/infrastructure/normalisation.py`  | `reference/parsing/` normalisation logic         | No static SCREEN_NAME_MAP (see below)          |
| `forge/infrastructure/embedder.py`       | `reference/retrieval/embedder.py`                | Path to FAISS_INDEX_DIR from settings          |
| `forge/infrastructure/step_retriever.py` | `reference/retrieval/retrieval.py`               | + cross-encoder + self-RAG (new)               |
| `forge/infrastructure/query_expander.py` | `reference/retrieval/query_expander.py`          | No changes needed                              |
| `forge/infrastructure/rag_engine.py`     | `reference/retrieval/cas_knowledge_retrieval.py` | + distillation cache (new, keep from V3)       |

### SCREEN_NAME_MAP — Dynamic, Never Static

**Never** define SCREEN_NAME_MAP as a hardcoded dictionary. As the repo grows, a static map becomes stale immediately.

Instead, in `screen_context.py`:

```python
def build_screen_name_map() -> dict:
    """Build dynamically from unique_steps after each ingest. Never static."""
    from forge.core.db import get_cursor
    result = {}
    with get_cursor() as cur:
        cur.execute("SELECT DISTINCT step_text FROM unique_steps")
        for row in cur.fetchall():
            text = row["step_text"].lower()
            for pattern, screen in _ANCHOR_PATTERNS:
                m = pattern.search(text)
                if m:
                    result[m.group(0).strip()] = screen
    return result
```

Call `build_screen_name_map()` after each ingest run. Cache result in memory for the session. Never persist to a file.

### Step Retriever — Full Stack Required

```
Action text
→ normalise_query_text() [query_expander.py]
→ expand_for_vector() → FAISS search (50%)
→ expand_for_fts() → PostgreSQL FTS (30%)
→ expand_for_trigram() → pg_trgm (20%)
→ _minmax() score normalisation per channel
→ Weighted merge
→ Stage boost (1.3× auto-detect | 1.6× caller hint)
→ Rich context fetch (step + scenario + file metadata)
→ Cross-encoder reranker (_cross_encode)
→ Self-RAG gate (one retry if top ce_score < LOW_MATCH_THRESHOLD)
→ Final candidates with markers
```

### RAG Engine — Semantic, Not Keyword

```
Query + stage_hint
→ Embed query (all-MiniLM-L6-v2)
→ FAISS search over cas_knowledge.faiss (top_k × 2 candidates)
→ Stage/screen boost for matching doc_chunks metadata
→ top_k results
→ Distillation cache check: {screen}_{stage}_{lob}
→ Cache miss: LLM generates focused summary → cache in DB
→ Return summary
```

Remove keyword scoring entirely. Remove in-memory chunk lists.

---

## 8. The 11 Agent Contracts

### Non-Negotiable Rules For All Agents

- Never swallow exceptions silently. All errors log and bubble up.
- Always log what was received and what was returned.
- Never return empty state. Always return best attempt with markers.
- LLM not loaded = raise clear exception immediately, not on first use.

---

### Agent 1 — Reader

**Reads:** `jira_input_mode`, JIRA content (PAT fetch or CSV), `three_amigos_notes`  
**Job:** Assemble complete `jira_facts`. Handle messy CAS JIRAs — AC missing, content in comments, spread across custom fields.  
**Writes:** `jira_facts`  
**Failure:** Sets `parse_quality: poor`, populates `missing_fields[]`. Never blocks.

---

### Agent 2 — Domain Expert (CAS Specific)

**Reads:** `jira_facts`  
**Calls:** RAG Engine with screen + stage + LOB context  
**Job:** Fetch relevant CAS domain knowledge — fields, conditional rules, LOB variations.  
**Writes:** `domain_brief`  
**Failure:** Low-confidence fields marked `[DOMAIN_UNCERTAIN]`. Continues.  
**CAS Specific:** Yes. Swap `CAS_DOCS_PATH` → swap module.

---

### Agent 3 — Scope Definer

**Reads:** `jira_facts`, `domain_brief`  
**Job:** Story scope = what JIRA introduces. Ambient scope = existing content not in story — light touch only.  
**Writes:** `scope`  
**Failure:** Ambiguous → conservative. Only scope what JIRA explicitly mentions.

---

### Agent 4 — Coverage Planner

**Reads:** `jira_facts`, `domain_brief`, `scope`, `flow_type`  
**Job:** Plan complete coverage. For ordered flows — decide thread count, assign LogicalIDs.  
**Writes:** `coverage_plan`  
**LogicalID format:** `CAS_{storyID}_{outcome}` e.g. `CAS_256008_REJECT`  
**Failure:** Gaps go in `coverage_gaps[]`. Never fabricates intents.

---

### Agent 5 — Action Decomposer (CAS Specific)

**Reads:** `coverage_plan`, `domain_brief`, `flow_type`  
**Job:** Translate each intent into CAS tester actions — repo vocabulary, not business language.  
**Writes:** `action_sequences`  
**Hard constraints:**

- `then[]` maximum 2 items — one Then, one And. No exceptions.
- No `But` keyword ever.
- Ordered sequences: first Given = prerequisite step (exact text, no variation).
  **CAS Specific:** Yes.

---

### Agent 6 — Retriever

**Reads:** `action_sequences`, `domain_brief`, `jira_facts`  
**Calls:** Step Retriever full stack (FAISS + FTS + trgm + cross-encoder + self-RAG)  
**Job:** Find best matching repo step for each action.  
**Writes:** `retrieved_steps` with markers  
**Markers:** `[NEW_STEP_NOT_IN_REPO]` | `[LOW_MATCH]` | `[ROLE_GAP]`  
**Failure:** Always returns best attempt with correct marker. Never empty.

---

### Agent 7 — Composer

**Reads:** `coverage_plan`, `action_sequences`, `retrieved_steps`, `domain_brief`, `flow_type`  
**Job:** Compose retrieved steps into coherent scenarios with correct structure.  
**Writes:** `composed_scenarios`  
**Scenario title rules:**

- Must describe behavior, not list screen names
- Bad: "Display CDDE, recommendation, credit approval and stage"
- Good: "Verify Guarantor option is available in Applicant Type dropdown at Credit Approval"
- Ordered: `<LogicalID> : {behavior description}`  
  **Hard constraints:** Then max 2. No But. Ordered: first Given = prerequisite. Markers carried forward, never dropped.

---

### Agent 8 — ATDD Expert

**Reads:** `composed_scenarios`, `domain_brief`, `flow_type`, `coverage_plan`  
**Calls:** Order.json reader  
**Job:** Quality gate — review scenarios against CAS ATDD conventions.

**Validates ALL files:**

- `But` keyword → hard ban
- `Then` + 2+ `And` → hard ban
- `Scenario:` with Examples → must be `Scenario Outline:`
- Scenario titles → behavior-descriptive

**Validates UNORDERED:**

- Dictionary scope correct — no mixing within scenario
- Angle-bracket syntax present where expansion expected
- No `@Order` tag

**Validates ORDERED:**

- Every scenario starts with prerequisite step (exact text)
- No `#${...}` dictionaries
- No `Background:` block
- Every annotation in Order.json
- LogicalIDs follow convention
- `@Order` or `@E2EOrder` at file level

**Writes:** `reviewed_scenarios` with `atdd_issues[]` and `atdd_passed: bool`  
**Failure:** Never silently passes. Every issue documented.

---

### Agent 9 — Writer

**Reads:** `reviewed_scenarios`, `jira_facts`, `domain_brief`, `flow_type`  
**Job:** Render reviewed scenarios as complete `.feature` file.  
**Writes:** `feature_file`

Responsibilities:

- File-level tags: `@CAS-{storyID}`, `@NotImplemented`, `@Order`/`@E2EOrder` if ordered
- Feature title + purpose comment block
- Background block: unordered only — `Given user is on CAS Login Page`
- Section divider comments: `###=== SECTION NAME ===###`
- Correct keywords — no `But`, correct `Scenario Outline:`
- Dictionary declarations at correct scope (unordered only)
- Markers as inline comments: `# [NEW_STEP_NOT_IN_REPO]`

---

### Agent 10 — Critic

**Reads:** `feature_file`, `coverage_plan`, `jira_facts`, `domain_brief`  
**Job:** Review feature file against coverage plan. Loop back once if critical gaps.  
**Writes:** `critique`  
**Loop rule:** `loop_back: true` → returns to Agent 7. `is_second_pass` prevents second loop. Maximum one loop. Hard stop.

---

### Agent 11 — Reporter

**Reads:** `feature_file`, `critique`, `coverage_plan`, `jira_facts`  
**Job:** Assemble final feature file + gap report.  
**Writes:** `final_output`  
**Always produces output.** Low confidence → says so clearly. Never hides problems.

---

## 9. JIRA Input — Two Modes

### Mode 1: JIRA ID (Default)

Tester provides Story ID. Forge fetches via PAT from `JIRA_URL` in `.env`.  
Per-session override: tester can paste a different PAT in the Advanced section of the Generate form.  
Fetch everything — description, AC, all comments, all custom fields, linked issues.

**PAT precedence:**

1. Per-session PAT override from the Generate form
2. User saved encrypted PAT from settings
3. Environment-level `JIRA_PAT` from `.env`

**Security rules:** PAT values are never logged, never returned to the frontend, and never stored in plaintext. Database fields store encrypted ciphertext only.

### Mode 2: CSV (Fallback — available on all machines)

Tester pastes raw CSV content directly in the form.  
Port parsing from `reference/parsing/jira_parser.py`.

### JIRA Parser Rules

- Never fail silently — always flag what was not found
- Never block — always pass something to Agent 1
- Set `parse_quality`: "complete" | "partial" | "poor"
- Populate `missing_fields[]` with what was not found

---

## 10. Feature Repo Indexer

Port from `reference/tools/ingest.py` and `reference/parsing/feature_parser.py`. This is a direct port — do not simplify.

### DB Schema — 4 Normalized Tables

Port from `reference/storage/schema.sql`:

- `features` — one row per file
- `scenarios` — one row per scenario
- `steps` — one row per step occurrence
- `example_blocks` — one row per Examples table
- `unique_steps` — materialized view, deduplicated steps with usage counts

### V2 Features to Preserve — All of These

- Incremental ingest — mtime diffing, only process changed files
- Change detection — delete + re-insert on change
- Delete detection — CASCADE clean on removed files
- Background step accumulation — prepend to every subsequent scenario
- Doc string capture — append to preceding step text
- Header-based Examples table parsing
- screen_context inference via \_ANCHOR_PATTERNS (dynamic, not static map)
- `_parse_dicts()` for `#${Key=["v1","v2"]}` annotations
- `_check_conflict()` for @Order + dicts invalid combo
- LogicalID marker detection
- BOM + non-UTF-8 encoding handling
- Skip `PickApplication.feature` and `OpenApplication.feature`

### Two FAISS Indices — Separate, Not Combined

**Step index** (`faiss_index.bin`) — built by `forge/scripts/index_repo.py`  
Reads from `unique_steps` materialized view.

**Doc chunk index** (`cas_knowledge.faiss`) — built by `forge/scripts/build_knowledge.py`  
Reads from CAS PDFs in `data/knowledge/cas/`.  
Stores chunk metadata in `doc_chunks` PostgreSQL table.

---

## 11. STP and OpenApplication.feature

Critical for ordered flows.

Forge does not generate traversal scenarios. STP via `OpenApplication.feature` handles stage setup. Forge's ordered scenarios start from the target stage, assuming STP already ran.

**Infrastructure files — never index, never generate:**

- `PickApplication.feature`
- `OpenApplication.feature`

**Mandatory first step — every ordered scenario:**

```gherkin
Given all prerequisite are performed in previous scenario of "<ProductType>" logical id "<LogicalID>"
```

Not optional. Not situational. Agent 5 generates it. Agent 9 writes it. Agent 8 validates it. No exceptions.

---

## 12. Forge Chat Architecture

### Context Router

Every message classified before response:

```
User message
→ Router: CAS domain | ATDD | General
→ CAS: retrieve from RAG engine → inject into prompt
→ ATDD: load from CAS_ATDD_Context.md → inject
→ General: Gemma from own knowledge
→ Respond
```

Router is one lightweight LLM call. User never chooses manually.

UI shows context pill: `● CAS Knowledge Active` (teal) or `● General` (muted).

### Session Memory

Within session: conversation history in memory.  
Across sessions: saved to PostgreSQL per user. Load last session on login.

---

## 13. User Management

No self-registration. Admin creates users via CLI.

```bash
python -m forge.scripts.create_user --username anand --display "Anand" --password forge123
```

Script prompts for password if `--password` not given. Uses argon2 hashing.

### User Profile

Each user has: username, display name, password, JIRA PAT (optional, encrypted at rest), theme preference, last login.

### Admin Endpoint

`POST /admin/users` — create user (admin JWT required)  
`GET /admin/users` — list users  
`DELETE /admin/users/{id}` — deactivate user

First admin user created via CLI script only.

---

## 14. Frontend — Vanilla HTML/CSS/JS

No React. No npm on server. No build step.

FastAPI serves `static/` directly:

```python
app.mount("/", StaticFiles(directory="static", html=True), name="static")
```

**Pages:**

- `static/index.html` — Login
- `static/chat.html` — Forge Chat (protected)
- `static/atdd.html` — ATDD selector + generation + progress + output (protected)
- `static/settings.html` — User settings + profile (protected)

**Shared:**

- `static/app.js` — auth token, API calls, navigation, theme, logout
- `static/style.css` — design tokens + custom styles
- `static/fonts/` — Inter + JetBrains Mono TTF self-hosted

**ATDD form inputs:**

- Toggle: JIRA ID (default) | Paste CSV
- JIRA Story ID field (shown when JIRA ID selected)
- CSV textarea (shown when CSV selected)
- Three Amigos Notes textarea
- Flow Type selector: Ordered | Unordered
- Advanced section (collapsed): JIRA PAT override

**ATDD generation — three states on same page:**

1. Module selector (CAS active, LMS/Collections Coming Soon)
2. Generation form (after CAS selected)
3. Progress + Output (after submit)

**Agent pipeline visualization — critical:**
11 agents shown as rows. Each lights up as it runs. Status: waiting → running (pulse) → done (green) → failed (red). Elapsed counter live. Never a plain spinner.

**Fonts — self-hosted, Forge runs offline:**

- Inter Variable (UI)
- JetBrains Mono (code blocks, feature file output)
- No Google Fonts CDN. Ever.

---

## 15. API Endpoints

| Method | Path                        | Auth  | Purpose                |
| ------ | --------------------------- | ----- | ---------------------- |
| POST   | `/auth/login`               | No    | Login, returns JWT     |
| POST   | `/auth/logout`              | Yes   | Invalidate session     |
| POST   | `/chat/`                    | Yes   | Send message           |
| GET    | `/chat/sessions`            | Yes   | List user sessions     |
| GET    | `/chat/sessions/{id}`       | Yes   | Load session history   |
| DELETE | `/chat/sessions/{id}`       | Yes   | Delete session         |
| POST   | `/generate/`                | Yes   | Start generation job   |
| GET    | `/generate/{job_id}/stream` | Yes   | SSE progress stream    |
| GET    | `/generate/{job_id}/result` | Yes   | Fetch completed result |
| GET    | `/settings/`                | Yes   | Load user settings     |
| PUT    | `/settings/`                | Yes   | Save user settings     |
| PUT    | `/settings/profile`         | Yes   | Update display name    |
| PUT    | `/settings/password`        | Yes   | Change password        |
| POST   | `/settings/test-jira`       | Yes   | Test JIRA connection   |
| POST   | `/settings/test-model`      | Yes   | Test LLM is loaded     |
| POST   | `/admin/users`              | Admin | Create user            |
| GET    | `/admin/users`              | Admin | List users             |
| DELETE | `/admin/users/{id}`         | Admin | Deactivate user        |

### SSE Stream — Valid JSON Always

```
data: {"agent": 3, "elapsed": 12}
data: {"agent": 4, "elapsed": 28}
data: {"status": "done"}
data: {"status": "failed", "reason": "..."}
```

### SSE Auth Contract

Protected stream clients must use `fetch()` streaming with the normal `Authorization: Bearer <jwt_token>` header. Do not use native browser `EventSource` while auth is header-based, because `EventSource` cannot reliably send custom Authorization headers.

Allowed alternatives only if explicitly redesigned:

- HttpOnly cookie auth for all protected frontend requests
- One-time short-lived stream token in query string, generated by an authenticated request

Default implementation: authenticated `fetch()` streaming.

### Generation Job Execution Model

Forge uses a simple in-process async job runner for dev/demo:

1. `POST /generate/` validates input, creates a `generation_jobs` row with status `pending`, and returns `job_id`.
2. `job_runner.py` starts the job when a worker slot is available. Dev/demo default: `MAX_CONCURRENT_JOBS=1`.
3. While running, the job row is updated after each agent: `status='running'`, `current_agent`, `elapsed_seconds`, and partial diagnostic data where useful.
4. The SSE endpoint reads job progress from memory when available and from `generation_jobs` as fallback.
5. On success, store `feature_file`, `gap_report`, `confidence_score`, `completed_at`, and `status='done'`.
6. On failure, store `error_message`, `completed_at`, and `status='failed'`. Never leave an exception only in logs.
7. On server startup, any jobs found in `pending` or `running` older than the current process are marked `failed` with reason `Server restarted before completion`.

This is intentionally not Celery/Redis for V1. Add an external queue only after Forge has real multi-user load.

---

## 16. LLM — Hard Rules

**If LLM model file does not exist at `LLM_MODEL_PATH` on startup:**

- Server starts anyway
- Log: `[WARN] LLM model not found at {path}. LLM calls will fail.`
- Any endpoint that calls LLM returns: `{"error": "LLM model not loaded. Check LLM_MODEL_PATH in .env and restart."}`
- Never crash. Never silent failure.

**LLM client is a single lazy-loaded instance in `forge/core/llm.py`:**

```python
_llm_instance = None

def get_llm():
    global _llm_instance
    if _llm_instance is None:
        path = get_settings().llm_model_path
        if not Path(path).exists():
            raise LLMNotLoadedError(f"Model not found: {path}")
        _llm_instance = Llama(model_path=path, n_gpu_layers=get_settings().llm_gpu_layers)
    return _llm_instance
```

---

## 17. Hard Rules — What Claude Code Must Never Do

- No hardcoded paths anywhere. Always `get_settings().field_name`.
- No silent exception swallowing in agents. Always log + raise or return with marker.
- No static SCREEN_NAME_MAP. Dynamic from DB only.
- No rewriting V2 logic from scratch. Port and adapt.
- No `But` keyword in generated Gherkin. Ever.
- No more than two items in Then block.
- No dictionaries in ordered files.
- No Background blocks in ordered files.
- No second Critic loop. `is_second_pass` enforces this.
- No marker drops. Markers travel Agent 6 → final output intact.
- No cloud API calls. Fully offline.
- No Ollama. llama_cpp only.
- No React. No npm on server. Static HTML only.
- No Google Fonts CDN. Self-hosted only.
- No native EventSource for protected SSE while using Authorization headers; use authenticated fetch streaming.
- No plaintext PAT storage or PAT logging. Encrypt at rest and mask everywhere.
- No fabricated domain knowledge. Agent 2 fetches from documents.

---

## 18. CodeGraph — Code Intelligence

After first Claude Code session, initialize CodeGraph in the project root:

```bash
npx @colbymchenry/codegraph
```

This indexes all files and makes the codebase navigable as a graph.

Claude Code: When CodeGraph is initialized, use `codegraph_search` for quick symbol lookups. Do not call `codegraph_explore` in main session — spawn Explore agent for deep exploration. This prevents context flooding.

---

## 19. Build Order

Each task is independently testable. Complete one, verify, proceed.

**Task 1 — DB Schema + Core**
Run `forge/scripts/setup_db.py`. Verify all tables created. Build `forge/core/config.py`, `forge/core/db.py`, `forge/core/llm.py`.

**Task 2 — Auth + User CLI**
`users` table, login route, JWT middleware. `forge/scripts/create_user.py`. Test: create user → login → get token → hit protected route.

**Task 3 — Repo Indexer**
Port feature_parser + repo_indexer from V2. Run `index_repo.py`. Verify table counts: features, scenarios, steps, example_blocks, unique_steps.

**Task 4 — Step FAISS Index**
`forge/scripts/build_step_index.py`. Reads from `unique_steps`. Builds `faiss_index.bin`. Verify step count matches `unique_steps`.

**Task 5 — CAS Knowledge Build**
`forge/scripts/build_knowledge.py`. Ingests PDFs from `data/knowledge/cas/`. Builds `cas_knowledge.faiss` + `doc_chunks` table. Verify chunk count.

**Task 6 — Step Retriever**
Port from V2. Add cross-encoder. Add self-RAG gate. Test: 5 known CAS action phrases → correct repo steps returned.

**Task 7 — RAG Engine**
Port from V2. FAISS semantic retrieval. Distillation cache. Test: known screen + stage → grounded domain context returned.

**Task 8 — LangGraph Skeleton**
`state.py` + `graph.py`. All 11 agents as empty stubs that log and pass State. Confirm State flows end to end.

**Task 9 — JIRA Client**
PAT mode + CSV mode. Test CSV: paste sample from `reference/samples/jira/` → parse correctly.

**Task 10 — Agent 1 (Reader)**
Wire JIRA client. LLM assembles `jira_facts`. Test on messy CSV sample.

**Task 11 — Agents 2–11**
Build in order. Each reads from previous agent's State output. Test Agent 2 domain grounding first — it sets quality for everything downstream.

**Task 12 — FastAPI Routes**
All endpoints. SSE stream with valid JSON. Test: full generate job via API, stream events visible.

**Task 13 — Frontend**
Read `AGENTS.md` for full UI spec. Vanilla HTML/CSS/JS in `static/`. Test: login → chat → ATDD → settings, all functional.

**Task 14 — Verify Setup Script**
`forge/scripts/verify_setup.py`. Checks all `.env` paths exist, models loadable, DB reachable, tables populated. Prints pass/fail per item. Run this before any demo.

**Task 15 — Integration Test**
Submit sample JIRA CSV from `reference/samples/jira/`. Evaluate output: scope discipline, step grounding, marker honesty, ATDD structural correctness.

**Task 16 — Golden Acceptance Tests**
Run `python -m forge.scripts.run_acceptance_tests`. This must verify auth, CSV generation, ordered generation, unordered generation, progress streaming, marker preservation, LLM-missing behavior, and Agent 8 hard failures.

---

## 20. Minimum Acceptance Tests — Mandatory

These tests are part of the product contract, not optional QA notes. Keep the sample inputs under `reference/samples/jira/` or `tests/fixtures/`.

| Test                                | Expected Result                                                                           |
| ----------------------------------- | ----------------------------------------------------------------------------------------- |
| Login with valid user               | JWT returned and protected endpoint works                                                 |
| Invalid JWT on protected page       | API returns 401 and UI redirects to login                                                 |
| CSV unordered story                 | Generates unordered feature with Background and dictionaries                              |
| CSV ordered story                   | Generates ordered feature with `@Order`, LogicalID, and canonical prerequisite first step |
| Weak step retrieval                 | `[LOW_MATCH]` marker appears and reaches final output                                     |
| Missing repo step                   | `[NEW_STEP_NOT_IN_REPO]` marker appears and reaches final output                          |
| Role/entity mismatch                | `[ROLE_GAP]` marker appears and reaches final output                                      |
| Ordered tag not matching Order.json | Agent 8 fails ATDD review; issue is visible in gap report                                 |
| LLM model path missing              | Server stays up; chat/generation return clear model-not-loaded error                      |
| SSE/progress stream                 | Authenticated fetch stream receives agent progress and final done/failed event            |
| Offline frontend smoke test         | Login, Chat shell, ATDD shell, Settings shell render without internet                     |

---

## 21. Evaluation — No Story-Specific Calibration

Evaluate on any story using these dimensions:

- Story scope respected — no ambient scope bleed
- Steps repo-grounded — marker rate acceptable
- Markers placed honestly — no silent drops
- ATDD structural rules pass — Agent 8 pass rate
- Gap report surfaces real gaps — not empty, not fabricated
- Chat answers CAS questions from document knowledge

Run on new stories each sprint. Fix agent prompts or retrieval logic — never the story.

---

_FORGE.md — Final. Build from here._  
_Questions: `docs/CAS_ATDD_Context.md` for domain knowledge. `docs/FORGE_SRS.md` for endpoint and table detail. `reference/` for V2 logic to port._

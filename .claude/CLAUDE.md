# CLAUDE.md

## Claude Code Build Instructions — Forge Agentic Backend

**You are:** Claude Code  
**Your job:** Build the Forge backend — Python, FastAPI, LangGraph, PostgreSQL  
**Project root:** `D:\Code\Agentic_Forge\`  
**Date:** April 2026

---

## READ EVERYTHING BEFORE WRITING A SINGLE LINE

Read these documents completely before writing any code:

1. `docs/FORGE.md` — Architecture, tech stack, agent contracts, hard rules
2. `docs/FORGE_SRS.md` — Every API endpoint, DB schema, infrastructure component detail, glossary

When you finish reading, summarize in 5 bullet points what Forge is and what you are building. Then report ready for Task 1.

---

<!-- CODEGRAPH_START -->

## CodeGraph

CodeGraph builds a semantic knowledge graph of codebases for faster, smarter code exploration.

### If `.codegraph/` exists in the project

**NEVER call `codegraph_explore` or `codegraph_context` directly in the main session.** These tools return large amounts of source code that fills up main session context. Instead, ALWAYS spawn an Explore agent for any exploration question (e.g., "how does X work?", "explain the Y system", "where is Z implemented?").

**When spawning Explore agents**, include this instruction in the prompt:

> This project has CodeGraph initialized (.codegraph/ exists). Use `codegraph_explore` as your PRIMARY tool — it returns full source code sections from all relevant files in one call.
>
> **Rules:**
>
> 1. Follow the explore call budget in the `codegraph_explore` tool description — it scales automatically based on project size.
> 2. Do NOT re-read files that codegraph_explore already returned source code for. The source sections are complete and authoritative.
> 3. Only fall back to grep/glob/read for files listed under "Additional relevant files" if you need more detail, or if codegraph returned no results.

**The main session may only use these lightweight tools directly** (for targeted lookups before making edits, not for exploration):

| Tool                                      | Use For                              |
| ----------------------------------------- | ------------------------------------ |
| `codegraph_search`                        | Find symbols by name                 |
| `codegraph_callers` / `codegraph_callees` | Trace call flow                      |
| `codegraph_impact`                        | Check what's affected before editing |
| `codegraph_node`                          | Get a single symbol's details        |

### If `.codegraph/` does NOT exist

At the start of a session, ask the user if they'd like to initialize CodeGraph:

"I notice this project doesn't have CodeGraph initialized. Would you like me to run `codegraph init -i` to build a code knowledge graph?"

<!-- CODEGRAPH_END -->

## Who You Are Working With

**Anand** — CAS QA Lead, Nucleus Software. Domain expert. All CAS domain questions go to him. Architecture decisions are yours.

**CONTEXT.md** — Shared status snapshot. Read it at the start of every session. Update it when you complete a task. Codex reads this too — keep it accurate.

**CHANGELOG.md** — Append-only handoff log. Update it after every completed task, before `/compact`, and before ending a session. This is what the next agent reads to understand what actually changed.

---

## Operating Mode — Keep Context Cheap Without Getting Stupid

Use terse technical English by default. Do **not** use broken grammar, meme language, or "caveman mode". Saving a few output tokens is not worth unclear instructions or bad implementation.

### Default: Terse Execution Mode

Use this for normal build work:

- No greetings. No motivational filler.
- Do not restate the whole spec.
- Report only: what changed, files touched, verification result, blockers.
- Prefer short bullets over paragraphs.
- Do not paste large code blocks unless Anand asks or the change is small and reviewable.
- When reading files, summarize only the relevant finding. Do not dump file contents.

### Plan Mode

Use Plan Mode only when:

- Anand explicitly asks for a plan, design, or architecture review.
- The change touches multiple subsystems.
- The task is risky, ambiguous, or could break existing contracts.

Plan Mode output must still be concise: goal, files affected, steps, risks, verification.

### Context Discipline

- Use `/context` when context feels high or after large file reads.
- Use `/compact` before context becomes unstable. Focus the compaction on current task, files changed, decisions, verification, and next command.
- Before compaction, session switch, or token exhaustion: update both `CONTEXT.md` and `CHANGELOG.md`.
- Use subagents/explore sessions for broad research so the main session stays focused.

---

## Hard Rules — Never Break These

**Configuration**

- `.env` is the single source of truth for ALL paths, settings, and credentials
- All config read exclusively via `get_settings()` in `forge/core/config.py`
- No hardcoded paths anywhere in code. No exceptions. Not even in comments as examples.
- No hardcoded model names. No hardcoded DB names. Always from settings.
- Secrets must never be logged. This includes JIRA PAT, JWT, password hashes, encryption keys, and `.env` contents.

**LLM**

- LLM is llama_cpp on all machines. No Ollama. No cloud APIs. Ever.
- LLM client is a single lazy-loaded instance in `forge/core/llm.py`
- If model file does not exist at startup — server starts anyway, logs a warning
- Any endpoint calling LLM catches `LLMNotLoadedError` and returns clean JSON error
- Never crash on missing model. Never silent failure.

**Secrets and PAT Handling**

- `JIRA_PAT` from `.env` may be plain because it is machine-local config.
- User-saved PAT values in DB must be encrypted before storage.
- Add `PAT_ENCRYPTION_KEY` to `.env` and `Settings`. Use Fernet-compatible key material.
- Never return a PAT from API. Return masked status only, e.g. `***masked***` or `is_configured: true`.
- Never log PATs, JWTs, passwords, password hashes, or raw Authorization headers.

**Agents**

- Never swallow exceptions silently in any agent
- Every agent logs what it received and what it returned
- Every agent returns best attempt with markers — never empty state
- Markers travel from Agent 6 to final output intact. Never dropped.
- Maximum one Critic loop. `is_second_pass` flag enforces this. Hard stop.

**V2 Reference**

- `reference/` contains V2 codebase. Port logic directly — do not rewrite from scratch.
- "Study and simplify" is what caused architectural downgrades in previous builds. Do not repeat.
- Adapt import paths, config references, DB table names to V3. Keep logic faithful.
- Specific port instructions per file are in `docs/FORGE_SRS.md` Section 4.

**Database**

- DB name: `agentic_forge_local`
- Schema created by `forge/scripts/setup_db.py` — never by hand
- Never DROP tables in code except in `setup_db.py --fresh` mode
- SCREEN_NAME_MAP is ALWAYS dynamic — built from `unique_steps` after ingest. Never a static dictionary.

**Frontend**

- Backend serves `static/` folder via FastAPI StaticFiles mount
- Do not touch anything in `static/` — that is Codex territory
- Do not touch `AGENTS.md` — that is Codex territory

**General**

- No cloud API calls. Fully offline.
- No Google Fonts CDN. No external URLs.
- No self-registration endpoint — users created via CLI only
- No second Critic loop — hard stop enforced in graph.py
- No `But` keyword ever in generated Gherkin
- No more than 2 items in Then block — Then + one And maximum
- No dictionaries in ordered files
- No Background blocks in ordered files

---

## Project Structure — Build Everything Here

```
D:\Code\Agentic_Forge\
│
├── CLAUDE.md                  ← you are here
├── AGENTS.md                  ← Codex territory, do not touch
├── CONTEXT.md                 ← shared status snapshot, read and update every session
├── CHANGELOG.md               ← append-only handoff log, update after every task
├── .env                       ← single source of truth
├── requirements.txt           ← all Python dependencies
│
├── docs/
│   ├── FORGE.md
│   ├── FORGE_SRS.md
│   ├── CAS_ATDD_Context.md
│   └── Design.md              ← Codex territory, do not touch
│
├── reference/                 ← V2 code — PORT from here, do not modify
│
├── data/
│   ├── knowledge/cas/         ← CAS module
│   │   ├── _source/           ← CAS PDFs go here
│   │   ├── taxanomy_source/   ← Seed taxonomy TOML files
│   │   ├── screens/           ← Generated wiki (screens)
│   │   ├── stages/            ← Generated wiki (stages)
│   │   └── concepts/          ← Generated wiki (concepts)
│   ├── knowledge/lms/         ← Future LMS module (same structure)
│   ├── knowledge/collections/ ← Future collections module (same structure)
│   └── indices/               ← FAISS indices built here
│
├── logs/
│   └── forge.log
│
├── static/                    ← Codex territory, do not touch
│
└── forge/
    ├── core/
    │   ├── state.py
    │   ├── graph.py
    │   ├── llm.py
    │   ├── db.py
    │   └── config.py
    ├── agents/
    │   ├── agent_01_reader.py
    │   ├── agent_02_domain_expert.py
    │   ├── agent_03_scope_definer.py
    │   ├── agent_04_coverage_planner.py
    │   ├── agent_05_action_decomposer.py
    │   ├── agent_06_retriever.py
    │   ├── agent_07_composer.py
    │   ├── agent_08_atdd_expert.py
    │   ├── agent_09_writer.py
    │   ├── agent_10_critic.py
    │   └── agent_11_reporter.py
    ├── infrastructure/
    │   ├── feature_parser.py
    │   ├── repo_indexer.py
    │   ├── screen_context.py
    │   ├── normalisation.py
    │   ├── embedder.py
    │   ├── step_retriever.py
    │   ├── query_expander.py
    │   ├── rag_engine.py
    │   ├── graph_rag.py
    │   ├── order_json_reader.py
    │   └── jira_client.py
    ├── chat/
    │   ├── router.py
    │   ├── chat_engine.py
    │   └── session_store.py
    ├── modules/
    │   └── cas/
    │       └── config.py
    ├── api/
    │   ├── main.py
    │   ├── auth.py
    │   ├── models.py
    │   └── routes/
    │       ├── auth.py
    │       ├── chat.py
    │       ├── generate.py
    │       ├── settings.py
    │       └── admin.py
    └── scripts/
        ├── setup_db.py
        ├── index_repo.py
        ├── build_step_index.py
        ├── build_knowledge.py
        ├── create_user.py
        └── verify_setup.py
```

---

## .env — What It Contains

Before Task 1, verify `.env` exists and has these keys. If missing, create `.env` with this template and tell Anand which values need filling:

```env
# Machine profile
MACHINE_PROFILE=dev

# Database
DB_NAME=agentic_forge_local
DB_USER=postgres
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# LLM — llama_cpp on all machines
LLM_BACKEND=llama_cpp
LLM_MODEL_PATH=D:\LLM_MODEL\gemma-4-E4B-it-IQ4_XS.gguf
LLM_GPU_LAYERS=0
LLM_CONTEXT_SIZE=8192
LLM_THREADS=4

# Models
EMBEDDING_MODEL=D:\LLM_MODEL\all-MiniLM-L6-v2
CROSS_ENCODER_MODEL=D:\LLM_MODEL\cross-encoder

# Paths
FEATURES_REPO_PATH=
ORDER_JSON_PATH=D:\Code\Agentic_Forge\reference\config\workflow\order.json
CAS_DOCS_PATH=D:\Code\Agentic_Forge\data\knowledge\cas
FAISS_INDEX_DIR=D:\Code\Agentic_Forge\data\indices
LOG_PATH=D:\Code\Agentic_Forge\logs\forge.log

# Auth
SECRET_KEY=
JWT_EXPIRE_HOURS=12
PAT_ENCRYPTION_KEY=

# JIRA — blank on personal machine, fill on work laptop
JIRA_URL=
JIRA_PAT=

# Retrieval tuning
LOW_MATCH_THRESHOLD=0.3
SELF_RAG_MAX_RETRIES=1
CRITIC_MAX_LOOPS=1
```

---

## config.py — The Settings Contract

`forge/core/config.py` is the only place `.env` is read. Every other file uses `get_settings()`.

```python
from pydantic_settings import BaseSettings
from pathlib import Path
from functools import lru_cache

class Settings(BaseSettings):
    # Machine
    machine_profile: str = "dev"

    # Database
    db_name: str = "agentic_forge_local"
    db_user: str = "postgres"
    db_password: str = ""
    db_host: str = "localhost"
    db_port: int = 5432

    # LLM
    llm_backend: str = "llama_cpp"
    llm_model_path: Path = Path("")
    llm_gpu_layers: int = 0
    llm_context_size: int = 8192
    llm_threads: int = 4

    # Models
    embedding_model: str = ""
    cross_encoder_model: str = ""

    # Paths
    features_repo_path: Path = Path("")
    order_json_path: Path = Path("")
    cas_docs_path: Path = Path("")
    faiss_index_dir: Path = Path("")
    log_path: Path = Path("logs/forge.log")

    # Auth
    secret_key: str = ""
    jwt_expire_hours: int = 12
    pat_encryption_key: str = ""

    # JIRA
    jira_url: str = ""
    jira_pat: str = ""

    # Retrieval
    low_match_threshold: float = 0.3
    self_rag_max_retries: int = 1
    critic_max_loops: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

---

## Build Order — One Task at a Time

Complete one task. Report what was built and how to verify it. Wait for Anand's confirmation. Then next task.

Do not skip ahead. Do not bundle tasks. Each task must be independently verifiable.

---

### Task 1 — Core Foundation

Build these files:

- `forge/core/config.py` — Settings class as specified above
- `forge/core/db.py` — Port from `reference/storage/connection.py`. ThreadedConnectionPool min=1 max=10. Public API: `get_conn()`, `release_conn()`, `get_cursor()`, `run_sql_file()`. Read all DB params from `get_settings()`.
- `forge/core/llm.py` — Lazy-loaded single instance. `get_llm()` raises `LLMNotLoadedError` if model file missing. `llm_complete(prompt, system, max_tokens)` as the only public call surface.
- `forge/core/state.py` — `ForgeState` TypedDict exactly as defined in `docs/FORGE.md` Section 6.
- `forge/core/graph.py` — LangGraph graph wiring all 11 agents as empty stubs. Each stub logs "Agent N received state" and returns state unchanged. Graph must run end to end with no errors.

**Verification:**

```bash
python -c "from forge.core.config import get_settings; print(get_settings().db_name)"
python -c "from forge.core.graph import run_graph; print('Graph OK')"
```

Expected: prints `agentic_forge_local` and `Graph OK`.

---

### Task 2 — Database Setup + Auth

Build these files:

- `forge/scripts/setup_db.py` — Reads schema SQL, creates all tables. `--fresh` flag drops and recreates everything. Schema SQL defined inline in script or in `forge/infrastructure/schema.sql`. Tables: `users`, `chat_sessions`, `chat_messages`, `generation_jobs`, `user_settings`, `features`, `scenarios`, `steps`, `example_blocks`, `unique_steps` (materialized view), `doc_chunks`, `rag_cache`. Full schema in `docs/FORGE_SRS.md` Section 2.
- `forge/api/auth.py` — JWT creation and verification. argon2 password hashing. `create_access_token()`, `verify_token()`, `hash_password()`, `verify_password()`.
- `forge/api/crypto.py` — PAT encryption/decryption helpers. Encrypt user PAT before DB storage. Decrypt only when calling JIRA. Mask everywhere else.
- `forge/api/models.py` — All Pydantic models. Full list in `docs/FORGE_SRS.md` Section 3.
- `forge/api/main.py` — FastAPI app. Registers all routers. Mounts `static/` with StaticFiles. Configures logging to `LOG_PATH`.
- `forge/api/routes/auth.py` — `POST /auth/login`, `POST /auth/logout`.
- `forge/scripts/create_user.py` — CLI: `python -m forge.scripts.create_user --username anand --display "Anand" --admin`. Prompts for password if not given. Uses argon2.

**Verification:**

```bash
python -m forge.scripts.setup_db
python -m forge.scripts.create_user --username anand --display "Anand" --admin
uvicorn forge.api.main:app --port 8000
# Then: POST http://localhost:8000/auth/login with {"username":"anand","password":"..."}
# Expected: JWT token returned
```

---

### Task 3 — Feature Repo Parser + Indexer

Build these files:

- `forge/infrastructure/normalisation.py` — Port normalisation logic from V2. `_norm()`, `STEP_KEYWORD_MAP`. NO static `SCREEN_NAME_MAP`. Dynamic only — see below.
- `forge/infrastructure/screen_context.py` — Port from `reference/parsing/screen_context.py`. `_ANCHOR_PATTERNS` for navigation detection. `infer_screen_contexts()` called during parsing. `build_screen_name_map()` queries `unique_steps` after ingest — never a static dict.
- `forge/infrastructure/feature_parser.py` — Port from `reference/parsing/feature_parser.py` (626 lines). All CAS extensions required: Background accumulation, doc string capture, header-based Examples parsing, dictionary parsing `_parse_dicts()`, conflict detection `_check_conflict()`, LogicalID detection, BOM/encoding handling, screen context inference.
- `forge/infrastructure/repo_indexer.py` — Port from `reference/tools/ingest.py` (355 lines). Full incremental ingest: mtime diffing, new/changed/removed file handling, transactional 4-table insert, materialized view refresh. `--full-rebuild` flag drops and recreates schema then re-indexes. Skip `PickApplication.feature` and `OpenApplication.feature`.
- `forge/scripts/index_repo.py` — Entry point. Calls repo_indexer. Reports table counts on completion.

**Verification:**

```bash
python -m forge.scripts.index_repo --full-rebuild
# Expected output:
# [OK] features: N  scenarios: M  steps: P  example_blocks: Q  unique_steps: R
# Counts should be non-zero if FEATURES_REPO_PATH is set and contains .feature files
```

Then verify in PostgreSQL:

```sql
SELECT count(*) FROM features;
SELECT count(*) FROM unique_steps;
SELECT count(*) FROM steps WHERE screen_context IS NOT NULL;
```

---

### Task 4 — Embedder + Step FAISS Index

Build these files:

- `forge/infrastructure/embedder.py` — Port from `reference/retrieval/embedder.py`. Uses `all-MiniLM-L6-v2` from `settings.embedding_model`. `build_index(step_rows)`, `load_index()`, `search_index(index, id_map, query_text, top_k)`.
- `forge/scripts/build_step_index.py` — Reads from `unique_steps` view. Embeds all step texts. Builds FAISS IndexFlatL2. Saves `faiss_index.bin` and `step_id_map.npy` to `settings.faiss_index_dir`.

**Verification:**

```bash
python -m forge.scripts.build_step_index
# Expected: faiss_index.bin and step_id_map.npy created in FAISS_INDEX_DIR
# Step count in index must match unique_steps count
```

---

### Task 5 — CAS Knowledge Build

Build these files:

- `forge/scripts/build_knowledge.py` — Port from `reference/tools/build_pdf_chunk_corpus.py`. Reads PDFs from `settings.cas_docs_path`. Chunks text with metadata (section, stage, screen hints). Builds FAISS index over doc chunks. Saves `cas_knowledge.faiss` to `settings.faiss_index_dir`. Inserts chunk metadata into `doc_chunks` table.

**Verification:**

```bash
python -m forge.scripts.build_knowledge
# Expected: cas_knowledge.faiss created, doc_chunks table populated
```

```sql
SELECT count(*) FROM doc_chunks;
SELECT DISTINCT stage_hint FROM doc_chunks WHERE stage_hint IS NOT NULL;
```

Note: If `CAS_DOCS_PATH` is empty, script must report clearly and exit without error.

---

### Task 6 — Step Retriever

Build these files:

- `forge/infrastructure/query_expander.py` — Port from `reference/retrieval/query_expander.py` verbatim. Functions: `normalise_query_text()`, `expand_for_vector()`, `expand_for_fts()`, `expand_for_trigram()`.
- `forge/infrastructure/step_retriever.py` — Port from `reference/retrieval/retrieval.py`. Full stack as specified in `docs/FORGE_SRS.md` Section 4.2:
  - Three channel retrieval (FAISS + FTS + pg_trgm)
  - Per-channel score normalisation via `_minmax()`
  - Weighted merge (50/30/20)
  - Stage boost (1.6× hint, 1.3× auto-detect)
  - Rich context fetch (step + scenario + file metadata)
  - Cross-encoder reranker using `settings.cross_encoder_model`
  - Self-RAG gate: one retry if top `ce_score < settings.low_match_threshold`
  - Marker assignment based on ce_score thresholds

**Verification:**

```python
from forge.infrastructure.step_retriever import retrieve
results = retrieve("Delete Guarantor", top_k=5)
for r in results:
    print(r['step_text'][:60], r.get('ce_score'), r.get('marker'))
```

Expected: real repo steps returned with ce_score values.

---

### Task 7 — RAG Engine

Build these files:

- `forge/infrastructure/rag_engine.py` — Port from `reference/retrieval/cas_knowledge_retrieval.py`. Full stack as specified in `docs/FORGE_SRS.md` Section 4.3:
  - Lazy-load `cas_knowledge.faiss` and doc_chunks metadata
  - Embed query → FAISS search → stage/screen boost → top_k chunks
  - On-demand distillation: LLM generates focused summary per context
  - Distillation cache: check `rag_cache` table before calling LLM
  - Cache key: `{screen}_{stage}_{lob}`

**Verification:**

```python
from forge.infrastructure.rag_engine import get_context
result = get_context(screen="Collateral", stage="Credit Approval", lob="HL", query="mandatory fields")
print(result[:200])
```

Expected: non-empty text referencing actual CAS document content (or "model not loaded" error if LLM not available yet — that is acceptable here).

---

### Task 8 — JIRA Client

Build these files:

- `forge/infrastructure/jira_client.py` — Two modes:
  - PAT mode: fetch story using `jira-python` library, PAT from `settings.jira_pat` or per-request override
  - CSV mode: parse raw CSV string — port parsing logic from `reference/parsing/jira_parser.py`
  - Fetch everything: description, AC, all comments, all custom fields
  - Never fail silently — always return structured result with `parse_quality` and `missing_fields`

**Verification:**

```python
from forge.infrastructure.jira_client import parse_csv
# Use any sample from reference/samples/jira/
with open("reference/samples/jira/sample.csv") as f:
    raw = f.read()
result = parse_csv(raw)
print(result['parse_quality'], result.get('missing_fields'))
```

---

### Task 9 — All 11 Agents

Build all agent files. Read `docs/FORGE.md` Section 8 and `docs/CAS_ATDD_Context.md` before writing any agent.

Build in this order:

1. `agent_01_reader.py`
2. `agent_02_domain_expert.py`
3. `agent_03_scope_definer.py`
4. `agent_04_coverage_planner.py`
5. `agent_05_action_decomposer.py`
6. `agent_06_retriever.py`
7. `agent_07_composer.py`
8. `agent_08_atdd_expert.py`
9. `agent_09_writer.py`
10. `agent_10_critic.py`
11. `agent_11_reporter.py`

**Rules for every agent:**

- System prompt defined as Python string constant in the agent file
- System prompt structure: ROLE → CONTEXT → JOB → OUTPUT → RULES → HARD BANS
- Agent output is always JSON — parse strictly, never silently accept partial parse
- Log input state summary at start, log output summary at end
- Catch all exceptions, log them, re-raise — never swallow
- Return best attempt with markers on partial failure — never empty state

**Wire agents into graph.py** — replace empty stubs with real implementations.

**Verification:**

```python
from forge.core.graph import run_graph
from forge.core.state import ForgeState

# Use a CSV sample
state = ForgeState(
    user_id="1",
    jira_input_mode="csv",
    jira_csv_raw=open("reference/samples/jira/sample.csv").read(),
    flow_type="unordered",
    three_amigos_notes="",
    jira_story_id=None,
    jira_pat_override=None
)
result = run_graph(state)
print(result.get('feature_file', 'NO OUTPUT')[:500])
```

Expected: feature file content in result, even if LLM is slow.

---

### Task 10 — Chat Engine

Build these files:

- `forge/chat/router.py` — Classify message as `cas` | `atdd` | `general`. One lightweight LLM call. Returns context type string.
- `forge/chat/session_store.py` — PostgreSQL persistence. `save_message()`, `load_session()`, `list_sessions()`, `delete_session()`. Per-user isolation.
- `forge/chat/chat_engine.py` — Conversation loop. When context is `cas` — call `rag_engine.get_context()` and inject into system prompt. Conversation history from session store. Returns response + context_type.

**Verification:**

```bash
# With server running:
curl -X POST http://localhost:8000/chat/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is the mandatory first step in ordered flows?", "session_id": null}'
# Expected: response mentioning prerequisite step, context_type: "atdd" or "cas"
```

---

### Task 11 — All FastAPI Routes

Build these files:

- `forge/api/routes/chat.py` — All chat endpoints per `docs/FORGE_SRS.md` Section 3
- `forge/api/routes/generate.py` — Generation job endpoints. Use an in-process `asyncio` task registry for dev/demo. Persist job status to `generation_jobs`. SSE stream with valid JSON events. Elapsed time must update per agent. Failed event on exception.

Generation job rules:

- `POST /generate/` creates a DB row with `pending`, starts one async task, and returns `job_id`.
- Worker sets status `running`, updates `current_agent`, `elapsed_seconds`, then sets `done` or `failed`.
- If server restarts, any `pending` or `running` job older than startup time is marked `failed` with reason `Server restarted before job completed`.
- One active generation job per user in dev/demo. If user already has `pending` or `running`, return HTTP 409 with clear message.
- Do not run generation inside the request thread.
- `forge/api/routes/settings.py` — Settings load, save, profile update, password change, test-jira, test-model
- `forge/api/routes/admin.py` — User create, list, deactivate. Admin JWT required.

**SSE stream contract — exact format:**

Backend accepts normal `Authorization: Bearer <token>` headers for this endpoint. Frontend must consume it using authenticated `fetch()` streaming, not native browser `EventSource`, because EventSource cannot reliably send Authorization headers.

```
data: {"agent": 3, "elapsed": 12}\n\n
data: {"agent": 4, "elapsed": 28}\n\n
data: {"status": "done"}\n\n
```

Or on failure:

```
data: {"status": "failed", "reason": "LLM model not loaded..."}\n\n
```

Every event must be valid JSON with double quotes. Never single-quoted pseudo-JSON.

**Verification:**

```bash
# Full generate test with CSV:
curl -X POST http://localhost:8000/generate/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"jira_input_mode":"csv","jira_csv_raw":"...","flow_type":"unordered","three_amigos_notes":"","module":"cas"}'
# Returns: {"job_id": "..."}

# Then stream:
curl http://localhost:8000/generate/<job_id>/stream \
  -H "Authorization: Bearer <token>"
# Expected: SSE events with agent numbers incrementing
```

---

### Task 12 — Verify Setup Script

Build:

- `forge/scripts/verify_setup.py` — Checks all paths, models, DB, tables. Prints pass/fail per item. Exit code 0 = all pass.

Full check list in `docs/FORGE_SRS.md` Section 4.7.

```bash
python -m forge.scripts.verify_setup
```

---

### Task 13 — Integration Test

Run full pipeline on a real sample:

```bash
# Use a CSV from reference/samples/jira/
python -c "
from forge.core.graph import run_graph
from forge.core.state import ForgeState
import json

with open('reference/samples/jira/YOUR_SAMPLE.csv') as f:
    csv_raw = f.read()

state = ForgeState(
    user_id='1',
    jira_input_mode='csv',
    jira_csv_raw=csv_raw,
    flow_type='unordered',
    three_amigos_notes='',
    jira_story_id=None,
    jira_pat_override=None
)
result = run_graph(state)
print('=== FEATURE FILE ===')
print(result.get('feature_file','NO OUTPUT'))
print('=== GAP REPORT ===')
print(json.dumps(result.get('final_output',{}).get('gap_report',{}), indent=2))
"
```

Evaluate output on:

- Story scope respected — no ambient scope bleed
- Steps repo-grounded — marker rate reasonable
- Markers placed honestly — no silent drops
- ATDD structural rules pass — no `But`, no oversized Then blocks
- Gap report non-empty and accurate

---

## Reporting After Each Task

After completing each task, report:

```
Task N — [Name] — COMPLETE

Files created or modified:
- forge/path/to/file.py

How to verify:
- [exact command to run]

Verification output:
- [paste actual output]

Deviations from spec:
- [any decision made differently from docs, with reason]

Ready for Task N+1.
```

Do not move to next task until Anand confirms.

Also append a short entry to `CHANGELOG.md` and update `CONTEXT.md` before reporting completion.

---

## When You Are Stuck

1. Re-read `docs/FORGE.md` — architecture question
2. Re-read `docs/FORGE_SRS.md` — implementation question
3. Re-read `docs/CAS_ATDD_Context.md` — domain question
4. Read the V2 reference file for the component — implementation detail
5. Ask Anand — CAS domain clarification only, not architecture

---

## CONTEXT.md and CHANGELOG.md — Update Every Session

At the end of every session, update `CONTEXT.md` as the current snapshot:

```markdown
## Last Updated

[date and time]

## Completed Tasks

- Task 1 — Core Foundation — DONE
- Task 2 — DB + Auth — DONE
  ...

## Current Task

Task N — [name] — [status]

## What Was Just Done

[2-3 sentences]

## What Is Next

Task N+1 — [name]

## Known Issues

[anything broken or deferred]

## Decisions Made

[any deviation from spec with reason]
```

### When Done

- Create docs/How_to_run.md
- Create docs/How_to_maintain.md
- Create docs/User_Manual.md
- Create docs/How_to_Setup.md

Codex reads this file too. Keep it accurate.

Then append to `CHANGELOG.md` using this format:

```markdown
## YYYY-MM-DD HH:mm — Claude Code — Task N — Short title

### Changed

- ...

### Verified

- Command: `...`
- Result: pass/fail + short output

### Decisions

- ...

### Next

- ...

### Blockers

- None / ...
```

Do not rewrite old changelog entries except to fix obvious typos. Newest entry goes at the top.

---

_CLAUDE.md — Claude Code build instructions._  
_Architecture: `docs/FORGE.md`_  
_Implementation detail: `docs/FORGE_SRS.md`_  
_Domain knowledge: `docs/CAS_ATDD_Context.md`_

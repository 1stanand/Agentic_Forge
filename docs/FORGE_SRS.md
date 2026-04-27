# FORGE_SRS.md

## Software Requirements Specification — Forge Agentic

**Audience:** Claude Code, Codex  
**Companion to:** `docs/FORGE.md`  
**Date:** April 2026

---

## READ THIS FIRST

FORGE.md is the architecture overview. This document is the implementation detail. When FORGE.md says "port from V2" or "see FORGE_SRS.md" — this is where you go.

Read Section 1 (Glossary) before reading anything else. Every term used in this project is defined there. Do not assume you know what RAPTOR, Self-RAG, HyDE, or On-Demand Distillation mean in this context — read the definitions.

---

## 1. Glossary — Every Term Defined

### RAPTOR

**Recursive Abstractive Processing for Tree Organized Retrieval.**

In Forge, RAPTOR refers to the hierarchical chunking of CAS PDF documents into a searchable knowledge tree. PDFs are chunked at the page/section level, embedded with `all-MiniLM-L6-v2`, and stored in a FAISS index (`cas_knowledge.faiss`) alongside PostgreSQL metadata (`doc_chunks` table). The "tree" aspect means chunks are associated with stage/screen/section context, allowing filtered retrieval by hierarchy level. Built once by `forge/scripts/build_knowledge.py`. Not rebuilt at runtime.

### HyDE (Hypothetical Document Embeddings)

**A query expansion technique.**

Instead of embedding the raw user query and searching, HyDE generates a hypothetical answer to the query first, then embeds that answer. The hypothesis is closer in embedding space to real answers than the raw question is. In Forge, HyDE-style expansion happens inside `query_expander.py` — the `expand_for_vector()` function generates expanded phrasings of the action text before FAISS search. This bridges the vocabulary gap between how testers write actions and how steps are written in the repo.

### On-Demand Distillation

**LLM-generated summaries of CAS documents, cached per context.**

Agent 2 (Domain Expert) needs CAS knowledge focused on a specific screen + stage + LOB combination. Instead of dumping all retrieved chunks into the LLM prompt, the RAG engine calls the LLM to generate a focused summary of the retrieved chunks for that specific context. The summary is cached in PostgreSQL with key `{screen}_{stage}_{lob}`. On a cache hit, the LLM is not called — the cached summary is returned. This makes Agent 2 fast on repeated contexts while staying accurate on new ones.

### Self-RAG Gate

**A retrieval quality check with one retry.**

After the step retrieval stack returns candidates, the top candidate's cross-encoder score is checked against `LOW_MATCH_THRESHOLD`. If the score is below threshold, the retrieval is considered poor quality. Self-RAG fires: the query is expanded further and retrieval is re-run once. Maximum one retry. The retry result is used regardless of whether it improved. The purpose is to catch cases where the initial query was too narrow and a broader formulation finds better matches.

### Cross-Encoder Reranker

**A second-pass relevance scorer.**

After FAISS + FTS + trigram retrieval produces candidates, the cross-encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) re-scores each candidate as a (query, step_text) pair. Unlike embedding similarity (which compares independently), cross-encoders see both texts together and produce a more accurate relevance score. Results are sorted by `ce_score`. This is the final ranking signal before markers are assigned.

### GraphRAG Validator

**A knowledge graph-based validity checker.**

NetworkX graph: Stage → Screen → Entity → Role. Built from `reference/config/domain/*.toml` files. After step retrieval, each candidate step is validated against this graph — does this step belong to a valid screen for this stage? Does the role in the step match the entity type in the story? Invalid combinations produce `[ROLE_GAP]` marker. This catches steps that are semantically similar but contextually wrong.

### FAISS

**Facebook AI Similarity Search.**

Vector similarity index. Used in two separate indices in Forge:

1. `faiss_index.bin` — step embeddings from the feature repo
2. `cas_knowledge.faiss` — CAS document chunk embeddings

Both use `all-MiniLM-L6-v2` embeddings (dim=384, cosine similarity).

### Markers

**Honest gap signals in generated steps.**

Three markers, placed inline as Gherkin comments:

- `[NEW_STEP_NOT_IN_REPO]` — No matching step found in repo. Step is new, must be written.
- `[LOW_MATCH]` — A step was found but confidence is below threshold. Human review needed.
- `[ROLE_GAP]` — A step was found but the role/entity context does not match. Wrong actor.

Markers travel from Agent 6 through every agent to the final output. They are never dropped silently.

### LogicalID

**A unique identifier for an ordered test thread.**

Format: `CAS_{storyID}_{outcome}` e.g. `CAS_256008_REJECT`, `CAS_256008_APPROVE`.

LogicalIDs tie ordered scenarios together. The prerequisite first step references the LogicalID. `OpenApplication.feature` uses LogicalIDs to chain runs. Agent 4 assigns them. Agent 5 uses them. Agent 8 validates them. Agent 9 writes them into every ordered scenario title.

### STP (Straight Through Process)

**Pre-built infrastructure for stage traversal in ordered flows.**

Ordered scenarios do not write their own navigation from stage to stage. STP via `OpenApplication.feature` handles that. Forge generates scenarios that start at the target stage, assuming STP has already run. The mandatory first step signals this dependency explicitly.

### Distillation Cache

**PostgreSQL table caching On-Demand Distillation results.**

Table: `rag_cache`. Cache key: `{screen}_{stage}_{lob}`. On hit — return cached summary. On miss — call LLM, store result, return. Invalidated manually when CAS PDFs are updated and knowledge is rebuilt.

### pg_trgm

**PostgreSQL trigram extension for fuzzy text search.**

Enables similarity search on step text using character trigrams. Catches typos, partial matches, and vocabulary variations that exact FTS misses. One of three retrieval channels in the step retrieval stack.

---

## 2. Database Schema — Complete

DB name: `agentic_forge_local`

Run `forge/scripts/setup_db.py` to create all tables fresh.

---

### Users and Auth

```sql
CREATE TABLE users (
    id              SERIAL PRIMARY KEY,
    username        VARCHAR(100) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,       -- argon2 hash
    display_name    VARCHAR(200),
    is_admin        BOOLEAN DEFAULT FALSE,
    is_active       BOOLEAN DEFAULT TRUE,
    jira_pat        TEXT,                         -- encrypted PAT ciphertext only; never plaintext
    theme_pref      VARCHAR(10) DEFAULT 'dark',   -- dark | light
    created_at      TIMESTAMP DEFAULT NOW(),
    last_login      TIMESTAMP
);
```

---

### Chat

```sql
CREATE TABLE chat_sessions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     INTEGER REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(200),        -- first message truncated to 60 chars
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE chat_messages (
    id           UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id   UUID REFERENCES chat_sessions(id) ON DELETE CASCADE,
    role         VARCHAR(20) NOT NULL,    -- user | assistant
    content      TEXT NOT NULL,
    context_type VARCHAR(20),            -- cas | atdd | general
    created_at   TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_chat_sessions_user ON chat_sessions(user_id);
CREATE INDEX idx_chat_messages_session ON chat_messages(session_id);
```

---

### Generation Jobs

```sql
CREATE TABLE generation_jobs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         INTEGER REFERENCES users(id),
    status          VARCHAR(20) DEFAULT 'pending',  -- pending | running | done | failed
    jira_story_id   VARCHAR(50),
    flow_type       VARCHAR(20),
    module          VARCHAR(20) DEFAULT 'cas',
    feature_file    TEXT,
    gap_report      JSONB,
    confidence_score FLOAT,
    error_message   TEXT,
    current_agent   INTEGER DEFAULT 0,
    elapsed_seconds INTEGER DEFAULT 0,
    started_at      TIMESTAMP,
    completed_at    TIMESTAMP,
    created_at      TIMESTAMP DEFAULT NOW(),
    updated_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_jobs_user ON generation_jobs(user_id);
CREATE INDEX idx_jobs_status ON generation_jobs(status);
CREATE INDEX idx_jobs_updated_at ON generation_jobs(updated_at);
```

---

### User Settings

```sql
CREATE TABLE user_settings (
    user_id         INTEGER PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
    jira_url        VARCHAR(500),
    jira_pat        TEXT,            -- encrypted PAT ciphertext only; never plaintext
    ollama_url      VARCHAR(500),    -- kept for future, not used
    updated_at      TIMESTAMP DEFAULT NOW()
);
```

---

### Feature Repo — 4 Normalized Tables

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE TABLE features (
    id              SERIAL PRIMARY KEY,
    file_path       TEXT UNIQUE NOT NULL,
    file_name       TEXT NOT NULL,
    folder_path     TEXT,
    flow_type       VARCHAR(20),         -- ordered | unordered | unknown
    file_tags       TEXT[],              -- all @tags at file level
    file_dicts      JSONB,               -- file-level #${...} dictionaries
    file_annotations TEXT[],             -- all annotation tags
    scenario_count  INTEGER DEFAULT 0,
    lobs_present    TEXT[],
    stages_present  TEXT[],
    story_ids       TEXT[],              -- @CAS-XXXXXX tags
    mtime           FLOAT,               -- file modification time for incremental ingest
    indexed_at      TIMESTAMP DEFAULT NOW()
);

CREATE TABLE scenarios (
    id                  SERIAL PRIMARY KEY,
    feature_id          INTEGER REFERENCES features(id) ON DELETE CASCADE,
    title               TEXT NOT NULL,
    scenario_type       VARCHAR(30),        -- Scenario | Scenario Outline | Background
    scenario_tags       TEXT[],
    scenario_dicts      JSONB,              -- scenario-level dictionaries
    scenario_annotations TEXT[],
    logical_id          TEXT,               -- for ordered scenarios
    step_count          INTEGER DEFAULT 0,
    position            INTEGER,            -- order within feature file
    has_examples        BOOLEAN DEFAULT FALSE
);

CREATE TABLE steps (
    id              SERIAL PRIMARY KEY,
    scenario_id     INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    feature_id      INTEGER REFERENCES features(id) ON DELETE CASCADE,
    step_keyword    VARCHAR(20),     -- Given | When | Then | And | But | *
    step_text       TEXT NOT NULL,   -- full step text
    step_position   INTEGER,         -- position within scenario
    screen_context  TEXT,            -- inferred from navigation anchors — DYNAMIC
    stage_hint      TEXT,
    is_background   BOOLEAN DEFAULT FALSE,
    has_docstring   BOOLEAN DEFAULT FALSE,
    docstring_text  TEXT
);

CREATE TABLE example_blocks (
    id              SERIAL PRIMARY KEY,
    scenario_id     INTEGER REFERENCES scenarios(id) ON DELETE CASCADE,
    block_position  INTEGER,          -- which Examples block within scenario
    headers         TEXT[],
    rows            JSONB,            -- list of {col: val} dicts
    block_dicts     JSONB,            -- example-level dictionaries
    block_tags      TEXT[]
);

-- Materialized view — deduplicated steps with usage counts
CREATE MATERIALIZED VIEW unique_steps AS
SELECT
    step_text,
    step_keyword,
    MIN(screen_context) AS screen_context,
    MIN(stage_hint) AS stage_hint,
    COUNT(*) AS usage_count,
    array_agg(DISTINCT f.file_name) AS source_files,
    array_agg(DISTINCT f.folder_path) AS source_folders
FROM steps s
JOIN scenarios sc ON s.scenario_id = sc.id
JOIN features f ON s.feature_id = f.id
WHERE s.is_background = FALSE
GROUP BY s.step_text, s.step_keyword;

CREATE UNIQUE INDEX idx_unique_steps_text ON unique_steps(step_text);
CREATE INDEX idx_steps_screen ON steps(screen_context);
CREATE INDEX idx_steps_text_trgm ON steps USING gin(step_text gin_trgm_ops);
CREATE INDEX idx_unique_steps_trgm ON unique_steps USING gin(step_text gin_trgm_ops);
CREATE INDEX idx_steps_fts ON steps USING gin(to_tsvector('english', step_text));
CREATE INDEX idx_unique_steps_fts ON unique_steps USING gin(to_tsvector('english', step_text));
```

---

### CAS Document Knowledge

```sql
CREATE TABLE doc_chunks (
    id              SERIAL PRIMARY KEY,
    chunk_id        TEXT UNIQUE NOT NULL,   -- {doc_basename}_{page}_{chunk_idx}
    doc_path        TEXT,                   -- source PDF basename
    section_title   TEXT,
    stage_hint      TEXT,                   -- inferred from section content
    screen_hint     TEXT,                   -- inferred from section content
    text            TEXT NOT NULL,
    page_range      TEXT,                   -- e.g. "12-13"
    token_count     INTEGER,
    faiss_pos       INTEGER                 -- positional index in cas_knowledge.faiss
);

CREATE TABLE rag_cache (
    id          SERIAL PRIMARY KEY,
    cache_key   TEXT UNIQUE NOT NULL,       -- "{screen}_{stage}_{lob}"
    summary     TEXT NOT NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    hit_count   INTEGER DEFAULT 0
);

CREATE INDEX idx_doc_chunks_stage ON doc_chunks(stage_hint);
CREATE INDEX idx_doc_chunks_screen ON doc_chunks(screen_hint);
```

---

## 3. API Endpoints — Full Specification

Base URL: `http://localhost:8000`  
Auth: `Authorization: Bearer <jwt_token>` on all protected routes.

Streaming note: `/generate/{job_id}/stream` is also protected. Browser clients must consume it using `fetch()` streaming so the Authorization header can be sent. Do not use native `EventSource` unless auth is redesigned to HttpOnly cookies or one-time stream tokens.

---

### POST /auth/login

**Auth:** None  
**Request:**

```json
{
  "username": "anand",
  "password": "forge123"
}
```

**Response 200:**

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "display_name": "Anand",
  "user_id": 1,
  "is_admin": false
}
```

**Response 401:**

```json
{ "detail": "Invalid username or password" }
```

---

### POST /auth/logout

**Auth:** Required  
**Request:** Empty body  
**Response 200:**

```json
{ "message": "Logged out" }
```

---

### POST /chat/

**Auth:** Required  
**Request:**

```json
{
  "message": "What fields are mandatory at the KYC stage?",
  "session_id": "uuid-or-null"
}
```

If `session_id` is null — create new session.  
**Response 200:**

```json
{
  "response": "At KYC stage, the mandatory fields are...",
  "session_id": "550e8400-...",
  "context_type": "cas",
  "session_title": "What fields are mandatory at..."
}
```

---

### GET /chat/sessions

**Auth:** Required  
**Response 200:**

```json
[
  {
    "id": "550e8400-...",
    "title": "What fields are mandatory at...",
    "created_at": "2026-04-26T19:00:00",
    "updated_at": "2026-04-26T19:05:00",
    "message_count": 4
  }
]
```

---

### GET /chat/sessions/{session_id}

**Auth:** Required  
**Response 200:**

```json
{
  "id": "550e8400-...",
  "title": "What fields are mandatory at...",
  "messages": [
    {
      "role": "user",
      "content": "What fields...",
      "context_type": "cas",
      "created_at": "..."
    },
    {
      "role": "assistant",
      "content": "At KYC stage...",
      "context_type": "cas",
      "created_at": "..."
    }
  ]
}
```

---

### DELETE /chat/sessions/{session_id}

**Auth:** Required  
**Response 200:**

```json
{ "message": "Session deleted" }
```

---

### POST /generate/

**Auth:** Required  
**Request:**

```json
{
  "jira_input_mode": "jira_id",
  "jira_story_id": "CAS-256008",
  "jira_csv_raw": null,
  "flow_type": "ordered",
  "three_amigos_notes": "Guarantor must see all sections",
  "module": "cas",
  "jira_pat_override": null
}
```

Or CSV mode:

```json
{
  "jira_input_mode": "csv",
  "jira_story_id": null,
  "jira_csv_raw": "Summary,Description,AC\n...",
  "flow_type": "unordered",
  "three_amigos_notes": "",
  "module": "cas",
  "jira_pat_override": null
}
```

**Response 202:**

```json
{ "job_id": "550e8400-..." }
```

**Job creation behavior:**

- Insert row in `generation_jobs` with `status="pending"`.
- Return `job_id` immediately.
- `job_runner.py` starts the job when a worker slot is available.
- Dev/demo default is one job at a time: `MAX_CONCURRENT_JOBS=1`.

---

### GET /generate/{job_id}/stream

**Auth:** Required  
**Client:** authenticated `fetch()` streaming with `Authorization: Bearer <jwt_token>`  
**Response:** Server-Sent Events-compatible text stream

Progress event (one per agent completion):

```
data: {"agent": 3, "elapsed": 12}
```

Where `agent` is 1–11 matching the agent that just completed.

Done event:

```
data: {"status": "done"}
```

Failed event:

```
data: {"status": "failed", "reason": "LLM model not loaded. Check LLM_MODEL_PATH in .env"}
```

The backend must emit valid JSON after `data:` for every event. No plain-text status lines.

**Agent name mapping for UI:**

```
1  → Reader
2  → Domain Expert
3  → Scope Definer
4  → Coverage Planner
5  → Action Decomposer
6  → Retriever
7  → Composer
8  → ATDD Expert
9  → Writer
10 → Critic
11 → Reporter
```

---

### GET /generate/{job_id}/result

**Auth:** Required  
**Response 200 (job done):**

```json
{
  "job_id": "550e8400-...",
  "feature_file": "@CAS-256008\n@NotImplemented\n@Order\nFeature: ...",
  "gap_report": {
    "story_id": "CAS-256008",
    "coverage_gaps": ["Guarantor rejection path not covered"],
    "markers_summary": {
      "NEW_STEP_NOT_IN_REPO": 3,
      "LOW_MATCH": 1,
      "ROLE_GAP": 0
    },
    "atdd_issues": [],
    "confidence_score": 0.82,
    "recommendation": "Review 3 new steps with team before committing"
  },
  "confidence_score": 0.82
}
```

**Response 202 (job still running):**

```json
{ "status": "running", "current_agent": 5, "elapsed": 34 }
```

**Response 404:**

```json
{ "detail": "Job not found" }
```

---

### GET /settings/

**Auth:** Required  
**Response 200:**

```json
{
  "jira_url": "https://jira.nucleus.com",
  "jira_pat": "***masked***",
  "display_name": "Anand",
  "theme_pref": "dark"
}
```

---

### PUT /settings/

**Auth:** Required  
**Request:**

```json
{
  "jira_url": "https://jira.nucleus.com",
  "jira_pat": "ATATT3x..."
}
```

**Response 200:**

```json
{ "message": "Settings saved" }
```

---

### PUT /settings/profile

**Auth:** Required  
**Request:**

```json
{ "display_name": "Anand Kumar" }
```

**Response 200:**

```json
{ "message": "Profile updated", "display_name": "Anand Kumar" }
```

---

### PUT /settings/password

**Auth:** Required  
**Request:**

```json
{
  "current_password": "forge123",
  "new_password": "newpass456"
}
```

**Response 200:**

```json
{ "message": "Password updated" }
```

**Response 400:**

```json
{ "detail": "Current password incorrect" }
```

---

### POST /settings/test-jira

**Auth:** Required  
**Request:** Empty body (uses saved settings)  
**Response 200:**

```json
{ "status": "ok", "message": "JIRA connection successful. Project: CAS" }
```

**Response 200 (failed):**

```json
{ "status": "error", "message": "Connection refused. Check JIRA URL and PAT." }
```

---

### POST /settings/test-model

**Auth:** Required  
**Request:** Empty body  
**Response 200:**

```json
{
  "status": "ok",
  "message": "Model loaded. Response length: 12 tokens.",
  "response_length": 12
}
```

**Response 200 (model not loaded):**

```json
{
  "status": "error",
  "message": "LLM model not loaded. Check LLM_MODEL_PATH in .env and restart."
}
```

---

### POST /admin/users

**Auth:** Admin JWT required  
**Request:**

```json
{
  "username": "ravi",
  "display_name": "Ravi Kumar",
  "password": "forge123",
  "is_admin": false
}
```

**Response 201:**

```json
{
  "id": 2,
  "username": "ravi",
  "display_name": "Ravi Kumar",
  "created_at": "..."
}
```

---

### GET /admin/users

**Auth:** Admin JWT required  
**Response 200:**

```json
[
  {
    "id": 1,
    "username": "anand",
    "display_name": "Anand",
    "is_active": true,
    "last_login": "..."
  },
  {
    "id": 2,
    "username": "ravi",
    "display_name": "Ravi Kumar",
    "is_active": true,
    "last_login": null
  }
]
```

---

### DELETE /admin/users/{user_id}

**Auth:** Admin JWT required  
**Response 200:**

```json
{ "message": "User deactivated" }
```

Note: Deactivates, does not delete. Chat history preserved.

---

## 4. Infrastructure Components — Detailed Behavior

---

### 4.1 LLM Client (`forge/core/llm.py`)

Single lazy-loaded instance. One instance for the entire application lifetime.

```python
class LLMNotLoadedError(Exception):
    pass

_llm_instance = None

def get_llm():
    global _llm_instance
    if _llm_instance is None:
        path = get_settings().llm_model_path
        if not Path(path).exists():
            raise LLMNotLoadedError(
                f"LLM model not found at: {path}\n"
                f"Update LLM_MODEL_PATH in .env and restart the server."
            )
        logger.info(f"Loading LLM from {path}")
        _llm_instance = Llama(
            model_path=str(path),
            n_gpu_layers=get_settings().llm_gpu_layers,
            n_ctx=get_settings().llm_context_size,
            n_threads=get_settings().llm_threads,
            verbose=False
        )
        logger.info("LLM loaded successfully")
    return _llm_instance

def llm_complete(prompt: str, system: str = "", max_tokens: int = 2048) -> str:
    """Single completion call. Raises LLMNotLoadedError if model missing."""
    llm = get_llm()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    response = llm.create_chat_completion(messages=messages, max_tokens=max_tokens)
    return response["choices"][0]["message"]["content"]
```

Any endpoint calling `get_llm()` or `llm_complete()` must catch `LLMNotLoadedError` and return:

```json
{ "error": "LLM model not loaded. Check LLM_MODEL_PATH in .env and restart." }
```

---

### 4.2 Step Retrieval Stack (`forge/infrastructure/step_retriever.py`)

Full stack — port from `reference/retrieval/retrieval.py`. Every layer required.

```
Input: action_text (str), top_k (int), screen_filter (str), stage_hint (str)

Step 1 — Query Preparation
  normalise_query_text(action_text)              ← port from query_expander.py
  vector_query  = expand_for_vector(normalised)  ← richer, synonym-expanded
  fts_query     = expand_for_fts(normalised)     ← FTS-safe operators
  trgm_query    = expand_for_trigram(normalised) ← trigram-safe form

Step 2 — Three Channel Retrieval
  FAISS channel:
    embed vector_query → search faiss_index.bin → top (top_k * 3) candidate IDs
    raw scores: L2 distance → convert to similarity

  FTS channel:
    SELECT id, ts_rank(to_tsvector('english', step_text),
                       plainto_tsquery('english', fts_query)) AS score
    FROM unique_steps
    WHERE to_tsvector('english', step_text) @@ plainto_tsquery('english', fts_query)
    LIMIT top_k * 3

  Trigram channel:
    SELECT id, similarity(step_text, trgm_query) AS score
    FROM unique_steps
    WHERE similarity(step_text, trgm_query) > 0.2
    ORDER BY score DESC
    LIMIT top_k * 3

Step 3 — Score Normalisation
  _minmax(faiss_scores)   → [0, 1]
  _minmax(fts_scores)     → [0, 1]
  _minmax(trgm_scores)    → [0, 1]

Step 4 — Weighted Merge
  combined_score = (faiss_norm * 0.50) + (fts_norm * 0.30) + (trgm_norm * 0.20)
  Deduplicate by step ID — keep highest combined_score

Step 5 — Stage Boost
  if stage_hint in step.stage_hint: score *= 1.6
  elif stage auto-detected from query: score *= 1.3
  if sub-stage tag matches: score *= 1.15

Step 6 — Rich Context Fetch (_fetch_context)
  For each top candidate:
    JOIN steps + scenarios + features
    → step_text, step_keyword, screen_context, stage_hint
    → scenario title, scenario tags, scenario dicts
    → file_name, file_path, file_tags, flow_type
    → sibling steps (same scenario, ordered by position)
    → example_blocks for scenario

Step 7 — Cross-Encoder Rerank (_cross_encode)
  pairs = [(action_text, candidate.step_text) for candidate in top_candidates]
  ce_scores = cross_encoder.predict(pairs)
  Sort by ce_score descending
  Attach ce_score to each candidate

Step 8 — Self-RAG Gate
  if results[0].ce_score < LOW_MATCH_THRESHOLD and retry_count == 0:
    expanded_query = expand_for_vector(action_text) + " " + action_text
    return retrieve(expanded_query, top_k, screen_filter, stage_hint, retry_count=1)

Step 9 — Marker Assignment
  ce_score >= 0.7:              no marker
  0.3 <= ce_score < 0.7:        [LOW_MATCH]
  ce_score < 0.3 or no result:  [NEW_STEP_NOT_IN_REPO]
  role mismatch (GraphRAG):     [ROLE_GAP]

Output: List[{step_text, step_keyword, ce_score, marker, context: {scenario, file, siblings}}]
```

---

### 4.3 RAG Engine (`forge/infrastructure/rag_engine.py`)

Port core retrieval from `reference/retrieval/cas_knowledge_retrieval.py`. Keep distillation cache from V3.

```
Input: query (str), stage_hint (str), screen_hint (str), lob (str), top_k (int=5)

Step 1 — Cache Check
  cache_key = f"{screen_hint}_{stage_hint}_{lob}"
  hit = SELECT summary FROM rag_cache WHERE cache_key = %s
  if hit: UPDATE hit_count, return hit.summary

Step 2 — Embed Query
  embedding = embedder.embed(query)   ← all-MiniLM-L6-v2

Step 3 — FAISS Search
  candidates = cas_knowledge_faiss.search(embedding, top_k * 2)
  → list of (faiss_pos, distance)

Step 4 — Fetch Chunk Metadata
  faiss_positions = [c.faiss_pos for c in candidates]
  chunks = SELECT * FROM doc_chunks WHERE faiss_pos = ANY(%s)

Step 5 — Stage/Screen Boost
  for chunk in chunks:
    if chunk.stage_hint == stage_hint: chunk.score *= 1.5
    if chunk.screen_hint == screen_hint: chunk.score *= 1.3
  Sort by score, take top_k

Step 6 — On-Demand Distillation
  context_text = "\n\n".join(chunk.text for chunk in top_k_chunks)
  system = "You are a CAS domain expert. Summarize the following CAS documentation
            for a tester working on screen '{screen}' at stage '{stage}' for LOB '{lob}'.
            Be specific. Focus on fields, rules, and conditional behavior."
  summary = llm_complete(context_text, system=system, max_tokens=512)

Step 7 — Cache Result
  INSERT INTO rag_cache (cache_key, summary) VALUES (%s, %s)
  ON CONFLICT (cache_key) DO UPDATE SET summary = %s, hit_count = hit_count + 1

Output: summary (str)
```

---

### 4.4 Feature Repo Indexer (`forge/infrastructure/repo_indexer.py`)

Port from `reference/tools/ingest.py`. Full incremental ingest.

```
Mode 1 — Incremental (default):
  1. db_fetch_all_mtimes() → {file_path: mtime} from features table
  2. Walk FEATURES_REPO_PATH for *.feature files
  3. Skip PickApplication.feature and OpenApplication.feature
  4. Compare mtime:
     - New file (not in DB): parse → insert
     - Changed file (mtime differs): db_delete_feature() → parse → insert
     - Removed file (in DB, not on disk): db_delete_feature() (CASCADE cleans children)
     - Unchanged: skip
  5. db_refresh_unique_steps()   ← REFRESH MATERIALIZED VIEW unique_steps

Mode 2 — Full Rebuild (--full-rebuild flag):
  1. Run schema.sql to drop and recreate all tables
  2. Walk all *.feature files
  3. Parse and insert all
  4. db_refresh_unique_steps()
```

---

### 4.5 Feature Parser (`forge/infrastructure/feature_parser.py`)

Port from `reference/parsing/feature_parser.py`. All CAS extensions required.

CAS-specific extensions to parse correctly:

**Background steps** — accumulate and prepend to every subsequent scenario in the file:

```gherkin
Background:
  Given user is on CAS Login Page   ← prepended to every Scenario
```

**Doc strings** — append to preceding step text:

```gherkin
When user enters address
"""
123 Main Street, Mumbai
"""
← step_text becomes: "user enters address\n123 Main Street, Mumbai"
```

**Header-based Examples tables** — not generic col_0/col_1:

```gherkin
Examples:
  | ProductType | ApplicationStage |
  | HL          | DDE              |
← headers = ["ProductType", "ApplicationStage"]
← rows = [{"ProductType": "HL", "ApplicationStage": "DDE"}]
```

**Dictionary parsing** — `#${Key:["v1","v2"]}`:

```python
def _parse_dicts(line: str) -> Optional[Dict]:
    # Parse #${ProductType:["HL","PL","SHG"]} → {"ProductType": ["HL","PL","SHG"]}
```

**Conflict detection** — `@Order` + dictionaries in same file → flag:

```python
def _check_conflict(file_tags, file_dicts) -> Optional[str]:
    if "@Order" in file_tags and file_dicts:
        return "Ordered file cannot contain dictionaries"
```

**Screen context inference** — dynamic, never static:

```python
# After each scenario closes, call:
infer_screen_contexts(scenario_steps)
# Uses _ANCHOR_PATTERNS to detect navigation steps
# Sets step["screen_context"] based on detected pattern
# SCREEN_NAME_MAP is built from DB after ingest — not used during parsing
```

**Encoding handling**:

```python
for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
    try:
        content = path.read_text(encoding=encoding)
        break
    except UnicodeDecodeError:
        continue
```

---

### 4.6 Build Knowledge Script (`forge/scripts/build_knowledge.py`)

Port from `reference/tools/build_pdf_chunk_corpus.py`. Builds `cas_knowledge.faiss`.

```
Input: PDF files in CAS_DOCS_PATH

For each PDF:
  1. Extract text page by page using pdfplumber
  2. Detect section titles from font size / formatting
  3. _split_into_chunks(page_text, max_tokens=300)
  4. _infer_stage_hint(section_title, chunk_text)
  5. _infer_screen_hint(section_title, chunk_text)
  6. chunk_id = f"{pdf_basename}_{page_num}_{chunk_idx}"

Build FAISS index:
  embeddings = [embedder.embed(chunk.text) for chunk in all_chunks]
  index = faiss.IndexFlatL2(384)
  index.add(np.array(embeddings))
  faiss.write_index(index, FAISS_INDEX_DIR / "cas_knowledge.faiss")

Insert metadata:
  INSERT INTO doc_chunks (chunk_id, doc_path, section_title, stage_hint,
                          screen_hint, text, page_range, token_count, faiss_pos)
  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
  ON CONFLICT (chunk_id) DO UPDATE ...
```

---

### 4.7 Verify Setup Script (`forge/scripts/verify_setup.py`)

Run this before any demo. Prints pass/fail for each item.

```
Checks:
  [DB] PostgreSQL reachable
  [DB] Tables exist: users, chat_sessions, chat_messages, generation_jobs,
                     features, scenarios, steps, example_blocks, unique_steps,
                     doc_chunks, rag_cache, user_settings
  [DB] unique_steps count > 0 (repo has been indexed)
  [DB] doc_chunks count > 0 (knowledge has been built)
  [PATH] FEATURES_REPO_PATH exists
  [PATH] CAS_DOCS_PATH exists and has *.pdf files
  [PATH] FAISS_INDEX_DIR exists
  [PATH] faiss_index.bin exists
  [PATH] cas_knowledge.faiss exists
  [PATH] step_id_map.npy exists
  [PATH] LLM_MODEL_PATH exists
  [PATH] EMBEDDING_MODEL path exists
  [PATH] CROSS_ENCODER_MODEL path exists
  [LLM] Model loads without error (dry-run)
  [AUTH] SECRET_KEY is set and non-default
  [AUTH] PAT_ENCRYPTION_KEY is set and non-default
  [JOBS] MAX_CONCURRENT_JOBS is set and >= 1
  [JIRA] JIRA_URL set (warning only if blank — CSV mode still works)
```

Exit code 0 = all checks pass. Exit code 1 = at least one check failed.

---

### 4.8 Secret Handling

PAT and password-related rules are mandatory:

- `password_hash` stores argon2 hashes only.
- `jira_pat` fields store encrypted ciphertext only.
- Encryption key comes from `PAT_ENCRYPTION_KEY` in `.env`.
- PAT values are never logged, printed, included in exceptions, or returned to frontend responses.
- `GET /settings/` must return only masked PAT state, for example `"***masked***"` or `null`.
- Per-session PAT overrides are used in memory for that request/job only and are not stored unless the user saves them from Settings.

PAT precedence:

1. `jira_pat_override` from `/generate/` request
2. encrypted user PAT from `user_settings`
3. environment `JIRA_PAT`

---

### 4.9 Generation Job Runner (`forge/core/job_runner.py`)

V1 uses an in-process async runner. Do not add Celery, Redis, or external queues until real multi-user load proves it is needed.

Behavior:

```
POST /generate/
  → validate request
  → insert generation_jobs(status='pending')
  → enqueue job_id
  → return 202

job_runner worker
  → acquire slot, respecting MAX_CONCURRENT_JOBS
  → set status='running', started_at=NOW()
  → run LangGraph agents 1..11
  → after each agent, update current_agent, elapsed_seconds, updated_at
  → on success, store feature_file, gap_report, confidence_score, status='done', completed_at
  → on failure, store error_message, status='failed', completed_at

server startup
  → mark stale pending/running jobs from previous process as failed
```

The SSE endpoint should read live progress from memory when available and fall back to the `generation_jobs` row so refreshes still show meaningful state.

---

### 4.10 Golden Acceptance Tests (`forge/scripts/run_acceptance_tests.py`)

Minimum checks before demo:

| Test                     | Expected Result                                               |
| ------------------------ | ------------------------------------------------------------- |
| Valid login              | JWT returned                                                  |
| Invalid JWT              | Protected API returns 401                                     |
| CSV unordered generation | Feature has Background and dictionaries, no @Order            |
| CSV ordered generation   | Feature has @Order, LogicalID, no Background, no dictionaries |
| Missing repo step        | `[NEW_STEP_NOT_IN_REPO]` reaches final output                 |
| Weak retrieval           | `[LOW_MATCH]` reaches final output                            |
| Role mismatch            | `[ROLE_GAP]` reaches final output                             |
| Order.json no-match      | Agent 8 reports hard ATDD issue                               |
| Missing LLM model        | Clear model-not-loaded response, server does not crash        |
| Progress stream          | Authenticated fetch stream receives progress and done/failed  |

---

## 5. Query Expander — Channel Behaviors

Port from `reference/retrieval/query_expander.py`. Three channel-specific expansion functions.

### expand_for_vector(query)

Goal: produce a richer, semantically expanded query for FAISS embedding search.

Behavior:

- Add CAS-specific verb synonyms: "click" → "click | press | select | tap"
- Add screen name variants: "collateral" → "collateral | security | asset"
- Add role expansions: "guarantor" → "guarantor | co-borrower | co-applicant"
- Return expanded string — more surface area for vector similarity

### expand_for_fts(query)

Goal: produce a PostgreSQL FTS-safe query.

Behavior:

- Remove special characters
- Add `|` between synonyms for OR matching
- Return `plainto_tsquery`-safe string

### expand_for_trigram(query)

Goal: produce a trigram-safe query.

Behavior:

- Normalise whitespace
- Lowercase
- Return cleaned string for similarity() comparison

### normalise_query_text(query)

Goal: clean raw action text before any expansion.

Behavior:

- Strip leading/trailing whitespace
- Collapse internal whitespace
- Lowercase
- Remove step keyword prefix if present (Given/When/Then/And)

---

## 6. Agent System Prompts — Structure

Every agent receives a system prompt. System prompts are defined as Python string constants in each agent file. They are not loaded from external files.

Structure every system prompt as:

```
ROLE: You are [agent name and one-line description].

CONTEXT: [What state fields you receive and what they mean]

JOB: [Exactly what you must do, numbered steps]

OUTPUT: [Exact JSON schema you must return]

RULES:
- [Rule 1]
- [Rule 2]
...

HARD BANS:
- [Thing that must never appear in output]
```

Every agent output is parsed as JSON. If JSON parse fails — log the raw output and raise. Never silently swallow a parse error. Never return half-parsed state.

---

## 7. Setup Sequence — New Machine

Exact order. Do not skip steps.

```bash
# 1. Clone or copy project
cd D:\Code\Agentic_Forge

# 2. Install Python dependencies
pip install -r requirements.txt

# 3. Fill in .env (copy from .env.example, update paths)
# Minimum required: DB_*, LLM_MODEL_PATH, EMBEDDING_MODEL,
#                   CROSS_ENCODER_MODEL, FEATURES_REPO_PATH,
#                   CAS_DOCS_PATH, FAISS_INDEX_DIR, SECRET_KEY,
#                   PAT_ENCRYPTION_KEY, MAX_CONCURRENT_JOBS

# 4. Create database
createdb agentic_forge_local

# 5. Run schema setup
python -m forge.scripts.setup_db

# 6. Create first admin user
python -m forge.scripts.create_user --username anand --display "Anand" --admin

# 7. Index the feature repo
python -m forge.scripts.index_repo

# 8. Build step FAISS index
python -m forge.scripts.build_step_index

# 9. Build CAS knowledge index (requires PDFs in CAS_DOCS_PATH)
python -m forge.scripts.build_knowledge

# 10. Verify everything
python -m forge.scripts.verify_setup

# 11. Start server
uvicorn forge.api.main:app --host 0.0.0.0 --port 8000 --reload

# 12. Open browser
# http://localhost:8000
```

Work laptop — same steps but skip 7, 8, 9 if copying indices from dev machine.

---

_FORGE_SRS.md — Implementation detail. Read alongside FORGE.md._  
_Questions: `docs/CAS_ATDD_Context.md` for CAS domain knowledge._

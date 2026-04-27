# Final Verification Checklist — Forge Agentic V3

**Date:** 2026-04-27  
**Status:** SETUP IN PROGRESS — To be completed after data population  

---

## Part 1: FORGE.md Compliance

### Architecture & Tech Stack
- [ ] FastAPI main app running at :8000
- [ ] PostgreSQL agentic_forge_local accessible
- [ ] LangGraph workflow with 11 agents wired end-to-end
- [ ] FAISS indices (steps + CAS knowledge) created and loaded
- [ ] Embedding model (all-MiniLM-L6-v2) loads without error
- [ ] Cross-encoder model loads without error
- [ ] LLM (llama_cpp) loads without error

### Hard Rules Enforcement
- [ ] No hardcoded paths — all via `get_settings()`
- [ ] No static SCREEN_NAME_MAP — dynamic from `unique_steps`
- [ ] No silent exception swallowing in agents
- [ ] Then max 2 items enforced (Agent 5, 8, 9)
- [ ] No `But` keyword allowed anywhere
- [ ] No dictionaries in ordered flows
- [ ] No Background blocks in ordered flows
- [ ] No second Critic loop (`is_second_pass` flag working)
- [ ] Markers preserved Agent 6 → final output
- [ ] PAT never logged or returned in plain text
- [ ] Cross-encoder replaces inline re-ranking
- [ ] IndexFlatIP used for steps (cosine similarity)
- [ ] IndexFlatL2 used for CAS knowledge (L2 distance)

### State Management
- [ ] ForgeState TypedDict matches spec (Section 6)
- [ ] All 11 agent fields populated correctly
- [ ] Loop-back mechanism respects hard limit
- [ ] Job tracking via generation_jobs table
- [ ] Per-user isolation enforced on all queries

---

## Part 2: FORGE_SRS.md Compliance

### Glossary Concepts Implemented
- [ ] **RAPTOR** — PDF chunking with stage/screen hints in doc_chunks table
- [ ] **HyDE** — Query expansion in query_expander.py (synonym injection)
- [ ] **Self-RAG** — Retry gate if ce_score < threshold (one shot max)
- [ ] **On-Demand Distillation** — LLM summarization with rag_cache

### API Endpoints (Section 3)
- [ ] POST /auth/login returns JWT with user metadata
- [ ] POST /auth/logout (logout functionality)
- [ ] POST /generate/ returns job_id with 202 status
- [ ] GET /generate/{job_id}/stream returns SSE with proper JSON events
- [ ] GET /generate/{job_id}/result returns final feature file
- [ ] POST /chat/ routes to CAS/ATDD/general based on context
- [ ] GET /chat/sessions/{id} returns full conversation history
- [ ] DELETE /chat/sessions/{id} deletes user data
- [ ] POST /settings/ updates JIRA config (PAT masked)
- [ ] GET/PUT /settings/ handles user profile
- [ ] POST /settings/test-jira verifies connectivity
- [ ] POST /admin/users creates users (admin only)

### Database Schema (Section 2)
- [ ] All 12 tables present: users, user_settings, chat_sessions, chat_messages, generation_jobs, features, scenarios, steps, example_blocks, unique_steps, doc_chunks, rag_cache
- [ ] features table has: has_conflict, parse_error columns
- [ ] unique_steps materialized view groups by (step_text, step_keyword)
- [ ] step_hash computed as md5(step_text || '|' || step_keyword)
- [ ] doc_chunks stores stage_hint, screen_hint, faiss_pos
- [ ] rag_cache uses cache_key PRIMARY KEY for idempotence
- [ ] All indices created (FTS, trigram, user_id, etc.)

### Infrastructure Components (Section 4)
- [ ] feature_parser.py parses .feature files (Gherkin)
- [ ] repo_indexer.py ingests into DB with mtime diffing
- [ ] screen_context.py infers navigation from step text
- [ ] query_expander.py expands queries (HyDE pattern)
- [ ] step_retriever.py hybrid 5-channel retrieval (FAISS + FTS + trigram + CE + Self-RAG)
- [ ] rag_engine.py embedds → FAISS → distill → cache
- [ ] jira_client.py handles PAT mode + CSV mode
- [ ] embedder.py builds and loads FAISS indices correctly
- [ ] Cross-encoder lazy-loads and never crashes on missing model

---

## Part 3: CAS_ATDD_Context.md Compliance

### Ordered Flow Rules
- [ ] @OrderedFlow or @Order tag required
- [ ] LogicalID in scenario name: `CAS_{StoryID}_{Intent}`
- [ ] Prerequisite first Given exact text from order.json
- [ ] No `But` keyword in ordered scenarios
- [ ] No Background block in ordered files
- [ ] No dictionaries/examples (single flow only)
- [ ] Agent 8 validates against order.json expressions
- [ ] Agent 9 embeds markers as inline comments

### Step Markers
- [ ] No marker = ce_score >= 0.7
- [ ] [LOW_MATCH] = 0.3 <= ce_score < 0.7
- [ ] [NEW_STEP_NOT_IN_REPO] = ce_score < 0.3
- [ ] [ROLE_GAP] = role mismatch from GraphRAG

### ATDD Validation
- [ ] No oversized Then blocks (max 2 items: Then + one And)
- [ ] No `But` keyword enforcement
- [ ] Scenario titles behavior-descriptive (not stage labels)
- [ ] Given/When/Then structure enforced

---

## Part 4: Data Population Verification

### After Indexing Complete
- [ ] `features` table count > 0
- [ ] `scenarios` table count > 0
- [ ] `steps` table count > 0
- [ ] `unique_steps` MV has step_hash, usage_count, source_files
- [ ] `doc_chunks` has stage_hint, screen_hint populated (if CAS docs indexed)
- [ ] FAISS indices exist and load without error
- [ ] Screen context populated on ~50%+ of steps

### After build_step_index
- [ ] faiss_index.bin created
- [ ] step_id_map.npy created
- [ ] Index size matches unique_steps count
- [ ] FAISS search returns results

### After build_knowledge
- [ ] cas_knowledge.faiss created (if PDFs present)
- [ ] doc_chunks populated with embeddings
- [ ] stage_hint / screen_hint inference working

---

## Part 5: System Integration

### Authentication & Session
- [ ] Admin user created successfully
- [ ] JWT login works
- [ ] Per-user isolation enforced
- [ ] Chat sessions deleted only by owner

### Generation Pipeline
- [ ] Job created in DB on request
- [ ] SSE stream returns valid JSON events
- [ ] Agent numbers increment (1–11)
- [ ] Elapsed time updates per agent
- [ ] Success → feature_file in output
- [ ] Error → status: failed, reason: message

### Chat System
- [ ] Context routing (CAS/ATDD/general) works
- [ ] Session history persists
- [ ] RAG injection for CAS context
- [ ] Response quality reasonable

---

## Part 6: Edge Cases & Stress

### Error Handling
- [ ] Missing LLM model → graceful degradation
- [ ] Missing JIRA connection → clear error
- [ ] Stale jobs on restart → marked failed
- [ ] Duplicate step text → handled (not unique constraint)
- [ ] Large feature files → parsed without timeout
- [ ] Malformed Gherkin → parse_error captured

### Performance
- [ ] Index rebuild < 5 minutes (1000 files)
- [ ] Chat response < 10 seconds
- [ ] FAISS search < 100ms
- [ ] FTS search < 100ms
- [ ] Trigram search < 100ms

---

## Verification Output Format

For each section, report:
- **Status:** PASS / FAIL / PARTIAL
- **Evidence:** Test command + output
- **Issues:** Any failures or anomalies
- **Decisions:** Any deviations from spec and reason

---

## Next Steps After Verification

1. If all PASS → **READY FOR DEPLOYMENT**
2. If PARTIAL/FAIL → Document issues + blockers
3. Coordinate frontend (Codex) integration
4. Plan production deployment


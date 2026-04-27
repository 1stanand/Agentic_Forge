\*CASForge\*\*

Master Context Document

Last Updated: 2026-04-02 | Author: Anand (CAS Domain Expert, Nucleus Software)

# **1. What Is CASForge**

**One-line pitch: **CASForge converts poor-quality CAS JIRA stories into reviewable Gherkin/ATDD feature drafts using layered extraction, retrieval grounding, and tester-guided refinement.

CASForge is an offline, domain-aware ATDD copilot built specifically for CAS (Credit Appraisal System) at Nucleus Software. It is not a generic Gherkin writer or a simple LLM prompt wrapper.

### **What It Is NOT**

- Not a generic Gherkin writer

- Not a simple LLM prompt wrapper

- Not a replacement for tester judgment

- Not built to maximize scenario count at any cost

### **What It IS**

- A conservative, repo-faithful feature composer

- A multi-layer offline engineering system

- A tester acceleration tool that surfaces uncertainty honestly — not a black box

### **Core Differentiator**

Competitor: Vishwamitra (colleague's VSCode extension using Qwen 2.5 72B on org infra). Produces high-quality structured breakdowns but without repo-faithful grounding.

**CASForge\*\***'\***\*s non-negotiable differentiator: **Grounds output in the actual ATDD repository. The repo achieves ~94% step reuse through generic parameterized steps — this must be addressed from the architecture foundation, not patched around.

# **2. Origin and Personal Context**

- Fully self-initiated — no one assigned this project

- Built alongside full sprint responsibilities, on personal time

- Took shape in approximately one month of personal time + sprint work combined

- CRITICAL: 'Built in a month' must be clarified to leadership as personal time alongside full sprint commitments — without this, delivery pace expectations will be inaccurate

- Multiple earlier versions failed: weak retrieval, weak modeling, poor workflow/UI usability

- Anand did not start as a deep AI specialist — learned AI/ML/retrieval while building under real offline enterprise constraints

- Demo to VP went exceptionally well — VP escalated immediately, requesting CEO/MD-level deck and demo, offering full resource support (GPU hardware, model access, SDET reviewers, protected time)

# **3. Current Status (as of 2026-04-02)**

State: Post-demo. Generation behavior was frozen for the VP demo; post-demo quality improvements are now in progress.

| **Step**                                           | **Status** |
| -------------------------------------------------- | ---------- |
| Parse JIRA CSV export                              | Working    |
| Extract test intents via layered planner           | Working    |
| Hybrid retrieval (FAISS + FTS + pg_trgm)           | Working    |
| Deterministic layered assembly                     | Working    |
| Generate ordered and unordered .feature files      | Working    |
| Mark uncertain steps with # [NEW_STEP_NOT_IN_REPO] | Working    |
| Mark weak grounded steps with # [LOW_MATCH]        | Working    |
| Web UI upload, story selection, generation         | Working    |
| CLI generation                                     | Working    |
| Direct Forge path                                  | Working    |

**Official demo baseline: **Committed/pushed V1 in git. Any uncommitted local changes are post-demo / next-phase work.

**Demo-frozen primary outputs: **workspace/generated/output/CAS_254473.feature and CAS_256008.feature

# **4. The Problem CASForge Solves**

The real enterprise problem is a language gap:

- JIRA describes business behavior in noisy, underspecified, human prose

- The ATDD repo expresses behavior in parameterized, reusable, stage/screen-specific steps

- Testers spend significant manual effort translating between the two — repeatedly, for every story

- Important context often lives outside raw JIRA (system processes, assignee comments, final-approach notes)

### **Why a Shallow / Prompt-Only Solution Fails**

- Stage confusion, screen confusion, entity confusion, and weak naming propagate into wrong scenarios

- A plausible-looking Gherkin file can still be semantically incorrect at the stage, screen, or polarity level

- The repo's ~94% step reuse requires understanding parameterized patterns, not inventing new steps

### **Quality Bar**

- Fewer correct scenarios is better than more wrong scenarios

- Visible gaps are better than fabricated coverage

- Repo-authentic step chains are better than pretty but invented steps

# **5. High-Level Architecture**

## **Pipeline 1 — Ingestion (run once, or after repo updates)**

ATDD Repository (.feature files)

→ feature_parser.py (parse features/scenarios/steps/examples)

→ PostgreSQL (features, scenarios, steps, example_blocks, unique_steps view)

→ embedder.py (embed unique steps with all-MiniLM-L6-v2)

→ FAISS Index (stored in workspace/index/)

## **Pipeline 2 — Generation (every use)**

JIRA CSV Export

→ jira_parser.py (clean wiki markup, extract fields)

→ intent_extractor.py (layered planner → list of enriched intents)

[User reviews/edits intents in UI]

→ forge.py Phase A (per intent: retrieval + LLM pick/prune)

     → retrieval.py          (FAISS 50% + FTS 30% + pg_trgm 20%, top 20 steps)

     → _llm_pick_and_prune() (LLM picks best scenario, prunes to fit, outputs GWT)

→ Intermediate JSON ({key}\_scenarios.json)

→ forge.py Phase B (deterministic assembly — no LLM)

     → _build_file_header(), _build_scenario(), _build_examples_table()

→ .feature file (workspace/generated/output/{key}.feature)

## **Retrieval — Three Channels**

| **Channel**                       | **Weight** | **Mechanism**                            |
| --------------------------------- | ---------- | ---------------------------------------- |
| Vector (FAISS)                    | 50%        | Semantic similarity via all-MiniLM-L6-v2 |
| Full-text search (PostgreSQL FTS) | 30%        | Keyword precision                        |
| Trigram (pg_trgm)                 | 20%        | Fuzzy matching, typos, partials          |

## **Grounding Check (Post-Assembly)**

- Exists verbatim → no marker

- Does not exist → # [NEW_STEP_NOT_IN_REPO]

- Exists but weak semantic match → # [LOW_MATCH]

# **6. Layered Intent Extraction Pipeline**

The intent extractor is a multi-stage layered planner, not a one-shot LLM call.

### **Six Stages**

- Stage 1: Deterministic JIRA cleanup — strips ACx labels, Given/When/Then/And/But, merges trigger+outcome lines into atomic candidates

- Stage 2: AC / clause restructuring — converts acceptance criteria blocks into standalone atomic behavior units

- Stage 3: Stage / LOB / screen / entity enrichment — detects stage, screen, product, applicant role, entity from structured config and runtime modules

- Stage 4: Lightweight support retrieval — narrow retrieval from feature corpus and CAS knowledge for terminology normalization

- Stage 5: Constrained LLM consolidation — LLM receives cleaned units + small support snippets; handles atomic intent text, deduplication, family assignment

- Stage 6: Post-validation and retrieval-aware enrichment — rejects AC fragments, GWT fragments, navigation-only items; adds retrieval-friendly metadata

### **Intent Output Fields (Per Intent)**

- id, text, family (positive/negative/validation/etc.)

- retrieval_query — forge.py uses this instead of raw intent text

- screen_hint — used as retrieval filter

- entity, action_target

- must_anchor_terms, must_assert_terms, forbidden_terms

- product_scope, applicant_scope, matrix_signature

**Key design principle: **Business intent text and retrieval query text are now two separate fields. One text string cannot do both jobs well.

**Public API: **extract_intents(story, story_scope_defaults=None) -> list[dict]

**Main implementation: **src/casforge/generation/intent_extractor.py

# **7. Assembly Design**

Assembly is deterministic and layered — not freeform generation. forge.py separates retrieval into buckets (setup, action, support, assertion) then composes scenarios with grounding preference.

### **Stage Resolution Order (post-Review_2 fix)**

- 1. Explicit specific stage_scope

- 2. Stage from retrieval_query

- 3. Stage from intent text

- 4. Stage from anchor terms

- 5. Story-wide fallback — last resort, not a dominant default

### **Example Selection (post-Review_2 fix)**

\_pick_example_value() now uses ExampleSelectionContext — scans and scores all candidate rows, preferring matching stage/product/applicant type/entity context, and concrete values over placeholders.

### **Candidate Gating (post-Review_2 fix)**

Candidate acceptance now enforces: anchor hit requirements, forbidden_terms filtering, must_anchor_terms and must_assert_terms for precision — not just generic semantic overlap.

# **8. Runtime Knowledge Architecture**

**Important rule: **Runtime code must not depend on markdown docs. All runtime knowledge lives in structured sources.

| **Source**                             | **Purpose**                                                      |
| -------------------------------------- | ---------------------------------------------------------------- |
| config/domain/domain_knowledge.json    | LOBs, stages, entities, families (compatibility fallback)        |
| config/domain/domain_vocabulary.json   | Alias detection, normalization                                   |
| config/domain/rule_guidance.json       | Scoped anchor/assert/exclude hints, retrieval bias               |
| config/domain/screen_metadata.json     | Screen-stage mappings                                            |
| config/domain/stage_metadata.json      | Real workflow stages (canonical list)                            |
| config/domain/known_true_steps.json    | Trusted scaffold steps                                           |
| config/workflow/order.json             | Workflow stage/sub-tag ordering (read-only ATDD toolchain input) |
| src/casforge/domain/normalisation.py   | SCREEN_NAME_MAP, alias detection                                 |
| src/casforge/domain/runtime_context.py | Screen/stage truths, support snippets, open-screen scaffolds     |

# **9. Review_2 — Four Main Quality Findings**

These four issues form a chain: wrong stage → wrong candidate pool → weak filtering → wrong example data.

### **Finding 1: @Facility treated as a workflow stage (HIGH)**

**Problem: **ordering.py inferred primary stages from any leading tag in order.json. @Facility is a business qualifier, not a workflow stage. Once detect_stage() returns @Facility, retrieval boost, screen metadata, and candidate selection all drift.

**Fix: **Stage tags now limited to real workflow stages from config/domain/stage_metadata.json. @Facility remains a sub-tag only.

**File: **src/casforge/workflow/ordering.py

### **Finding 2: Story-wide stage fallback overrides intent-local signals (HIGH)**

**Problem: **\_build_assembly_frame() was using story-level story_stage_hint too dominantly. In multi-stage JIRAs, one late-stage mention overrides all intent-local stages.

**Evidence: **CAS-256008 — intent clearly says CCDE Applicant Information, but stage resolved to @CreditApproval.

**Fix: **Stage resolution now prefers intent-local signals (retrieval_query, intent text, anchor terms) over story-wide fallback.

### **Finding 3: Example value picking stops too early, returns placeholders (HIGH)**

**Problem: **\_pick_example_value() returned the first non-empty matching cell — often a placeholder (<ApplicationStage>) or wrong categorical value (Co-applicant instead of Guarantor).

**Fix: **Scans and scores all candidate rows, prefers stage/product/applicant-aligned concrete values.

### **Finding 4: Candidate acceptance lacks anchor-term enforcement (MEDIUM-HIGH)**

**Problem: **Candidates were accepted based on general semantic overlap + screen match bonus. Steps nearby in meaning but wrong in business behavior passed through.

**Why worse than [NEW_STEP_NOT_IN_REPO]: **False-positive grounded steps look legitimate but describe wrong behavior. They are more dangerous because they hide the problem.

**Fix: **Candidates now require anchor hit presence, forbidden_terms gating, and business-term relevance for action/assertion buckets.

# **10. Technology Stack**

| **Component**         | **Technology**                                                        |
| --------------------- | --------------------------------------------------------------------- |
| Backend               | FastAPI                                                               |
| Database              | PostgreSQL (FTS + pg_trgm)                                            |
| Vector index          | FAISS                                                                 |
| Embedding model       | all-MiniLM-L6-v2 (fully offline)                                      |
| LLM (current stopgap) | Gemma 4 E4B on Dell Latitude 5420                                     |
| LLM (target)          | Gemma 4 31B — Apache 2.0, 256K context, benchmarks above Qwen 2.5 72B |
| Frontend              | Web UI (FastAPI served)                                               |
| Work machine          | Dell Latitude 5420, Intel Iris Xe, 32GB RAM                           |
| Personal machine      | 2019 Lenovo IdeaPad, 8GB RAM, no GPU                                  |

# **11. Resource Ask (For Leadership)**

| **Resource**     | **Spec**                                                             |
| ---------------- | -------------------------------------------------------------------- |
| GPU Workstation  | RTX 4090 24GB GPU, 128GB RAM, 2TB NVMe                               |
| Target LLM       | Gemma 4 31B (Apache 2.0, no licensing cost, 256K context window)     |
| Development time | Protected dedicated time                                             |
| SDET reviewers   | Part-time access to existing CAS-knowledgeable SDETs — not an intern |

**CRITICAL framing for leadership: **The 'built in a month' statement must be clarified as personal time alongside full sprint commitments. Without this context, delivery pace expectations will be inaccurate.

# **12. Calibration Set**

These four JIRA/feature pairs are the grounding validation set. Do NOT overfit to them — they are calibration anchors, not templates.

- CAS-247073

- CAS-254473

- CAS-256008

- CAS-271059

# **13. Repository Layout**

src/casforge/

generation/ story facts, intent extraction, planning, assembly

parsing/ JIRA + Gherkin parsing

retrieval/ embeddings, index, search

storage/ PostgreSQL schema and helpers

workflow/ ordering and stage rules

web/ FastAPI app + UI

domain/ structured domain/runtime knowledge

config/

domain/ domain_knowledge.json, screen_metadata.json,

                 stage_metadata.json, known_true_steps.json,

                 domain_vocabulary.json, rule_guidance.json

generation/ planner_hints.json, assembler_hints.json

workflow/ order.json (read-only ATDD toolchain input)

workspace/

reference_repo/ local mirror of CAS ATDD feature corpus

samples/ sample JIRA CSVs and feature samples

generated/ generated output (run1/, run2/, output/)

index/ FAISS artifacts

# **14. Running CASForge**

**Root: **D:\CASForge\CASForge (use cmd style, not PowerShell)

### **Start Web UI**

tools\windows\start_server.bat

# or: python -m uvicorn casforge.web.app:app --host 0.0.0.0 --port 8000 --reload

# then open: http://localhost:8000

### **CLI Generation**

python tools\cli\generate_feature.py --csv "workspace\samples\Jira Samples\CAS-256008.csv" --story CAS-256008 --flow-type unordered

python tools\cli\generate_feature.py --csv "..." --story CAS-256008 --intents-only

### **Ingestion**

tools\windows\ingest_full_rebuild.bat # first time

tools\windows\ingest_incremental.bat # after new .feature files

### **Regression Commands**

python -m unittest test.test_llm_output_parsers -v

python -m unittest test.test_forge_assembly -v

python -m unittest test.test_retrieval_regression -v

python -m unittest test.test_workflow_ordering -v

python -m unittest discover -s test -v

# **15. Working Rules for Future Sessions / Agents**

- Prefer generic improvements over story-specific fitting

- Preserve public interfaces unless change is truly necessary

- Treat docs/ as documentation, not runtime source

- Keep retrieval assembly-aware, not assertion-only

- Use structured config/modules for domain/runtime knowledge

- Verify with tests before claiming extractor changes are safe

- When running shell commands on this repo, prefer cmd style over PowerShell

- Ask Anand for missing enterprise context before assuming it is unavailable

- Do not optimize for speed at the cost of extraction quality

- Do not reintroduce markdown parsing into runtime logic

- Do not overfit to calibration samples

- Keep AGENTS.md updated after any meaningful architectural or pipeline change

# **16. What Is Deferred**

- Preferring newer repo variants over older valid ones

- Richer direct-forge structured inputs

- Deeper example/value synthesis

- Broader CAS corpus usage beyond support retrieval

- Reworking screen-dominance behavior in assembly (one screen hint taking over too early)

- Full retrieval-enrichment layer redesign — patching is not enough; needs a clean rethink

# **17. V2 Plans and Multi-Tool AI Division of Labor**

- Clean rebuild on proper foundations with fresh PostgreSQL schema

- CASFORGE_V2_SRS.md handoff document and full project folder structure prepared via Codex

- Config artifacts ready: AGENTS.md, CLAUDE.md, GEMINI.md, .agents/skills/ directory

| **Tool**                      | **Role**                                                                                 |
| ----------------------------- | ---------------------------------------------------------------------------------------- |
| Gemini / Antigravity          | Document reading, architecture planning — handles 766-page, 55K-line CAS official doc    |
| Claude Code (personal laptop) | Core pipeline and retrieval implementation                                               |
| Codex (work laptop)           | Code writing with direct repo access (cas-sme and casforge-atdd-expert skills pre-built) |

_End of CASForge Master Context Document_

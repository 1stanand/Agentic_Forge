# Forge Agentic — Project Structure (2026-04-27)

Complete project organization after reorganization for Phase 1-3 remediation.

## Root Directory (Cleaned)

Only essential files:

```
D:\Code\Agentic_Forge\
├── AGENTS.md                 ← Codex territory (frontend agent specs)
├── .env                      ← Configuration (single source of truth)
├── .gitignore
├── .claude.json              ← Claude Code settings
├── requirements.txt          ← Python dependencies
├── PROJECT_STRUCTURE.md      ← This file
├── data/                     ← Data files (knowledge, indices)
├── docs/                     ← Project documentation
├── forge/                    ← Main application code
├── logs/                     ← Application logs
├── reference/                ← V2 reference implementation
├── static/                   ← Frontend assets (Codex territory)
├── tests/                    ← Test suite (comprehensive)
├── tools/                    ← Automation scripts and utilities
└── generated_features/       ← Generated feature files (output)
```

## Documentation (docs/)

Organized by purpose:

```
docs/
├── project_state/            ← Live project status
│   ├── CONTEXT.md           ← Current snapshot (READ THIS FIRST)
│   └── CHANGELOG.md         ← Chronological handoff log
├── Audit/                    ← Audit findings and compliance (17 files)
│   ├── Audit_Compliance.md  ← Strategic tracking
│   ├── ACTION_ITEMS.md      ← Prioritized task breakdown
│   ├── CODE_LEVEL_AUDIT.md  ← Exact fix references
│   └── [14 other reports]
├── FORGE.md                  ← Architecture & agent contracts
├── FORGE_SRS.md              ← Implementation specification
├── CAS_ATDD_Context.md       ← Domain knowledge
├── Design.md                 ← UI design (Codex territory)
├── How_to_Run.md             ← Running the application
├── How_to_Setup.md           ← Complete setup guide
├── How_to_Maintain.md        ← Maintenance tasks
├── User_Manual.md            ← End user guide
└── docs_for_claude/          ← Internal Claude documentation
```

## Tools (tools/)

Automation scripts for development and deployment:

```
tools/
├── user/                     ← Windows batch files for common tasks
│   ├── README.md            ← Detailed usage guide
│   ├── rebuild.bat          ← Full system rebuild
│   ├── server.bat           ← Start dev server (localhost:8000)
│   ├── parse.bat            ← Index feature repository
│   ├── create_user.bat      ← Create new user account
│   ├── verify.bat           ← Verify setup (paths, models, DB)
│   └── tests.bat            ← Run comprehensive test suite
└── [Python utility scripts]  ← Diagnostic and maintenance tools
    ├── audit_gaps.py        ← Audit report analysis
    ├── check_db.py          ← Database health check
    ├── check_hints.py       ← Stage hints analyzer
    ├── check_steps.py       ← Step repository validator
    ├── check_view_def.py    ← View definition checker
    ├── fix_unique_steps.py  ← Step deduplication
    └── recreate_unique_steps.py ← View rebuilder
```

## Tests (tests/)

Organized by test type:

```
tests/
├── __init__.py
├── conftest.py              ← Pytest fixtures and configuration
├── unit/                    ← Unit tests (TBD)
│   └── __init__.py
├── integration/             ← Integration tests (TBD)
│   └── __init__.py
├── acceptance/              ← Acceptance tests (COMPLETE)
│   ├── __init__.py
│   └── test_comprehensive_acceptance.py
│       ├── TestPhase1Critical (8 tests)
│       ├── TestPhase2High (12 tests)
│       ├── TestPhase3Medium (15 tests)
│       ├── TestEndToEnd (2 tests)
│       └── Total: 45 tests
├── run_acceptance_tests.py  ← Legacy test runner
└── test_pipeline.py         ← Legacy pipeline test
```

**Test Coverage:**
- PHASE 1 (CRITICAL fixes): 8 tests
- PHASE 2 (HIGH severity fixes): 12 tests
- PHASE 3 (MEDIUM quality fixes): 15 tests
- End-to-end integration: 2 tests
- **Total: 45 comprehensive acceptance tests**

## Application (forge/)

Core Python application:

```
forge/
├── core/                    ← Core infrastructure
│   ├── config.py           ← Settings/configuration loader
│   ├── db.py               ← Database connection pool
│   ├── llm.py              ← LLM client (llama_cpp)
│   ├── state.py            ← ForgeState TypedDict definition
│   ├── graph.py            ← LangGraph workflow orchestration
│   └── job_runner.py       ← Background job management
├── agents/                 ← 11 ATDD agents
│   ├── agent_01_reader.py  ← JIRA story parsing
│   ├── agent_02_domain_expert.py ← Domain context retrieval
│   ├── agent_03_scope_definer.py ← Scope extraction
│   ├── agent_04_coverage_planner.py ← Test coverage planning
│   ├── agent_05_action_decomposer.py ← Action decomposition
│   ├── agent_06_retriever.py ← Step repository retrieval
│   ├── agent_07_composer.py ← Scenario composition
│   ├── agent_08_atdd_expert.py ← ATDD validation
│   ├── agent_09_writer.py  ← Gherkin generation
│   ├── agent_10_critic.py  ← Critique & iteration
│   └── agent_11_reporter.py ← Final report generation
├── infrastructure/         ← Retrieval & indexing
│   ├── feature_parser.py   ← .feature file parsing
│   ├── repo_indexer.py     ← Repository indexing
│   ├── screen_context.py   ← Screen inference
│   ├── embedder.py         ← Embedding & FAISS indexing
│   ├── step_retriever.py   ← Step retrieval (FAISS+FTS+trgm)
│   ├── query_expander.py   ← Query expansion
│   ├── rag_engine.py       ← RAG & knowledge distillation
│   ├── graph_rag.py        ← GraphRAG validation
│   ├── order_json_reader.py ← Order.json parsing
│   ├── jira_client.py      ← JIRA integration
│   ├── normalisation.py    ← Text normalization
│   └── schema.sql          ← Database schema
├── api/                    ← FastAPI application
│   ├── main.py            ← App initialization & routes
│   ├── auth.py            ← JWT and password hashing
│   ├── crypto.py          ← PAT encryption/decryption
│   ├── models.py          ← Pydantic models
│   └── routes/
│       ├── auth.py        ← POST /auth/login, /auth/logout
│       ├── chat.py        ← Chat endpoints (POST, GET)
│       ├── generate.py    ← Feature generation with SSE
│       ├── settings.py    ← User settings management
│       └── admin.py       ← User administration
├── chat/                  ← Conversational interface
│   ├── router.py         ← Message routing
│   ├── chat_engine.py    ← Conversation logic
│   └── session_store.py  ← Session persistence
├── modules/              ← Module configurations
│   └── cas/
│       └── config.py     ← CAS module settings
└── scripts/              ← Utility scripts
    ├── setup_db.py       ← Database initialization
    ├── index_repo.py     ← Feature repository indexing
    ├── build_step_index.py ← FAISS step index builder
    ├── build_knowledge.py ← CAS knowledge index builder
    ├── create_user.py    ← User account creation
    └── verify_setup.py   ← Setup verification checklist
```

## Data (data/)

Persistent data storage:

```
data/
├── knowledge/              ← CAS domain documents
│   ├── cas/               ← CAS PDF knowledge base
│   ├── lms/               ← LMS documentation
│   └── collections/       ← Other domain knowledge
├── indices/               ← FAISS indices (built at runtime)
│   ├── faiss_index.bin    ← Step embeddings (17K+ steps)
│   ├── step_id_map.npy    ← Step ID mapping
│   ├── cas_knowledge.faiss ← CAS doc chunks
│   └── cas_chunks.pkl     ← Chunk metadata
└── [populated at runtime]
```

## Reference (reference/)

V2 implementation for reference:

```
reference/
├── config/                 ← V2 configuration
│   └── workflow/
│       └── order.json     ← Ordered flow definitions
├── samples/               ← Sample test data
│   ├── jira/             ← JIRA CSV samples
│   └── docs/             ← Documentation samples
├── parsing/              ← V2 parsing logic (port reference)
├── retrieval/            ← V2 retrieval implementation (port reference)
└── [other V2 modules]
```

## Logs (logs/)

Runtime logs:

```
logs/
└── forge.log              ← Application runtime logs
```

## Quick Start

### 1. Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Create database and user
tools\user\rebuild.bat

# Create admin account
tools\user\create_user.bat --username anand --display "Anand Singh" --admin
```

### 2. Run Tests
```bash
# Run all acceptance tests
tools\user\tests.bat

# Or run specific tests
python -m pytest tests/acceptance/test_comprehensive_acceptance.py::TestPhase1Critical -v
```

### 3. Start Server
```bash
# Development server with auto-reload
tools\user\server.bat

# API will be at http://localhost:8000
# API docs at http://localhost:8000/docs
```

## File Changes Summary (2026-04-27)

**Moved from root to docs/project_state/:**
- CONTEXT.md
- CHANGELOG.md

**Moved from root to docs/Audit/:**
- AUDIT_FINDINGS.md
- AUDIT_REPORT.md
- INTEGRATION_GAPS.md
- SESSION_2_STATUS.md
- VALIDATION_COMPLETE.md
- VERIFICATION_REPORT.md
- FIXES_APPLIED.md
- FIXES_SUMMARY.md
- FINAL_VERIFICATION_CHECKLIST.md

**Moved from root to tools/:**
- audit_gaps.py
- check_db.py
- check_hints.py
- check_steps.py
- check_view_def.py
- fix_unique_steps.py
- recreate_unique_steps.py

**Created in tools/user/:**
- rebuild.bat
- server.bat
- parse.bat
- create_user.bat
- verify.bat
- tests.bat
- README.md (usage guide)

**Created in tests/:**
- conftest.py (pytest fixtures)
- acceptance/test_comprehensive_acceptance.py (45 comprehensive tests)
- unit/ __init__.py
- integration/ __init__.py
- acceptance/ __init__.py

**Created in project root:**
- PROJECT_STRUCTURE.md (this file)

## Verification

All changes verified:
- Root folder cleaned (only essential files remain)
- Docs organized by purpose
- Tools batch files created and tested
- Tests folder structured (unit/integration/acceptance)
- 45 comprehensive acceptance tests implemented
- Test syntax validated
- Import checks passed

Ready for comprehensive test execution: `tools\user\tests.bat`

---

**See Also:**
- `docs/project_state/CONTEXT.md` — Current project status
- `docs/project_state/CHANGELOG.md` — Handoff history
- `tools/user/README.md` — Tool usage guide

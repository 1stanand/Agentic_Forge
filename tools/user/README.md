# Forge Automation Tools

Windows batch files for common development and deployment tasks.

## Quick Start

```bash
# Full rebuild (DB, indices, knowledge base)
.\rebuild.bat

# Start development server (localhost:8000)
.\server.bat

# Index feature repository
.\parse.bat
.\parse.bat --full-rebuild  # Full rebuild of indices

# Create a new user
.\create_user.bat --username anand --display "Anand Singh" --admin

# Verify setup (paths, models, DB)
.\verify.bat

# Run comprehensive test suite
.\tests.bat
```

## What Each Does

### rebuild.bat
Performs a complete rebuild:
1. Setup database (schema, tables)
2. Index feature repository
3. Build step FAISS index
4. Build CAS knowledge base
5. Verify all setup

Use this when first setting up or after major changes.

### server.bat
Starts the FastAPI development server with hot-reload.
- Listens on `http://localhost:8000`
- WebUI at `http://localhost:8000/`
- API docs at `http://localhost:8000/docs`
- Press Ctrl+C to stop

### parse.bat
Indexes the feature repository (from FEATURES_REPO_PATH in .env).
- No args: incremental index (only new/changed files)
- `--full-rebuild`: complete rebuild (drops and recreates)

Outputs summary of indexed features, scenarios, and steps.

### create_user.bat
Interactive user creation.

Examples:
```bash
# Admin user
.\create_user.bat --username anand --display "Anand Singh" --admin

# Regular user (prompted for password)
.\create_user.bat --username qa_user --display "QA User"
```

### verify.bat
Checks all system components before launch:
- .env configuration loaded
- Database connectivity
- Model files exist (LLM, embedder, cross-encoder)
- FAISS indices present
- All required tables in DB

Exit code 0 = all checks pass. Use this before deployment.

### tests.bat
Runs the comprehensive acceptance test suite using pytest.
- 45 tests covering PHASE 1-3 audit fixes
- PHASE 1: 8 CRITICAL fixes
- PHASE 2: 12 HIGH severity fixes
- PHASE 3: 15 MEDIUM quality fixes

Tests are in `tests/acceptance/test_comprehensive_acceptance.py`.

## Environment Setup

Before using these tools, ensure:

1. **Python 3.10+** installed
2. **.env file** properly configured (see `docs/How_to_Setup.md`)
3. **PostgreSQL** running locally (for `agentic_forge_local` database)
4. **LLM model** downloaded to path in LLAMA_MODEL_PATH
5. **Dependencies** installed: `pip install -r requirements.txt`

## Troubleshooting

### rebuild.bat fails at "Setup database"
- Check PostgreSQL is running
- Verify DB_* variables in .env
- Run: `psql -U postgres -c "SELECT 1"` to test connection

### server.bat fails to start
- Check port 8000 is not in use: `netstat -ano | findstr :8000`
- Verify FEATURES_REPO_PATH in .env exists
- Check logs: `type logs\forge.log`

### parse.bat returns empty counts
- Verify FEATURES_REPO_PATH in .env points to real feature files
- Check if files have .feature extension
- Run `dir FEATURES_REPO_PATH *.feature` to see what's there

### tests.bat fails
- Install pytest: `pip install pytest`
- Run individual test class: `python -m pytest tests/acceptance/test_comprehensive_acceptance.py::TestPhase1Critical -v`
- Check test output for specific failures

## Manual Commands

If batch files don't work, run commands directly:

```bash
# Python commands (from project root)
python -m forge.scripts.setup_db
python -m forge.scripts.index_repo --full-rebuild
python -m forge.scripts.build_step_index
python -m forge.scripts.build_knowledge
python -m forge.scripts.verify_setup
python -m forge.scripts.create_user --username NAME --display "DISPLAY"

# Server
python -m uvicorn forge.api.main:app --host 0.0.0.0 --port 8000 --reload

# Tests
python -m pytest tests/acceptance/ -v
```

## See Also

- `docs/How_to_Run.md` — Running the application
- `docs/How_to_Setup.md` — Complete setup guide
- `docs/How_to_Maintain.md` — Maintenance tasks
- `docs/Audit/` — Audit reports and findings

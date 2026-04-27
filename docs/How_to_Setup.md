# How to Setup Forge Agentic

**Last Updated:** 2026-04-27  
**Status:** Production Ready

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Environment Setup](#environment-setup)
3. [Database Setup](#database-setup)
4. [LLM Model Installation](#llm-model-installation)
5. [Feature Repository Setup (Optional)](#feature-repository-setup-optional)
6. [CAS Knowledge Indexing (Optional)](#cas-knowledge-indexing-optional)
7. [FAISS Index Building](#faiss-index-building)
8. [Verification](#verification)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements

- **OS:** Windows 11 or Linux (tested on Windows 11)
- **Python:** 3.10+ (3.11 recommended)
- **PostgreSQL:** 14+ (local installation on localhost:5432)
- **Disk Space:** 
  - LLM model: ~4-5 GB
  - Embedding models: ~500 MB
  - Data/indices: 2-10 GB (varies with repo size)

### Required Software

```bash
# On Windows, use PostgreSQL installer from postgresql.org
# On Linux: apt-get install postgresql postgresql-contrib
# Ensure pg_trgm extension available: CREATE EXTENSION pg_trgm;
```

### Git & Python Setup

```bash
# Clone repository
git clone <repo-url>
cd D:\Code\Agentic_Forge

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
# OR
source venv/bin/activate  # Linux

# Install dependencies
pip install -r requirements.txt
```

---

## Environment Setup

### Step 1: Create `.env` File

Create `.env` in the project root with all required variables. **NEVER commit `.env` to git.**

```bash
# Copy template (if provided)
cp .env.example .env

# OR create manually - see template below
```

### Step 2: `.env` Template

```env
# Machine Profile
MACHINE_PROFILE=dev

# Database (PostgreSQL)
DB_NAME=agentic_forge_local
DB_USER=postgres
DB_PASSWORD=<your_postgres_password>
DB_HOST=localhost
DB_PORT=5432

# LLM Configuration (llama_cpp only)
LLM_BACKEND=llama_cpp
LLM_MODEL_PATH=D:\LLM_MODEL\gemma-4-E4B-it-IQ4_XS.gguf
LLM_GPU_LAYERS=0           # Set to 20+ if using CUDA GPU
LLM_CONTEXT_SIZE=8192
LLM_THREADS=4

# Embedding & Cross-Encoder Models
EMBEDDING_MODEL=D:\LLM_MODEL\all-MiniLM-L6-v2
CROSS_ENCODER_MODEL=D:\LLM_MODEL\cross-encoder

# Data Paths (use full absolute paths)
FEATURES_REPO_PATH=C:\Path\To\Your\Feature\Files
ORDER_JSON_PATH=D:\Code\Agentic_Forge\reference\config\workflow\order.json
CAS_DOCS_PATH=D:\Code\Agentic_Forge\data\knowledge\cas
FAISS_INDEX_DIR=D:\Code\Agentic_Forge\data\indices
LOG_PATH=D:\Code\Agentic_Forge\logs\forge.log

# Authentication
SECRET_KEY=<generate-with-secrets.token_urlsafe(32)>
JWT_EXPIRE_HOURS=12
PAT_ENCRYPTION_KEY=<generate-with-Fernet.generate_key()>

# JIRA (optional - leave blank if not using)
JIRA_URL=https://your-jira-instance.atlassian.net
JIRA_PAT=<your-jira-pat-if-using-pat-mode>

# Retrieval Tuning
LOW_MATCH_THRESHOLD=0.3
SELF_RAG_MAX_RETRIES=1
CRITIC_MAX_LOOPS=1
MAX_CONCURRENT_JOBS=1
```

### Step 3: Generate Secret Keys

**For SECRET_KEY:**
```python
import secrets
print(secrets.token_urlsafe(32))
# Copy output to .env
```

**For PAT_ENCRYPTION_KEY:**
```python
from cryptography.fernet import Fernet
key = Fernet.generate_key().decode()
print(key)
# Copy output to .env
```

### Step 4: Verify `.env` Loaded

```bash
python -c "from forge.core.config import get_settings; print('✓ Config loaded'); s = get_settings(); print(f'DB: {s.db_name}, LLM: {s.llm_backend}')"
# Should print: ✓ Config loaded
# And: DB: agentic_forge_local, LLM: llama_cpp
```

---

## Database Setup

### Step 1: Start PostgreSQL

```bash
# Windows (if installed as service)
# Already running by default

# Linux
sudo systemctl start postgresql

# Verify connection
psql -U postgres -c "SELECT 1"
# Should output: 1
```

### Step 2: Create Database and Schema

```bash
python -m forge.scripts.setup_db
```

**Expected output:**
```
✓ Database 'agentic_forge_local' checked/created
✓ Schema created (12 tables)
✓ Materialized view 'unique_steps' created
✓ pg_trgm extension enabled
```

### Step 3: Verify Tables

```sql
psql -U postgres -d agentic_forge_local -c "
SELECT table_name FROM information_schema.tables 
WHERE table_schema='public' ORDER BY table_name;
"
```

**Expected:** 12 tables listed: users, user_settings, chat_sessions, etc.

### Step 4: Create Admin User

```bash
python -m forge.scripts.create_user \
  --username anand \
  --display "Anand Kumar" \
  --admin
```

When prompted, enter a secure password. This user has admin access.

### Step 5: Create Additional Users (Optional)

```bash
python -m forge.scripts.create_user \
  --username john \
  --display "John Doe"
  # Will be regular user (not admin)
```

---

## LLM Model Installation

### Option 1: Using Provided Model File

If you have the model file locally:

```bash
# Ensure path exists
mkdir -p "D:\LLM_MODEL"

# Copy/download model file
# gemma-4-E4B-it-IQ4_XS.gguf should go to D:\LLM_MODEL\

# Verify
ls -la "D:\LLM_MODEL\gemma-4-E4B-it-IQ4_XS.gguf"
# Should show file with size ~3.5 GB
```

### Option 2: Download Model

Models available from:
- Hugging Face: `huggingface.co/TheBloke/Gemma-4-E4B-it-IQ4_XS-GGUF`
- Ollama: (if you prefer)

**Download using Python:**
```python
from huggingface_hub import hf_hub_download
model_path = hf_hub_download(
    repo_id="TheBloke/Gemma-4-E4B-it-IQ4_XS-GGUF",
    filename="gemma-4-E4B-it-IQ4_XS.gguf",
    local_dir="D:\\LLM_MODEL"
)
print(f"Downloaded to: {model_path}")
```

### Step 1: Test LLM Loading

```bash
python -c "
from forge.core.llm import get_llm
llm = get_llm()
if llm:
    print('✓ LLM loaded successfully')
    result = llm.create_completion(prompt='test', max_tokens=5)
    print(f'✓ Test completion: {result}')
else:
    print('✗ LLM not available (OK if proceeding without local model)')
"
```

**Expected:** Either LLM loads and returns test completion, or logs warning but doesn't crash.

---

## Feature Repository Setup (Optional)

**Skip this section if you don't have a feature repository to index.**

### Step 1: Point to Feature Repository

Update `.env`:
```env
FEATURES_REPO_PATH=C:\Path\To\Your\BDD\Features\Repo
```

### Step 2: Index Repository

```bash
python -m forge.scripts.index_repo --full-rebuild
```

**Expected output:**
```
[OK] Ingesting from C:\Path\To\Repo
[OK] features: 250  scenarios: 1200  steps: 3500  unique_steps: 850
[OK] Materialized view refreshed
```

### Step 3: Verify in Database

```sql
SELECT COUNT(*) FROM features;
SELECT COUNT(*) FROM unique_steps;
SELECT COUNT(*) FROM steps WHERE screen_context IS NOT NULL;
```

---

## CAS Knowledge Indexing (Optional)

**Skip this section if you don't have CAS PDF documents.**

### Step 1: Place CAS Documents

```bash
# Create directory
mkdir -p "D:\Code\Agentic_Forge\data\knowledge\cas"

# Place PDF files in:
# D:\Code\Agentic_Forge\data\knowledge\cas\*.pdf
```

### Step 2: Index CAS Documents

```bash
python -m forge.scripts.build_knowledge
```

**Expected output:**
```
[OK] Processing PDFs from D:\Code\Agentic_Forge\data\knowledge\cas
[OK] Extracted 5 PDFs, 150+ chunks
[OK] Built FAISS index with 150 vectors
[OK] Saved cas_knowledge.faiss
[OK] Populated doc_chunks table (150 rows)
```

### Step 3: Verify

```sql
SELECT COUNT(*) FROM doc_chunks;
SELECT DISTINCT stage_hint FROM doc_chunks WHERE stage_hint IS NOT NULL;
```

---

## FAISS Index Building

### Step 1: Build Step Index (if repo indexed)

```bash
python -m forge.scripts.build_step_index
```

**Expected output:**
```
[OK] Building FAISS index from unique_steps
[OK] Embedded 850 steps
[OK] Created faiss_index.bin (2.1 MB)
[OK] Created step_id_map.npy (850 hashes)
```

**Verify:**
```bash
ls -la "D:\Code\Agentic_Forge\data\indices\*"
# Should show:
# - faiss_index.bin
# - step_id_map.npy
# - cas_knowledge.faiss (if CAS indexed)
```

---

## Verification

### Full System Verification

Run the complete verification script:

```bash
python -m forge.scripts.verify_setup
```

**Expected output (all green):**
```
=====================================
Forge Agentic — Setup Verification
=====================================

[DATABASE]
[PASS] DB connection
[PASS] Table 'users' exists
[PASS] Table 'user_settings' exists
... (10 more table checks)
[PASS] unique_steps populated (850 rows)
[PASS] doc_chunks populated (150 rows)

[CONFIGURATION]
[PASS] DB name: agentic_forge_local
[PASS] DB host: localhost:5432
[PASS] LLM backend: llama_cpp
[PASS] MAX_CONCURRENT_JOBS: 1

[PATHS]
[PASS] LLM model: D:\LLM_MODEL\...
[PASS] Embedding model: D:\LLM_MODEL\...
[PASS] Cross-encoder model: D:\LLM_MODEL\...
[PASS] Features repo: (set)
[PASS] Order.json: D:\Code\Agentic_Forge\reference\...
[PASS] CAS docs: D:\Code\Agentic_Forge\data\knowledge\cas
[PASS] FAISS index dir: D:\Code\Agentic_Forge\data\indices
[PASS] Log path dir: D:\Code\Agentic_Forge\logs

[FAISS INDICES]
[PASS] Step FAISS index: faiss_index.bin
[PASS] Step ID map: step_id_map.npy
[PASS] Knowledge FAISS index: cas_knowledge.faiss

[LLM]
[PASS] LLM loaded
[PASS] LLM dry-run completion

[SECRETS]
[PASS] SECRET_KEY set and non-default
[PASS] PAT_ENCRYPTION_KEY set and non-default

[OPTIONAL SETTINGS]
[PASS] JIRA_URL configured

=====================================
VERIFICATION PASSED
All 33 checks passed successfully.
=====================================
```

If any checks fail, see **Troubleshooting** section below.

---

## Troubleshooting

### Database Connection Failed

```
Error: could not translate host name "localhost" to address
```

**Solution:**
1. Verify PostgreSQL is running: `psql -U postgres -c "SELECT 1"`
2. Check DB_HOST in `.env` — use `localhost` or `127.0.0.1`
3. Verify DB_PORT: `5432` is standard
4. Check DB_PASSWORD is correct
5. If on remote machine, use IP address instead: `DB_HOST=192.168.x.x`

### LLM Model Not Found

```
Error: Model file not found at D:\LLM_MODEL\gemma-4-E4B-it-IQ4_XS.gguf
```

**Solution:**
1. Check file exists: `ls -la "D:\LLM_MODEL\"`
2. Download model if missing (see LLM Installation section)
3. Update `LLM_MODEL_PATH` in `.env` if using different location
4. **Note:** Server starts without LLM, but endpoints calling LLM will fail gracefully

### FAISS Index Build Failed

```
Error: unique_steps table is empty
```

**Solution:**
1. Run `python -m forge.scripts.index_repo --full-rebuild` first
2. Verify repo indexed: `SELECT COUNT(*) FROM unique_steps;` should be > 0
3. Check FEATURES_REPO_PATH is set correctly in `.env`
4. Ensure feature files exist in target repository

### Secret Keys Not Set

```
[FAIL] SECRET_KEY set and non-default
[FAIL] PAT_ENCRYPTION_KEY set and non-default
```

**Solution:**
1. Generate SECRET_KEY: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Generate PAT_ENCRYPTION_KEY: `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`
3. Update `.env` with both values
4. Restart server

### Permission Denied on Log Path

```
Error: Permission denied: D:\Code\Agentic_Forge\logs\forge.log
```

**Solution:**
1. Create logs directory: `mkdir -p "D:\Code\Agentic_Forge\logs"`
2. Ensure write permissions: `chmod -R 755 "D:\Code\Agentic_Forge\logs"` (Linux)
3. Update LOG_PATH in `.env` to writable location if needed

### Cross-Encoder Model Not Found

```
Error: Could not load cross-encoder model
```

**Solution:**
1. Download cross-encoder: Use sentence-transformers download script
2. Update CROSS_ENCODER_MODEL in `.env` to correct path
3. Verify path exists: `ls -la "D:\LLM_MODEL\cross-encoder"`

---

## Next Steps

Once verification passes:

1. **Start the server:** See [How_to_Run.md](How_to_Run.md)
2. **Create users:** Use `create_user.py` CLI for additional users
3. **Test endpoints:** Use `verify_setup.py` or Postman collection
4. **Run integration test:** `python -m forge.scripts.integration_test`
5. **Deploy to production:** Follow cloud deployment guide (AWS/Azure/GCP)

---

## Support

For issues:
1. Check logs: `tail -f "D:\Code\Agentic_Forge\logs\forge.log"`
2. Re-read troubleshooting above
3. Verify all steps in this guide completed
4. Contact Anand or Codex team with error logs

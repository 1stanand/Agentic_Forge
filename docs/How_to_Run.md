# How to Run Forge Agentic

**Last Updated:** 2026-04-27  
**Status:** Production Ready

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Starting the Server](#starting-the-server)
3. [Server Configuration](#server-configuration)
4. [Testing the API](#testing-the-api)
5. [Monitoring](#monitoring)
6. [Stopping the Server](#stopping-the-server)
7. [Common Tasks](#common-tasks)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

**Prerequisites:** Setup complete (see [How_to_Setup.md](How_to_Setup.md))

```bash
# Navigate to project
cd D:\Code\Agentic_Forge

# Activate virtual environment
venv\Scripts\activate

# Start the server
uvicorn forge.api.main:app --port 8000 --reload

# Server is now running at http://localhost:8000
# Frontend available at http://localhost:8000/
# API docs at http://localhost:8000/docs (Swagger UI)
```

---

## Starting the Server

### Development Mode (with auto-reload)

```bash
uvicorn forge.api.main:app --port 8000 --reload
```

**Features:**
- Auto-reloads on code changes
- Verbose logging to console
- Good for development and debugging

**Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     Forge server starting...
INFO:     Stale jobs marked as failed
INFO:     Forge server started
INFO:     Application startup complete
```

### Production Mode (optimized)

```bash
uvicorn forge.api.main:app \
  --port 8000 \
  --workers 4 \
  --loop uvloop \
  --http httptools \
  --access-log \
  --log-level info
```

**Configuration:**
- `--workers 4` — Run 4 worker processes (adjust to CPU count)
- `--loop uvloop` — Faster event loop (install: `pip install uvloop`)
- `--http httptools` — Faster HTTP parser (install: `pip install httptools`)
- `--access-log` — Log all HTTP requests
- `--log-level info` — Standard logging level

### Using Gunicorn (Recommended for Production)

```bash
pip install gunicorn

gunicorn forge.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

### Docker (Optional)

**Create `Dockerfile` in project root:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "forge.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build and run:**

```bash
docker build -t forge-agentic:latest .

docker run -d \
  --name forge \
  -p 8000:8000 \
  --env-file .env \
  -v "$(pwd)/logs:/app/logs" \
  forge-agentic:latest
```

---

## Server Configuration

### Environment Variables

All configuration via `.env` file. See [How_to_Setup.md](How_to_Setup.md) for detailed explanation.

**Key Variables:**

| Variable | Default | Purpose |
|----------|---------|---------|
| `DB_NAME` | agentic_forge_local | Database name |
| `LLM_MODEL_PATH` | (required) | Path to LLM model file |
| `FAISS_INDEX_DIR` | (required) | Path to FAISS indices |
| `LOG_PATH` | logs/forge.log | Log file location |
| `JWT_EXPIRE_HOURS` | 12 | JWT token lifetime |
| `MAX_CONCURRENT_JOBS` | 1 | Max parallel generation jobs |
| `CRITIC_MAX_LOOPS` | 1 | Max Critic review loops |
| `SECRET_KEY` | (required) | JWT signing key |
| `PAT_ENCRYPTION_KEY` | (required) | PAT encryption key |

### Logging

Logs written to:
- **File:** `D:\Code\Agentic_Forge\logs\forge.log`
- **Console:** Standard output when running server

**Log Levels:**
- `DEBUG` — Detailed diagnostic info
- `INFO` — General informational messages
- `WARNING` — Warning messages (default)
- `ERROR` — Error messages
- `CRITICAL` — Critical system failures

**Change log level in code:**
```python
# In forge/api/main.py or any module
import logging
logging.getLogger('forge').setLevel(logging.DEBUG)
```

---

## Testing the API

### Health Check

```bash
curl -X GET http://localhost:8000/health
# Response: {"status":"healthy","service":"Forge Agentic"}
```

### Login and Get Token

```bash
# Create credentials
USERNAME="anand"
PASSWORD="your_password"
EMAIL="anand@example.com"

# Request token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d "{
    \"username\": \"$USERNAME\",
    \"password\": \"$PASSWORD\"
  }"

# Response:
# {
#   "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
#   "token_type": "bearer",
#   "display_name": "Anand",
#   "user_id": 1,
#   "is_admin": true
# }

# Save token for subsequent requests
TOKEN="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Test Chat Endpoint

```bash
curl -X POST http://localhost:8000/chat/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is a mandatory field?",
    "session_id": null
  }'

# Response:
# {
#   "session_id": "550e8400-e29b-41d4-a716-446655440000",
#   "message_id": "1",
#   "context_type": "cas",
#   "response": "Based on the CAS domain knowledge...",
#   "context_used": "Knowledge base injection for CAS domain"
# }
```

### Test Feature Generation

```bash
# Create a simple CSV payload
CSV_DATA="Feature,Story,Precondition,Given,When,Then,Acceptance Criteria
Collateral Registration,CAS-256008,None,User has valid collateral documents,User registers new collateral,System validates and stores collateral,All mandatory fields captured"

# Submit generation job
RESPONSE=$(curl -X POST http://localhost:8000/generate/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"jira_input_mode\": \"csv\",
    \"jira_csv_raw\": \"$CSV_DATA\",
    \"flow_type\": \"unordered\",
    \"three_amigos_notes\": \"Test generation\",
    \"module\": \"cas\"
  }")

# Extract job_id
JOB_ID=$(echo $RESPONSE | python -m json.tool | grep job_id | awk -F'"' '{print $4}')
echo "Job ID: $JOB_ID"

# Stream results (Server-Sent Events)
curl -N http://localhost:8000/generate/$JOB_ID/stream \
  -H "Authorization: Bearer $TOKEN"

# Should output:
# data: {"agent": 1, "elapsed": 2}
# data: {"agent": 2, "elapsed": 5}
# ... (agents 3-11)
# data: {"status": "done"}

# Get final result
curl -X GET http://localhost:8000/generate/$JOB_ID/result \
  -H "Authorization: Bearer $TOKEN"
```

### API Documentation

**Swagger UI:** http://localhost:8000/docs  
**ReDoc:** http://localhost:8000/redoc

Navigate to these URLs for interactive API documentation and testing.

---

## Monitoring

### Real-Time Log Monitoring

```bash
# Follow log file (Linux/Mac)
tail -f "D:\Code\Agentic_Forge\logs\forge.log"

# Watch for errors
grep ERROR "D:\Code\Agentic_Forge\logs\forge.log" | tail -20

# Count log entries
wc -l "D:\Code\Agentic_Forge\logs\forge.log"
```

### Database Monitoring

```bash
# Monitor active sessions
psql -U postgres -d agentic_forge_local -c "
SELECT usename, application_name, state, query 
FROM pg_stat_activity WHERE datname='agentic_forge_local';"

# Check table sizes
psql -U postgres -d agentic_forge_local -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;"

# Monitor generation jobs
psql -U postgres -d agentic_forge_local -c "
SELECT job_id, user_id, status, current_agent, created_at, updated_at 
FROM generation_jobs 
ORDER BY created_at DESC LIMIT 10;"
```

### Performance Metrics

**Check LLM response times:**
```bash
grep "llm_complete\|Agent" "D:\Code\Agentic_Forge\logs\forge.log" | grep elapsed
```

**Check database query times:**
```bash
psql -U postgres -d agentic_forge_local -c "
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC LIMIT 10;"
```

---

## Stopping the Server

### Graceful Shutdown

```bash
# If running in foreground terminal
Press CTRL+C

# Server logs shutdown message:
# INFO:     Shutting down
# INFO:     Finished server process
```

### Force Shutdown (if needed)

```bash
# Find process
ps aux | grep uvicorn

# Kill process
kill -9 <PID>

# Or use lsof
lsof -i :8000
kill -9 <PID>
```

---

## Common Tasks

### Create New User

```bash
python -m forge.scripts.create_user \
  --username john_doe \
  --display "John Doe" \
  --admin  # Optional, omit for regular user
```

### Index Feature Repository

```bash
# Full rebuild (clears old data)
python -m forge.scripts.index_repo --full-rebuild

# Incremental (only new/changed files)
python -m forge.scripts.index_repo
```

### Build FAISS Indices

```bash
# Step index (from unique_steps)
python -m forge.scripts.build_step_index

# CAS knowledge index (from PDFs)
python -m forge.scripts.build_knowledge
```

### Run Integration Tests

```bash
python -m forge.scripts.integration_test

# Output: Color-coded results for each sample
# Exit code 0 = all pass, 1 = at least one fail
```

### Verify Deployment

```bash
python -m forge.scripts.verify_setup

# Checks all 33 deployment requirements
# Exit code 0 = ready for production
```

### Reset Database

```bash
# Full reset (DESTRUCTIVE - clears all data)
python -m forge.scripts.setup_db --fresh

# Then recreate admin user
python -m forge.scripts.create_user --username anand --display "Anand" --admin
```

### Export/Backup Data

```bash
# Backup database
pg_dump -U postgres -d agentic_forge_local > backup_2026-04-27.sql

# Restore from backup
psql -U postgres -d agentic_forge_local < backup_2026-04-27.sql
```

---

## Troubleshooting

### Server Fails to Start

**Error:** `Address already in use`

```bash
# Port 8000 is in use by another process
lsof -i :8000
kill -9 <PID>

# OR use different port
uvicorn forge.api.main:app --port 8001
```

### Server Starts But Endpoints Fail

**Error:** `Internal Server Error`

1. Check logs: `tail -f "D:\Code\Agentic_Forge\logs\forge.log"`
2. Common causes:
   - Missing environment variables (check `.env`)
   - Database offline (test: `psql -U postgres -c "SELECT 1"`)
   - LLM model missing (check `LLM_MODEL_PATH` in `.env`)
   - FAISS indices not built (run build scripts)

### Job Hangs or Times Out

**Issue:** Generation job stuck in `pending` or `running`

**Solution:**
1. Check logs for errors: `grep "Agent\|ERROR" logs/forge.log | tail -20`
2. Check database job status: `SELECT * FROM generation_jobs WHERE status='running';`
3. Manually mark as failed if needed:
   ```sql
   UPDATE generation_jobs SET status='failed', reason='Manual reset' WHERE job_id='...';
   ```

### Database Connection Timeouts

**Error:** `Connection refused` or `connection timeout`

1. Verify PostgreSQL running: `psql -U postgres -c "SELECT 1"`
2. Check connection params in `.env`:
   - `DB_HOST` should be `localhost` or `127.0.0.1`
   - `DB_PORT` should be `5432`
   - `DB_USER` should be `postgres`
3. If on remote DB, ensure credentials and firewall rules correct

### LLM Errors

**Error:** `Model not loaded` or `CUDA out of memory`

**Solution:**
- If model unavailable, server continues but LLM endpoints return error
- To fix: Download model or set `LLM_GPU_LAYERS=0` to use CPU
- For CUDA OOM: Reduce context size or batch size in config

### Memory Usage Too High

**Server using >8GB RAM**

1. Check what's consuming memory:
   ```bash
   ps aux | grep uvicorn
   ```
2. Reduce `LLM_GPU_LAYERS` if using GPU
3. Reduce `MAX_CONCURRENT_JOBS` if running multiple
4. Check database connections: `SELECT COUNT(*) FROM pg_stat_activity;`
5. Restart server: `kill -9 <PID> && uvicorn ...`

### CORS Errors in Frontend

**Error:** `CORS error: origin not allowed`

All CORS origins already allowed in main.py:
```python
CORSMiddleware(allow_origins=["*"])
```

If still failing:
1. Verify frontend and backend on same local network
2. Check browser console for actual error message
3. Ensure Authorization header sent correctly

---

## Next Steps

- **Deploy to cloud:** AWS EC2, Azure App Service, GCP Cloud Run
- **Setup monitoring:** DataDog, New Relic, or CloudWatch
- **Setup auto-scaling:** For high-traffic deployments
- **Configure CI/CD:** GitHub Actions, GitLab CI
- **Backup strategy:** Regular database backups
- **Security hardening:** Rate limiting, WAF rules, DDoS protection

See [How_to_Maintain.md](How_to_Maintain.md) for operational procedures.

# How to Maintain Forge Agentic

**Last Updated:** 2026-04-27  
**Status:** Production Ready

---

## Table of Contents

1. [Daily Operations](#daily-operations)
2. [Database Maintenance](#database-maintenance)
3. [Index Maintenance](#index-maintenance)
4. [User Management](#user-management)
5. [Performance Tuning](#performance-tuning)
6. [Backups & Recovery](#backups--recovery)
7. [Updating Code](#updating-code)
8. [Common Issues](#common-issues)
9. [Monitoring Alerts](#monitoring-alerts)

---

## Daily Operations

### Server Health Check

Run daily to ensure system is ready:

```bash
python -m forge.scripts.verify_setup
```

**Expected:** All 33 checks pass, exit code 0.

**If any fail:**
1. Note which checks failed
2. See detailed error messages
3. Consult troubleshooting section below
4. Fix issues before proceeding

### Log Review

```bash
# Check for errors in past 24 hours
grep "ERROR\|CRITICAL" "D:\Code\Agentic_Forge\logs\forge.log" | tail -50

# If many errors, escalate
# Common patterns:
# - "LLMNotLoadedError" → model missing, acceptable if offline use
# - "Database connection failed" → DB down, restart PostgreSQL
# - "FAISS index not found" → Rebuild indices
# - "OutOfMemory" → Server memory exhausted, restart
```

### User Activity

```bash
# Check active chat sessions
psql -U postgres -d agentic_forge_local -c "
SELECT user_id, COUNT(*) as message_count 
FROM chat_messages 
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY user_id;"

# Check generation job activity
psql -U postgres -d agentic_forge_local -c "
SELECT status, COUNT(*) 
FROM generation_jobs 
WHERE created_at > NOW() - INTERVAL '24 hours'
GROUP BY status;"
```

---

## Database Maintenance

### Weekly: Analyze Query Performance

```bash
psql -U postgres -d agentic_forge_local -c "ANALYZE;"
```

This updates table statistics for query optimizer.

### Weekly: Vacuum Database

```bash
psql -U postgres -d agentic_forge_local -c "VACUUM ANALYZE;"
```

Reclaims disk space and optimizes indexes.

### Monthly: Refresh Materialized Views

```bash
psql -U postgres -d agentic_forge_local -c "
REFRESH MATERIALIZED VIEW CONCURRENTLY unique_steps;"
```

Updates the `unique_steps` view with any new steps. `CONCURRENTLY` allows queries while refreshing.

### Monthly: Check Index Health

```bash
psql -U postgres -d agentic_forge_local -c "
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE schemaname = 'public'
ORDER BY tablename;"

# Reindex if fragmented:
psql -U postgres -d agentic_forge_local -c "REINDEX DATABASE agentic_forge_local;"
```

### Check Table Sizes

```bash
# Top 10 largest tables
psql -U postgres -d agentic_forge_local -c "
SELECT schemaname, tablename, pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) 
FROM pg_tables WHERE schemaname = 'public' 
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC LIMIT 10;"

# Top 10 largest indices
psql -U postgres -d agentic_forge_local -c "
SELECT schemaname, tablename, indexname, pg_size_pretty(pg_relation_size(indexrelid)) 
FROM pg_indexes pi 
JOIN pg_class pc ON pi.indexname = pc.relname 
ORDER BY pg_relation_size(indexrelid) DESC LIMIT 10;"
```

### Archive Old Data

For very large deployments, archive generation jobs older than 90 days:

```bash
psql -U postgres -d agentic_forge_local -c "
-- Archive old jobs (example)
SELECT * INTO generation_jobs_archive_2026q1 
FROM generation_jobs 
WHERE created_at < '2026-04-01' AND status IN ('done', 'failed');

DELETE FROM generation_jobs 
WHERE created_at < '2026-04-01' AND status IN ('done', 'failed');

ANALYZE;"
```

---

## Index Maintenance

### Rebuild Step Index (After Repo Change)

```bash
# If feature repository updated with new steps
python -m forge.scripts.index_repo --full-rebuild

# Then rebuild FAISS
python -m forge.scripts.build_step_index
```

### Rebuild CAS Knowledge Index (After Doc Update)

```bash
# If new CAS PDFs added to data/knowledge/cas/
python -m forge.scripts.build_knowledge
```

### Verify Index Integrity

```python
# Quick check that indices load correctly
from forge.infrastructure.embedder import load_index
from pathlib import Path

# Load step index
try:
    step_index, step_map = load_index()
    print(f"✓ Step index: {len(step_map)} steps")
except Exception as e:
    print(f"✗ Step index error: {e}")

# Load CAS knowledge index
try:
    from forge.infrastructure.rag_engine import load_knowledge_index
    kg_index = load_knowledge_index()
    print(f"✓ CAS knowledge index loaded")
except Exception as e:
    print(f"✗ CAS knowledge error: {e}")
```

---

## User Management

### Create User

```bash
python -m forge.scripts.create_user \
  --username john_doe \
  --display "John Doe" \
  --password "secure_password"
```

### List Users

```bash
psql -U postgres -d agentic_forge_local -c "
SELECT id, username, display_name, is_admin, is_active, created_at 
FROM users ORDER BY created_at DESC;"
```

### Deactivate User (Soft Delete)

```bash
# User can no longer login, but data preserved
psql -U postgres -d agentic_forge_local -c "
UPDATE users SET is_active = FALSE 
WHERE username = 'john_doe';"
```

### Reset User Password

```bash
psql -U postgres -d agentic_forge_local -c "
-- First, hash the new password
-- Use this command in Python:
python -c "from forge.api.auth import hash_password; print(hash_password('new_password'))"

-- Then update:
UPDATE users SET password_hash = '<hash_from_above>' 
WHERE username = 'john_doe';"
```

### Delete User & Their Data

```bash
# DESTRUCTIVE: Also deletes all user's chat sessions and generation jobs
psql -U postgres -d agentic_forge_local -c "
DELETE FROM chat_messages WHERE session_id IN (
  SELECT id FROM chat_sessions WHERE user_id = (
    SELECT id FROM users WHERE username = 'john_doe'
  )
);

DELETE FROM chat_sessions WHERE user_id = (
  SELECT id FROM users WHERE username = 'john_doe'
);

DELETE FROM generation_jobs WHERE user_id = (
  SELECT id FROM users WHERE username = 'john_doe'
);

DELETE FROM user_settings WHERE user_id = (
  SELECT id FROM users WHERE username = 'john_doe'
);

DELETE FROM users WHERE username = 'john_doe';"
```

### Update User Permissions

```bash
# Grant admin rights
psql -U postgres -d agentic_forge_local -c "
UPDATE users SET is_admin = TRUE 
WHERE username = 'john_doe';"

# Revoke admin rights
psql -U postgres -d agentic_forge_local -c "
UPDATE users SET is_admin = FALSE 
WHERE username = 'john_doe';"
```

---

## Performance Tuning

### Slow Generation Jobs

**If jobs take >5 minutes:**

1. Check which agent is slow:
   ```bash
   grep "Agent\|elapsed" logs/forge.log | tail -20
   ```

2. Common bottlenecks:
   - **Agent 6 (Retriever)** — FAISS search slow if index too large
   - **Agent 2 (Domain Expert)** — RAG engine slow if CAS knowledge large
   - **Agent 8/9 (Validation/Writer)** — LLM response slow

3. Optimization:
   ```bash
   # Rebuild FAISS indices with smaller data
   python -m forge.scripts.build_step_index
   
   # Limit CAS knowledge size (keep only essential docs)
   rm -rf data/knowledge/cas/old_docs
   python -m forge.scripts.build_knowledge
   ```

### High Memory Usage

**If RAM usage >8GB:**

1. Reduce batch sizes in code:
   ```python
   # In embedder.py, reduce BATCH_SIZE from 256 to 128
   BATCH_SIZE = 128
   ```

2. Reduce concurrent jobs:
   ```bash
   # In .env
   MAX_CONCURRENT_JOBS=1  # Instead of higher number
   ```

3. Reduce LLM context:
   ```bash
   # In .env
   LLM_CONTEXT_SIZE=4096  # Instead of 8192
   ```

### Database Slow Queries

```bash
# Enable slow query log
psql -U postgres -d agentic_forge_local -c "
ALTER DATABASE agentic_forge_local SET log_min_duration_statement = 1000;"  # 1 second

# Then check for slow queries
grep "duration:" /var/log/postgresql/postgresql.log | grep "duration: [1-9][0-9][0-9]" | head -20
```

### FAISS Search Performance

```python
# If FAISS search slow:
# 1. Check index size
import numpy as np
step_map = np.load('data/indices/step_id_map.npy', allow_pickle=True)
print(f"Index has {len(step_map)} vectors")

# If >100k vectors, consider:
# - Partitioning index by stage/screen
# - Using IVF index instead of flat
# - Implementing caching layer
```

---

## Backups & Recovery

### Daily Backup Strategy

```bash
#!/bin/bash
# Save as backup_daily.sh

BACKUP_DIR="D:\Code\Agentic_Forge\backups"
mkdir -p "$BACKUP_DIR"

TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Database backup
pg_dump -U postgres -d agentic_forge_local \
  | gzip > "$BACKUP_DIR/db_backup_$TIMESTAMP.sql.gz"

# FAISS indices backup
tar -czf "$BACKUP_DIR/indices_backup_$TIMESTAMP.tar.gz" \
  "D:\Code\Agentic_Forge\data\indices"

# Logs backup
tar -czf "$BACKUP_DIR/logs_backup_$TIMESTAMP.tar.gz" \
  "D:\Code\Agentic_Forge\logs"

# Cleanup old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.gz" -mtime +30 -delete

echo "Backup complete: $TIMESTAMP"
```

**Schedule daily:**
```bash
# Linux: Add to crontab
0 2 * * * /path/to/backup_daily.sh

# Windows: Use Task Scheduler
# Create task to run: backup_daily.bat
```

### Restore from Backup

```bash
# Restore database
zcat backup_db_20260427_020000.sql.gz | psql -U postgres -d agentic_forge_local

# Restore indices
tar -xzf backup_indices_20260427_020000.tar.gz -C /

# Restore logs
tar -xzf backup_logs_20260427_020000.tar.gz -C /
```

### Test Backup Integrity

```bash
# Restore to test database
psql -U postgres -c "CREATE DATABASE test_restore;"
zcat backup_db_latest.sql.gz | psql -U postgres -d test_restore

# Verify
psql -U postgres -d test_restore -c "SELECT COUNT(*) FROM users; SELECT COUNT(*) FROM unique_steps;"

# Cleanup
psql -U postgres -c "DROP DATABASE test_restore;"
```

---

## Updating Code

### Pull Latest Changes

```bash
git pull origin main

# Verify no uncommitted changes
git status
```

### Update Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt --upgrade
```

### Database Migrations (if schema changed)

```bash
# Check if schema changes needed
python -m forge.scripts.setup_db

# If changes made:
# 1. Backup first
# 2. Review migration SQL
# 3. Run setup_db --fresh (if safe) or manual ALTER statements
```

### Restart Server

```bash
# Kill old process
lsof -i :8000 | awk 'NR!=1 {print $2}' | xargs kill -9

# Start new version
uvicorn forge.api.main:app --port 8000
```

### Rollback if Needed

```bash
# If new version causes issues:
git revert HEAD
git pull origin main

# Restore database backup
psql -U postgres < backup_db_YYYYMMDD_HHMMSS.sql

# Restart
python -m forge.scripts.verify_setup
```

---

## Common Issues

### "Stale jobs not cleaned up on startup"

```
WARNING: Stale jobs marked failed: 3 jobs
```

This is normal. Jobs left in `pending`/`running` state for >1 hour are marked failed on server restart.

**Fix if needed:**
```sql
UPDATE generation_jobs 
SET status='failed', reason='Marked stale on server restart'
WHERE status IN ('pending', 'running') AND updated_at < NOW() - INTERVAL '1 hour';
```

### "Materialized view refresh slow"

```bash
# REFRESH MATERIALIZED VIEW CONCURRENTLY unique_steps;
# Takes >30 seconds
```

If slow:
1. Check unique_steps row count: `SELECT COUNT(*) FROM unique_steps;`
2. If >50k rows, consider archiving old data
3. Drop and recreate view if severely fragmented:
   ```sql
   DROP MATERIALIZED VIEW unique_steps;
   -- (run setup_db to recreate)
   ```

### "PostgreSQL running out of connections"

```
FATAL: sorry, too many clients already
```

**Solution:**
1. Check active connections:
   ```sql
   SELECT COUNT(*) FROM pg_stat_activity;
   ```

2. Increase max connections:
   ```bash
   # Edit postgresql.conf
   max_connections = 200  # Default 100
   
   # Restart PostgreSQL
   sudo systemctl restart postgresql
   ```

3. Close idle connections:
   ```sql
   SELECT pg_terminate_backend(pid) 
   FROM pg_stat_activity 
   WHERE state = 'idle' AND state_change < NOW() - INTERVAL '1 hour';
   ```

### "FAISS index corrupted"

```
IndexError: Tried to retrieve an element that has not been added yet
```

**Fix:**
```bash
# Rebuild indices from scratch
rm -f data/indices/faiss_index.bin data/indices/step_id_map.npy

python -m forge.scripts.build_step_index
python -m forge.scripts.build_knowledge

# Verify
python -m forge.scripts.verify_setup
```

---

## Monitoring Alerts

### Setup Email Alerts (Optional)

**For critical errors, send email:**

```python
# Add to forge/core/alerts.py
import smtplib
from email.mime.text import MIMEText

def send_alert(subject, message):
    """Send email alert on critical events."""
    sender = "forge-alerts@company.com"
    recipient = "ops@company.com"
    
    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = recipient
    
    with smtplib.SMTP('localhost') as server:
        server.send_message(msg)

# Then in forge/api/main.py on error:
# send_alert("Forge Critical Error", "Server crashed on Agent 6")
```

### Key Metrics to Monitor

```bash
# Check these daily:

# 1. Success rate
psql -U postgres -d agentic_forge_local -c "
SELECT status, COUNT(*) FROM generation_jobs 
GROUP BY status;"

# 2. Average generation time
psql -U postgres -d agentic_forge_local -c "
SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at))) as avg_seconds
FROM generation_jobs WHERE status = 'done';"

# 3. User growth
psql -U postgres -d agentic_forge_local -c "
SELECT DATE(created_at) as day, COUNT(*) as new_users
FROM users GROUP BY DATE(created_at) ORDER BY day DESC LIMIT 30;"

# 4. Error count
grep -c ERROR logs/forge.log | tail -10

# 5. Database size
psql -U postgres -d agentic_forge_local -c "
SELECT pg_size_pretty(pg_database_size('agentic_forge_local'));"
```

### Recommended Alert Thresholds

| Metric | Threshold | Action |
|--------|-----------|--------|
| Job failure rate | >10% | Investigate errors |
| Avg generation time | >10 minutes | Check LLM/DB performance |
| DB size growth | >50% month-over-month | Archive old data |
| Error count | >100/day | Review error logs |
| Database connections | >80 | Investigate slow queries |
| Disk usage | >80% | Cleanup old files |

---

## Support & Escalation

### Before Escalating

1. Check logs: `tail -100 logs/forge.log`
2. Run verification: `python -m forge.scripts.verify_setup`
3. Check database: `psql -U postgres -d agentic_forge_local -c "SELECT 1;"`
4. Restart server (if safe): `kill -9 <PID> && uvicorn ...`

### When to Escalate

- Database won't connect
- Multiple generation jobs failing
- Server memory exhausted
- FAISS indices corrupted
- Unrecoverable errors in logs

### Provide to Support Team

```bash
# Collect diagnostic bundle
mkdir -p forge_diagnostics

cp logs/forge.log forge_diagnostics/
psql -U postgres -d agentic_forge_local -c "
SELECT * FROM generation_jobs ORDER BY updated_at DESC LIMIT 100;" \
  > forge_diagnostics/recent_jobs.csv

psql -U postgres -d agentic_forge_local -c "
SELECT name, setting FROM pg_settings WHERE name LIKE '%max%';" \
  > forge_diagnostics/db_config.txt

python -m forge.scripts.verify_setup > forge_diagnostics/verify.log 2>&1

echo "System date: $(date)" > forge_diagnostics/system_info.txt
echo "Python version: $(python --version)" >> forge_diagnostics/system_info.txt
echo "PostgreSQL version: $(psql --version)" >> forge_diagnostics/system_info.txt

# Share forge_diagnostics/ folder with support
```

---

## Next Steps

- **Scale up:** Add load balancing, caching (Redis), CDN
- **Monitor:** Setup DataDog or New Relic for continuous monitoring
- **Automate:** CI/CD pipeline for automated deployments
- **Document runbooks:** For common incidents
- **Train team:** On deployment and troubleshooting procedures

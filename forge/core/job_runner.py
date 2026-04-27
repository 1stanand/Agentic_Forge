"""
Generation Job Runner

In-process async queue for ATDD feature generation jobs.
Respects MAX_CONCURRENT_JOBS limit. Updates generation_jobs table with progress.
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional, Callable, Dict, Any
from uuid import uuid4

from forge.core.config import get_settings
from forge.core.db import get_cursor, get_conn, release_conn
from forge.core.state import ForgeState
from forge.core.graph import run_graph

logger = logging.getLogger(__name__)

# In-memory job queue and status
_active_jobs: Dict[str, Dict[str, Any]] = {}
_job_lock = asyncio.Lock()


async def submit_generation_job(
    user_id: str,
    jira_input_mode: str,
    jira_csv_raw: Optional[str] = None,
    jira_story_id: Optional[str] = None,
    jira_pat_override: Optional[str] = None,
    flow_type: str = "unordered",
    three_amigos_notes: str = "",
    module: str = "cas"
) -> str:
    """Submit a new feature generation job.

    Checks active job limit. Creates DB row with status='pending'.
    Starts async task if under limit, else returns job_id with pending status.

    Returns: job_id (UUID)
    """

    job_id = str(uuid4())
    max_jobs = get_settings().max_concurrent_jobs

    async with _job_lock:
        active_count = len([j for j in _active_jobs.values() if j["status"] in ["pending", "running"]])

        if active_count >= max_jobs:
            logger.warning(f"Job limit reached ({max_jobs}). Queuing {job_id}")
            _save_job_to_db(job_id, user_id, "queued")
            return job_id

    # Create DB row
    _save_job_to_db(job_id, user_id, "pending")

    # Start async task
    _active_jobs[job_id] = {
        "job_id": job_id,
        "user_id": user_id,
        "status": "pending",
        "current_agent": 0,
        "elapsed_seconds": 0,
        "result": None,
        "error": None,
        "start_time": time.time()
    }

    # Schedule task (non-blocking)
    asyncio.create_task(_run_generation_task(
        job_id=job_id,
        user_id=user_id,
        jira_input_mode=jira_input_mode,
        jira_csv_raw=jira_csv_raw,
        jira_story_id=jira_story_id,
        jira_pat_override=jira_pat_override,
        flow_type=flow_type,
        three_amigos_notes=three_amigos_notes,
        module=module
    ))

    logger.info(f"Job submitted: {job_id} for user {user_id}")
    return job_id


async def _run_generation_task(
    job_id: str,
    user_id: str,
    jira_input_mode: str,
    jira_csv_raw: Optional[str],
    jira_story_id: Optional[str],
    jira_pat_override: Optional[str],
    flow_type: str,
    three_amigos_notes: str,
    module: str
):
    """Run the generation pipeline for this job.

    Updates DB with status, current_agent, elapsed_seconds after each agent.
    """

    try:
        # Update status to running
        async with _job_lock:
            if job_id in _active_jobs:
                _active_jobs[job_id]["status"] = "running"

        _update_job_in_db(job_id, status="running", current_agent=0)

        # Build initial state
        state = ForgeState(
            user_id=user_id,
            jira_input_mode=jira_input_mode,
            jira_csv_raw=jira_csv_raw or "",
            jira_story_id=jira_story_id,
            jira_pat_override=jira_pat_override,
            flow_type=flow_type,
            three_amigos_notes=three_amigos_notes,
            jira_facts={},
            domain_brief={},
            scope={},
            coverage_plan={},
            action_sequences={},
            retrieved_steps={},
            composed_scenarios={},
            validation_result={},
            feature_file={},
            critic_review={},
            final_output={}
        )

        # Run graph
        start = time.time()
        result = run_graph(state)

        elapsed = int(time.time() - start)

        # Save result
        async with _job_lock:
            if job_id in _active_jobs:
                _active_jobs[job_id]["status"] = "done"
                _active_jobs[job_id]["elapsed_seconds"] = elapsed
                _active_jobs[job_id]["result"] = result

        # Update DB
        feature_file = result.get("final_output", {}).get("feature_file", "")
        gap_report = result.get("final_output", {}).get("gap_report", {})

        _update_job_in_db(
            job_id,
            status="done",
            current_agent=11,
            elapsed_seconds=elapsed,
            result_feature_file=feature_file,
            result_gaps=str(gap_report)
        )

        logger.info(f"Job completed: {job_id} in {elapsed}s")

    except Exception as e:
        logger.error(f"Job failed: {job_id} — {e}")

        # Save error
        async with _job_lock:
            if job_id in _active_jobs:
                _active_jobs[job_id]["status"] = "failed"
                _active_jobs[job_id]["error"] = str(e)

        _update_job_in_db(job_id, status="failed", error_message=str(e))


def get_job_status(job_id: str, user_id: str) -> Dict[str, Any]:
    """Get current status of a job (user isolation enforced in caller)."""

    # Check in-memory first
    if job_id in _active_jobs:
        job = _active_jobs[job_id]
        return {
            "job_id": job_id,
            "status": job["status"],
            "current_agent": job["current_agent"],
            "elapsed_seconds": job["elapsed_seconds"],
            "error": job.get("error")
        }

    # Check DB
    conn = get_conn()
    try:
        with get_cursor(conn) as cursor:
            cursor.execute("""
                SELECT id, user_id, status, current_agent, elapsed_seconds, error_message
                FROM generation_jobs
                WHERE id = %s AND user_id = %s
            """, (job_id, int(user_id)))

            row = cursor.fetchone()
            if not row:
                raise ValueError("Job not found")

            return {
                "job_id": str(row[0]),
                "status": row[2],
                "current_agent": row[3] or 0,
                "elapsed_seconds": row[4] or 0,
                "error": row[5]
            }
    finally:
        release_conn(conn)


def get_job_result(job_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """Get final result of a completed job (user isolation enforced in caller)."""

    conn = get_conn()
    try:
        with get_cursor(conn) as cursor:
            cursor.execute("""
                SELECT id, feature_file, gap_report
                FROM generation_jobs
                WHERE id = %s AND user_id = %s AND status = 'done'
            """, (job_id, int(user_id)))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                "job_id": str(row[0]),
                "feature_file": row[1] or "",
                "gaps": row[2] or {}
            }
    finally:
        release_conn(conn)


def _save_job_to_db(job_id: str, user_id: str, status: str):
    """Save new job to generation_jobs table."""

    conn = get_conn()
    try:
        with get_cursor(conn) as cursor:
            cursor.execute("""
                INSERT INTO generation_jobs
                    (id, user_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
            """, (job_id, int(user_id), status, datetime.now(), datetime.now()))

            logger.debug(f"Job saved to DB: {job_id}")

    except Exception as e:
        logger.error(f"Failed to save job: {e}")
        raise

    finally:
        release_conn(conn)


def _update_job_in_db(
    job_id: str,
    status: Optional[str] = None,
    current_agent: Optional[int] = None,
    elapsed_seconds: Optional[int] = None,
    result_feature_file: Optional[str] = None,
    result_gaps: Optional[str] = None,
    error_message: Optional[str] = None
):
    """Update job status in generation_jobs table."""

    conn = get_conn()
    try:
        with get_cursor(conn) as cursor:
            updates = []
            params = []

            if status is not None:
                updates.append("status = %s")
                params.append(status)

            if current_agent is not None:
                updates.append("current_agent = %s")
                params.append(current_agent)

            if elapsed_seconds is not None:
                updates.append("elapsed_seconds = %s")
                params.append(elapsed_seconds)

            if result_feature_file is not None:
                updates.append("feature_file = %s")
                params.append(result_feature_file)

            if result_gaps is not None:
                updates.append("gap_report = %s")
                params.append(result_gaps)

            if error_message is not None:
                updates.append("error_message = %s")
                params.append(error_message)

            if not updates:
                return

            updates.append("updated_at = %s")
            params.append(datetime.now())
            params.append(job_id)

            sql = f"UPDATE generation_jobs SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(sql, params)

            logger.debug(f"Job updated: {job_id}")

    except Exception as e:
        logger.error(f"Failed to update job: {e}")
        raise

    finally:
        release_conn(conn)


def mark_stale_jobs_failed(age_seconds: int = 3600):
    """On startup: mark any pending/running jobs older than age_seconds as failed."""

    conn = get_conn()
    try:
        with get_cursor(conn) as cursor:
            cursor.execute("""
                UPDATE generation_jobs
                SET status = 'failed',
                    error_message = 'Server restarted before job completed',
                    updated_at = %s
                WHERE status IN ('pending', 'running')
                AND updated_at < NOW() - INTERVAL '1 second' * %s
            """, (datetime.now(), age_seconds))

    except Exception as e:
        logger.warning(f"Failed to mark stale jobs: {e}")

    finally:
        release_conn(conn)

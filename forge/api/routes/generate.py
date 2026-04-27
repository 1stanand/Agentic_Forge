"""
Feature Generation Routes

Endpoints:
- POST /generate/ — submit generation job (202 + job_id)
- GET /generate/{job_id}/stream — SSE stream of agent progress
- GET /generate/{job_id}/result — get final feature file
"""

import asyncio
import json
import logging
from typing import AsyncGenerator, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from forge.api.auth import verify_token
from forge.core.job_runner import (
    submit_generation_job, get_job_status, get_job_result, mark_stale_jobs_failed
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/generate", tags=["generate"])


# Request/Response Models
class GenerateRequest(BaseModel):
    jira_input_mode: str  # "csv" or "pat"
    jira_csv_raw: Optional[str] = None  # CSV data (for csv mode)
    jira_story_id: Optional[str] = None  # Story ID (for pat mode)
    jira_pat_override: Optional[str] = None  # Optional PAT override
    flow_type: str = "unordered"  # "ordered" or "unordered"
    three_amigos_notes: str = ""  # Optional notes
    module: str = "cas"  # "cas" (only option for now)


class GenerateResponse(BaseModel):
    job_id: str
    status: str  # "pending"
    message: str


class GenerateResultResponse(BaseModel):
    job_id: str
    status: str
    feature_file: str
    gaps: Optional[dict] = None


class GenerateStreamEvent(BaseModel):
    agent: Optional[int] = None
    elapsed: Optional[int] = None
    status: Optional[str] = None
    reason: Optional[str] = None


@router.post("/", status_code=202)
async def submit_job(
    request: GenerateRequest,
    current_user: dict = Depends(verify_token)
) -> GenerateResponse:
    """Submit a feature generation job.

    Returns job_id immediately (HTTP 202).
    Check /generate/{job_id}/stream for progress, /generate/{job_id}/result for output.
    """

    try:
        user_id = current_user["user_id"]

        # Validate input
        if request.jira_input_mode == "csv" and not request.jira_csv_raw:
            raise HTTPException(status_code=400, detail="jira_csv_raw required for csv mode")

        if request.jira_input_mode == "pat" and not request.jira_story_id:
            raise HTTPException(status_code=400, detail="jira_story_id required for pat mode")

        # Submit job
        job_id = await submit_generation_job(
            user_id=user_id,
            jira_input_mode=request.jira_input_mode,
            jira_csv_raw=request.jira_csv_raw,
            jira_story_id=request.jira_story_id,
            jira_pat_override=request.jira_pat_override,
            flow_type=request.flow_type,
            three_amigos_notes=request.three_amigos_notes,
            module=request.module
        )

        logger.info(f"Job submitted: {job_id} for user {user_id}")

        return GenerateResponse(
            job_id=job_id,
            status="pending",
            message=f"Job {job_id} queued. Check /generate/{job_id}/stream for progress."
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Submit job error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{job_id}/stream")
async def stream_job_progress(
    job_id: str,
    current_user: dict = Depends(verify_token)
) -> StreamingResponse:
    """Stream job progress via Server-Sent Events (SSE).

    Client must use authenticated fetch() with Authorization header (not EventSource).
    Events:
    - {"agent": N, "elapsed": seconds} — after each agent completes
    - {"status": "done"} — job completed successfully
    - {"status": "failed", "reason": "error message"} — job failed
    """

    async def event_generator() -> AsyncGenerator[str, None]:
        """Generate SSE events for job progress."""

        user_id = current_user["user_id"]
        last_agent = 0
        poll_interval = 0.5  # seconds
        max_wait = 3600  # 1 hour timeout

        start_time = asyncio.get_event_loop().time()

        try:
            while True:
                # Check timeout
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > max_wait:
                    event = json.dumps({"status": "failed", "reason": f"Job timeout after {max_wait}s"})
                    yield f'data: {event}\n\n'
                    break

                # Get job status
                try:
                    status = get_job_status(job_id, user_id)
                except ValueError:
                    event = json.dumps({"status": "failed", "reason": "Job not found"})
                    yield f'data: {event}\n\n'
                    break

                job_status = status["status"]
                current_agent = status["current_agent"]
                elapsed_sec = status["elapsed_seconds"]

                # Emit agent progress events
                if current_agent > last_agent:
                    for agent_num in range(last_agent + 1, current_agent + 1):
                        event = json.dumps({"agent": agent_num, "elapsed": elapsed_sec})
                        yield f'data: {event}\n\n'
                    last_agent = current_agent

                # Check for completion
                if job_status == "done":
                    event = json.dumps({"status": "done"})
                    yield f'data: {event}\n\n'
                    break

                elif job_status == "failed":
                    error = status.get("error", "Unknown error")
                    event = json.dumps({"status": "failed", "reason": error})
                    yield f'data: {event}\n\n'
                    break

                # Poll again
                await asyncio.sleep(poll_interval)

        except Exception as e:
            logger.error(f"Stream error: {e}")
            event = json.dumps({"status": "failed", "reason": str(e)})
            yield f'data: {event}\n\n'

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )


@router.get("/{job_id}/result", response_model=GenerateResultResponse)
async def get_result(
    job_id: str,
    current_user: dict = Depends(verify_token)
) -> GenerateResultResponse:
    """Get the final feature file and gap report for a completed job.

    Only available if job status is 'done'.
    """

    try:
        user_id = current_user["user_id"]

        # Get status
        status = get_job_status(job_id, user_id)

        if status["status"] not in ["done", "failed"]:
            raise HTTPException(status_code=202, detail=f"Job still {status['status']}")

        if status["status"] == "failed":
            raise HTTPException(status_code=500, detail=f"Job failed: {status.get('error')}")

        # Get result
        result = get_job_result(job_id, user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Result not found")

        return GenerateResultResponse(
            job_id=job_id,
            status="done",
            feature_file=result["feature_file"],
            gaps=result.get("gaps")
        )

    except HTTPException:
        raise
    except ValueError:
        raise HTTPException(status_code=404, detail="Job not found")
    except Exception as e:
        logger.error(f"Get result error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Startup hook: mark stale jobs as failed
async def on_startup():
    """Mark any pending/running jobs older than 1 hour as failed."""
    mark_stale_jobs_failed(age_seconds=3600)
    logger.info("Marked stale jobs as failed on startup")

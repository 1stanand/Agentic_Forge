"""
Chat API Routes

Endpoints:
- POST /chat/ — send message, get response
- GET /chat/sessions — list user's sessions
- GET /chat/sessions/{id} — get session with history
- DELETE /chat/sessions/{id} — delete session
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from forge.api.auth import verify_token
from forge.chat.chat_engine import (
    process_message, get_session_history, list_user_sessions, delete_user_session
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])


# Request/Response Models
class ChatMessageRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    screen: Optional[str] = None
    stage: Optional[str] = None
    lob: Optional[str] = None


class ChatMessageResponse(BaseModel):
    session_id: str
    message_id: str
    context_type: str
    response: str
    context_used: bool


class ChatSessionSummary(BaseModel):
    session_id: str
    session_name: str
    created_at: str
    updated_at: str
    message_count: int


class ChatSessionDetail(BaseModel):
    session_id: str
    user_id: str
    session_name: str
    created_at: str
    updated_at: str
    messages: list


@router.post("/", response_model=ChatMessageResponse)
async def send_message(
    request: ChatMessageRequest,
    current_user: dict = Depends(verify_token)
) -> ChatMessageResponse:
    """Send a chat message and get a response.

    Creates new session if session_id is null.
    """

    try:
        user_id = current_user["user_id"]

        result = process_message(
            user_id=user_id,
            message_text=request.message,
            session_id=request.session_id,
            screen=request.screen,
            stage=request.stage,
            lob=request.lob
        )

        return ChatMessageResponse(
            session_id=result["session_id"],
            message_id=result["message_id"],
            context_type=result["context_type"],
            response=result["response"],
            context_used=result["context_used"]
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions", response_model=list[ChatSessionSummary])
async def list_sessions(
    current_user: dict = Depends(verify_token)
) -> list[ChatSessionSummary]:
    """List all chat sessions for the current user."""

    try:
        user_id = current_user["user_id"]
        sessions = list_user_sessions(user_id)

        return [
            ChatSessionSummary(
                session_id=s["session_id"],
                session_name=s["session_name"],
                created_at=s["created_at"].isoformat() if hasattr(s["created_at"], "isoformat") else str(s["created_at"]),
                updated_at=s["updated_at"].isoformat() if hasattr(s["updated_at"], "isoformat") else str(s["updated_at"]),
                message_count=s["message_count"]
            )
            for s in sessions
        ]

    except Exception as e:
        logger.error(f"List sessions error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
async def get_session(
    session_id: str,
    current_user: dict = Depends(verify_token)
) -> ChatSessionDetail:
    """Get a specific chat session with full message history.

    Per-user isolation: user can only access their own sessions.
    """

    try:
        user_id = current_user["user_id"]
        session = get_session_history(user_id, session_id)

        # Convert timestamps to ISO format
        messages = [
            {
                **m,
                "created_at": m["created_at"].isoformat() if hasattr(m["created_at"], "isoformat") else str(m["created_at"])
            }
            for m in session.get("messages", [])
        ]

        return ChatSessionDetail(
            session_id=session["session_id"],
            user_id=session["user_id"],
            session_name=session["session_name"],
            created_at=session["created_at"].isoformat() if hasattr(session["created_at"], "isoformat") else str(session["created_at"]),
            updated_at=session["updated_at"].isoformat() if hasattr(session["updated_at"], "isoformat") else str(session["updated_at"]),
            messages=messages
        )

    except ValueError:
        raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        logger.error(f"Get session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(verify_token)
) -> dict:
    """Delete a chat session and all its messages.

    Per-user isolation: user can only delete their own sessions.
    """

    try:
        user_id = current_user["user_id"]
        deleted = delete_user_session(user_id, session_id)

        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")

        return {"message": "Session deleted", "session_id": session_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete session error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

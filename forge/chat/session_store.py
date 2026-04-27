"""
Chat Session Store

PostgreSQL-backed chat message persistence.
Per-user isolation. Updates chat_sessions.updated_at on each message.

Tables: chat_sessions, chat_messages
"""

import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from uuid import uuid4

from forge.core.db import get_cursor, get_conn, release_conn

logger = logging.getLogger(__name__)


def create_session(user_id: str, session_name: Optional[str] = None) -> str:
    """Create a new chat session for the user.

    Returns: session_id (UUID)
    """
    name = session_name or f"Chat {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    conn = get_conn()
    try:
        with get_cursor(conn, dict_cursor=False) as cursor:
            cursor.execute("""
                INSERT INTO chat_sessions (user_id, title, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id
            """, (int(user_id), name, datetime.now(), datetime.now()))

            session_id = cursor.fetchone()[0]
            logger.info(f"Session created: {session_id} for user {user_id}")
            return str(session_id)
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise
    finally:
        release_conn(conn)


def save_message(session_id: str, user_id: str, message_text: str, sender: str,
                 context_type: str = "general") -> str:
    """Save a chat message to the session.

    sender: "user" or "assistant"
    context_type: "cas", "atdd", or "general"

    Returns: message_id (UUID)
    """
    timestamp = datetime.now()

    conn = get_conn()
    try:
        with get_cursor(conn, dict_cursor=False) as cursor:
            # Insert message
            cursor.execute("""
                INSERT INTO chat_messages
                    (session_id, role, content, context_type, created_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (session_id, sender, message_text, context_type, timestamp))

            message_id = cursor.fetchone()[0]

            # Update session updated_at
            cursor.execute("""
                UPDATE chat_sessions
                SET updated_at = %s
                WHERE id = %s AND user_id = %s
            """, (timestamp, session_id, int(user_id)))

            logger.debug(f"Message saved: {message_id} to session {session_id}")
            return str(message_id)

    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        raise
    finally:
        release_conn(conn)


def load_session(session_id: str, user_id: str, limit: int = 50) -> Dict[str, Any]:
    """Load a chat session with message history.

    Enforces per-user isolation.

    Returns: {
        "session_id": str,
        "user_id": str,
        "session_name": str,
        "created_at": datetime,
        "updated_at": datetime,
        "messages": [{"message_id", "sender", "text", "context_type", "created_at"}]
    }
    """
    conn = get_conn()
    try:
        with get_cursor(conn) as cursor:
            # Fetch session (with user isolation check)
            cursor.execute("""
                SELECT id, user_id, title, created_at, updated_at
                FROM chat_sessions
                WHERE id = %s AND user_id = %s
            """, (session_id, int(user_id)))

            session_row = cursor.fetchone()
            if not session_row:
                logger.warning(f"Session not found or access denied: {session_id} for user {user_id}")
                raise ValueError("Session not found")

            # Fetch messages (latest limit)
            cursor.execute("""
                SELECT id, role, content, context_type, created_at
                FROM chat_messages
                WHERE session_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (session_id, limit))

            messages = []
            for row in cursor.fetchall():
                messages.append({
                    "message_id": str(row[0]),
                    "sender": row[1],
                    "text": row[2],
                    "context_type": row[3],
                    "created_at": row[4]
                })

            # Reverse to chronological order
            messages.reverse()

            logger.debug(f"Loaded session {session_id}: {len(messages)} messages")

            return {
                "session_id": str(session_row[0]),
                "user_id": session_row[1],
                "session_name": session_row[2],
                "created_at": session_row[3],
                "updated_at": session_row[4],
                "messages": messages
            }

    except Exception as e:
        logger.error(f"Failed to load session: {e}")
        raise
    finally:
        release_conn(conn)


def list_sessions(user_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """List all chat sessions for a user.

    Returns: [{"session_id", "session_name", "created_at", "updated_at", "message_count"}]
    """
    conn = get_conn()
    try:
        with get_cursor(conn) as cursor:
            cursor.execute("""
                SELECT
                    cs.id,
                    cs.title,
                    cs.created_at,
                    cs.updated_at,
                    COUNT(cm.id) as message_count
                FROM chat_sessions cs
                LEFT JOIN chat_messages cm ON cs.id = cm.session_id
                WHERE cs.user_id = %s
                GROUP BY cs.id, cs.title, cs.created_at, cs.updated_at
                ORDER BY cs.updated_at DESC
                LIMIT %s
            """, (int(user_id), limit))

            sessions = []
            for row in cursor.fetchall():
                sessions.append({
                    "session_id": str(row[0]),
                    "session_name": row[1],
                    "created_at": row[2],
                    "updated_at": row[3],
                    "message_count": row[4] or 0
                })

            logger.debug(f"Listed {len(sessions)} sessions for user {user_id}")
            return sessions

    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise
    finally:
        release_conn(conn)


def delete_session(session_id: str, user_id: str) -> bool:
    """Delete a chat session and all its messages.

    Enforces per-user isolation. Returns True if deleted, False if not found.
    """
    conn = get_conn()
    try:
        with get_cursor(conn) as cursor:
            # Delete session (cascade will delete messages)
            cursor.execute("""
                DELETE FROM chat_sessions
                WHERE id = %s AND user_id = %s
            """, (session_id, int(user_id)))

            logger.debug(f"Session deleted: {session_id} for user {user_id}")
            return True

    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise
    finally:
        release_conn(conn)

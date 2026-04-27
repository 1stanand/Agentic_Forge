"""
Admin API Routes

Endpoints (admin JWT required):
- POST /admin/users — create user
- GET /admin/users — list all users
- DELETE /admin/users/{id} — deactivate user
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from forge.api.auth import verify_token, hash_password
from forge.core.db import get_conn, get_cursor, release_conn

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["admin"])


# Request/Response Models
class UserCreateRequest(BaseModel):
    username: str
    display_name: str
    password: str
    is_admin: bool = False


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    is_admin: bool
    is_active: bool


@router.post("/users", response_model=UserResponse)
async def create_user(
    request: UserCreateRequest,
    current_user: dict = Depends(verify_token)
) -> UserResponse:
    """Create a new user (admin only)."""

    try:
        # Check admin permission
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

        # Hash password
        password_hash = hash_password(request.password)

        conn = get_conn()
        try:
            with get_cursor(conn) as cursor:
                # Check if username exists
                cursor.execute(
                    "SELECT id FROM users WHERE username = %s",
                    (request.username,)
                )

                if cursor.fetchone():
                    raise HTTPException(status_code=409, detail="Username already exists")

                # Insert user
                cursor.execute("""
                    INSERT INTO users (username, display_name, password_hash, is_admin, is_active, created_at)
                    VALUES (%s, %s, %s, %s, TRUE, NOW())
                    RETURNING id, username, display_name, is_admin, is_active
                """, (request.username, request.display_name, password_hash, request.is_admin))

                row = cursor.fetchone()
                cursor.connection.commit()

                logger.info(f"User created: {request.username} by admin {current_user['username']}")

                return UserResponse(
                    id=row['id'],
                    username=row['username'],
                    display_name=row['display_name'],
                    is_admin=row['is_admin'],
                    is_active=row['is_active']
                )

        finally:
            release_conn(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Create user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: dict = Depends(verify_token)
) -> list[UserResponse]:
    """List all users (admin only)."""

    try:
        # Check admin permission
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

        conn = get_conn()
        try:
            with get_cursor(conn) as cursor:
                cursor.execute("""
                    SELECT id, username, display_name, is_admin, is_active
                    FROM users
                    ORDER BY created_at DESC
                """)

                users = []
                for row in cursor.fetchall():
                    users.append(UserResponse(
                        id=row['id'],
                        username=row['username'],
                        display_name=row['display_name'],
                        is_admin=row['is_admin'],
                        is_active=row['is_active']
                    ))

                logger.debug(f"Listed {len(users)} users")
                return users

        finally:
            release_conn(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"List users error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: int,
    current_user: dict = Depends(verify_token)
) -> dict:
    """Deactivate a user (admin only).

    Note: Not a hard delete, just marks is_active=FALSE.
    """

    try:
        # Check admin permission
        if not current_user.get("is_admin"):
            raise HTTPException(status_code=403, detail="Admin access required")

        # Prevent deactivating self
        if current_user["user_id"] == user_id:
            raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

        conn = get_conn()
        try:
            with get_cursor(conn) as cursor:
                # Check user exists
                cursor.execute(
                    "SELECT id, username FROM users WHERE id = %s",
                    (user_id,)
                )

                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="User not found")

                username = row['username']

                # Deactivate
                cursor.execute(
                    "UPDATE users SET is_active = FALSE WHERE id = %s",
                    (user_id,)
                )

                cursor.connection.commit()

                logger.info(f"User deactivated: {username} by admin {current_user['username']}")

                return {
                    "message": f"User {username} deactivated",
                    "user_id": user_id
                }

        finally:
            release_conn(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Deactivate user error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

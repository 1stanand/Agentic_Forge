"""
Settings API Routes

Endpoints:
- GET /settings/ — get user settings
- PUT /settings/ — update settings (jira_url, jira_pat)
- PUT /settings/profile — update profile (display_name)
- PUT /settings/password — change password
- POST /settings/test-jira — test JIRA connection
- POST /settings/test-model — test LLM model
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from forge.api.auth import verify_token, hash_password, verify_password, encrypt_pat, decrypt_pat
from forge.core.db import get_conn, get_cursor, release_conn
from forge.core.llm import get_llm, LLMNotLoadedError
from forge.infrastructure.jira_client import fetch_story

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


# Request/Response Models
class SettingsResponse(BaseModel):
    user_id: int
    username: str
    display_name: str
    jira_url: str
    jira_pat_configured: bool  # Never return actual PAT
    is_admin: bool


class ProfileUpdateRequest(BaseModel):
    display_name: str


class PasswordChangeRequest(BaseModel):
    current_password: str
    new_password: str


class SettingsUpdateRequest(BaseModel):
    jira_url: Optional[str] = None
    jira_pat: Optional[str] = None  # Plain text, will be encrypted before storage


class JiraTestRequest(BaseModel):
    jira_url: str
    jira_pat: str


class TestResultResponse(BaseModel):
    success: bool
    message: str


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    current_user: dict = Depends(verify_token)
) -> SettingsResponse:
    """Get current user settings."""

    try:
        user_id = current_user["user_id"]

        conn = get_conn()
        try:
            with get_cursor(conn) as cursor:
                cursor.execute("""
                    SELECT u.id, u.username, u.display_name, u.is_admin,
                           us.jira_url, us.jira_pat
                    FROM users u
                    LEFT JOIN user_settings us ON u.id = us.user_id
                    WHERE u.id = %s
                """, (user_id,))

                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="User not found")

                jira_pat_configured = bool(row['jira_pat'])  # jira_pat is not NULL

                return SettingsResponse(
                    user_id=row['id'],
                    username=row['username'],
                    display_name=row['display_name'] or "",
                    jira_url=row['jira_url'] or "",
                    jira_pat_configured=jira_pat_configured,
                    is_admin=row['is_admin']
                )

        finally:
            release_conn(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get settings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/", response_model=SettingsResponse)
async def update_settings(
    request: SettingsUpdateRequest,
    current_user: dict = Depends(verify_token)
) -> SettingsResponse:
    """Update user JIRA settings."""

    try:
        user_id = current_user["user_id"]

        conn = get_conn()
        try:
            with get_cursor(conn) as cursor:
                # Ensure user_settings row exists
                cursor.execute("""
                    INSERT INTO user_settings (user_id, updated_at)
                    VALUES (%s, NOW())
                    ON CONFLICT (user_id) DO NOTHING
                """, (user_id,))

                # Update JIRA settings
                if request.jira_url is not None or request.jira_pat is not None:
                    jira_url = request.jira_url
                    jira_pat_encrypted = None

                    if request.jira_pat:
                        # Encrypt PAT before storing
                        jira_pat_encrypted = encrypt_pat(request.jira_pat)

                    cursor.execute("""
                        UPDATE user_settings
                        SET jira_url = %s,
                            jira_pat = %s,
                            updated_at = NOW()
                        WHERE user_id = %s
                    """, (jira_url, jira_pat_encrypted, user_id))

                cursor.connection.commit()

                # Fetch and return updated settings
                cursor.execute("""
                    SELECT u.id, u.username, u.display_name, u.is_admin,
                           us.jira_url, us.jira_pat
                    FROM users u
                    LEFT JOIN user_settings us ON u.id = us.user_id
                    WHERE u.id = %s
                """, (user_id,))

                row = cursor.fetchone()
                jira_pat_configured = bool(row['jira_pat'])

                return SettingsResponse(
                    user_id=row['id'],
                    username=row['username'],
                    display_name=row['display_name'] or "",
                    jira_url=row['jira_url'] or "",
                    jira_pat_configured=jira_pat_configured,
                    is_admin=row['is_admin']
                )

        finally:
            release_conn(conn)

    except Exception as e:
        logger.error(f"Update settings error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/profile", response_model=SettingsResponse)
async def update_profile(
    request: ProfileUpdateRequest,
    current_user: dict = Depends(verify_token)
) -> SettingsResponse:
    """Update user profile (display name)."""

    try:
        user_id = current_user["user_id"]

        conn = get_conn()
        try:
            with get_cursor(conn) as cursor:
                cursor.execute("""
                    UPDATE users
                    SET display_name = %s
                    WHERE id = %s
                """, (request.display_name, user_id))

                cursor.connection.commit()

                # Fetch and return updated settings
                cursor.execute("""
                    SELECT u.id, u.username, u.display_name, u.is_admin,
                           us.jira_url, us.jira_pat
                    FROM users u
                    LEFT JOIN user_settings us ON u.id = us.user_id
                    WHERE u.id = %s
                """, (user_id,))

                row = cursor.fetchone()
                jira_pat_configured = bool(row['jira_pat'])

                return SettingsResponse(
                    user_id=row['id'],
                    username=row['username'],
                    display_name=row['display_name'] or "",
                    jira_url=row['jira_url'] or "",
                    jira_pat_configured=jira_pat_configured,
                    is_admin=row['is_admin']
                )

        finally:
            release_conn(conn)

    except Exception as e:
        logger.error(f"Update profile error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/password")
async def change_password(
    request: PasswordChangeRequest,
    current_user: dict = Depends(verify_token)
) -> dict:
    """Change user password."""

    try:
        user_id = current_user["user_id"]

        conn = get_conn()
        try:
            with get_cursor(conn) as cursor:
                # Get current password hash
                cursor.execute("SELECT password_hash FROM users WHERE id = %s", (user_id,))
                row = cursor.fetchone()
                if not row:
                    raise HTTPException(status_code=404, detail="User not found")

                # Verify current password
                if not verify_password(request.current_password, row['password_hash']):
                    raise HTTPException(status_code=401, detail="Incorrect current password")

                # Hash and store new password
                new_hash = hash_password(request.new_password)
                cursor.execute(
                    "UPDATE users SET password_hash = %s WHERE id = %s",
                    (new_hash, user_id)
                )

                cursor.connection.commit()

                return {"message": "Password changed successfully"}

        finally:
            release_conn(conn)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Change password error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test-jira", response_model=TestResultResponse)
async def test_jira_connection(
    request: JiraTestRequest,
    current_user: dict = Depends(verify_token)
) -> TestResultResponse:
    """Test JIRA connection with provided credentials."""

    try:
        # Try to fetch a story (simple test)
        # Use a dummy story ID just to test connectivity
        result = fetch_story(
            jira_input_mode="pat",
            jira_story_id="TEST",
            jira_pat_override=request.jira_pat
        )

        # If we got here without error, connection works (or story doesn't exist but API responded)
        if result.get("error"):
            return TestResultResponse(
                success=False,
                message=f"JIRA error: {result['error']}"
            )

        return TestResultResponse(
            success=True,
            message="JIRA connection successful"
        )

    except Exception as e:
        logger.warning(f"JIRA test failed: {e}")
        return TestResultResponse(
            success=False,
            message=f"JIRA connection failed: {str(e)}"
        )


@router.post("/test-model", response_model=TestResultResponse)
async def test_model_connection(
    current_user: dict = Depends(verify_token)
) -> TestResultResponse:
    """Test LLM model availability."""

    try:
        llm = get_llm()

        # Try a simple completion
        result = llm.create_completion(
            prompt="Say 'OK'",
            max_tokens=5
        )

        if result and result.get("choices"):
            return TestResultResponse(
                success=True,
                message="LLM model loaded and responding"
            )

        return TestResultResponse(
            success=False,
            message="LLM returned empty response"
        )

    except LLMNotLoadedError:
        return TestResultResponse(
            success=False,
            message="LLM model not loaded"
        )
    except Exception as e:
        logger.warning(f"Model test failed: {e}")
        return TestResultResponse(
            success=False,
            message=f"Model test failed: {str(e)}"
        )

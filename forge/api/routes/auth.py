import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from forge.api.models import LoginRequest, LoginResponse
from forge.api.auth import create_access_token, hash_password, verify_password, verify_token
from forge.core.db import get_conn, get_cursor, release_conn

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer()


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    print(f"[DEBUG] Login endpoint called")
    print(f"[DEBUG] Request: {request}")
    print(f"[DEBUG] Username: {request.username}, Password length: {len(request.password)}")

    logger.info(f"Login attempt: username={request.username}")
    conn = get_conn()
    print(f"[DEBUG] Connection obtained")

    try:
        with get_cursor(conn) as cursor:
            print(f"[DEBUG] Executing query for user: {request.username}")
            cursor.execute(
                "SELECT id, password_hash, display_name, is_admin FROM users WHERE username = %s AND is_active = TRUE",
                (request.username,)
            )
            user = cursor.fetchone()
            print(f"[DEBUG] Query result: {user is not None}")
            if user:
                print(f"[DEBUG] User found: {user['id']}, {user['display_name']}")
            logger.info(f"User lookup result: {user is not None}")

        if not user:
            print(f"[DEBUG] User not found!")
            logger.warning(f"User not found or inactive: {request.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")

        print(f"[DEBUG] Verifying password...")
        is_valid = verify_password(request.password, user['password_hash'])
        print(f"[DEBUG] Password verification result: {is_valid}")
        logger.info(f"Password verification: {is_valid}")

        if not is_valid:
            print(f"[DEBUG] Password invalid!")
            logger.warning(f"Password verification failed for user: {request.username}")
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token = create_access_token({
            "sub": str(user['id']),
            "user_id": user['id'],
            "username": request.username,
            "is_admin": user['is_admin']
        })

        return LoginResponse(
            access_token=token,
            token_type="bearer",
            display_name=user['display_name'],
            user_id=user['id'],
            is_admin=user['is_admin']
        )
    finally:
        release_conn(conn)


@router.post("/logout")
async def logout(credentials: HTTPAuthorizationCredentials = Depends(security)):
    payload = verify_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")
    return {"message": "Logged out"}

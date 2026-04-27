@echo off
REM Verify setup: paths, models, DB, tables
echo [VERIFY] Running setup verification...
cd /d %~dp0..\..\

echo.
echo Checking:
echo   - .env configuration
echo   - Database connectivity
echo   - Model files
echo   - FAISS indices
echo   - All required tables
echo.

python -m forge.scripts.verify_setup

if errorlevel 1 (
    echo.
    echo [ERROR] Verification failed. See output above.
    pause
    exit /b 1
)

echo.
echo [VERIFY] All checks passed!

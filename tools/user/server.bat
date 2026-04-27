@echo off
REM Start FastAPI development server
echo [SERVER] Starting Forge API server...
cd /d %~dp0..\..\

echo.
echo Server will start on http://localhost:8000
echo WebUI at http://localhost:8000/
echo API docs at http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python -m uvicorn forge.api.main:app --host 0.0.0.0 --port 8000 --reload

if errorlevel 1 (
    echo.
    echo [ERROR] Server failed to start. Check .env and dependencies.
    pause
)

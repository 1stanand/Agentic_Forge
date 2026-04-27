@echo off
REM Parse and index feature repository
echo [PARSE] Indexing feature repository...
cd /d %~dp0..\..\

echo.
echo Options:
echo   [no args]  - Incremental index (only new/changed files)
echo   --full-rebuild - Full rebuild (drop and recreate all)
echo.

if "%1"=="--full-rebuild" (
    echo Running full rebuild...
    python -m forge.scripts.index_repo --full-rebuild
) else (
    echo Running incremental index...
    python -m forge.scripts.index_repo
)

if errorlevel 1 (
    echo.
    echo [ERROR] Indexing failed. Check FEATURES_REPO_PATH in .env
    pause
    exit /b 1
)

echo.
echo [PARSE] Complete!
echo Verify: SELECT count(*) FROM features; SELECT count(*) FROM unique_steps;

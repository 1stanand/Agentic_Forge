@echo off
REM Full rebuild: DB, index_repo, FAISS indices, knowledge base
echo [REBUILD] Starting full rebuild...
cd /d %~dp0..\..\

echo.
echo [1/5] Setting up database...
python -m forge.scripts.setup_db || goto error

echo.
echo [2/5] Indexing feature repository...
python -m forge.scripts.index_repo --full-rebuild || goto error

echo.
echo [3/5] Building step FAISS index...
python -m forge.scripts.build_step_index || goto error

echo.
echo [4/5] Building CAS knowledge base...
python -m forge.scripts.build_knowledge || goto error

echo.
echo [5/5] Verifying setup...
python -m forge.scripts.verify_setup || goto error

echo.
echo [REBUILD] Complete!
exit /b 0

:error
echo.
echo [ERROR] Rebuild failed at step above. Check output for details.
exit /b 1

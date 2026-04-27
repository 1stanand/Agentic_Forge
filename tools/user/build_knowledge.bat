@echo off
REM Build module knowledge wiki from seed taxonomy + PDFs.
REM Usage: build_knowledge.bat [--module cas] [--rebuild]

echo [BUILD-KNOWLEDGE] Starting...
cd /d %~dp0..\..\

python -m forge.scripts.build_knowledge --module cas %*

if errorlevel 1 (
    echo [BUILD-KNOWLEDGE] FAILED
    pause
    exit /b 1
)

echo [BUILD-KNOWLEDGE] Done
exit /b 0

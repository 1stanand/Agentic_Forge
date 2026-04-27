@echo off
REM Run comprehensive acceptance test suite
echo [TESTS] Running acceptance test suite...
cd /d %~dp0..\..\

echo.
echo Running all test categories:
echo   - Unit tests
echo   - Integration tests
echo   - Acceptance tests
echo.

python -m pytest tests/ -v --tb=short

if errorlevel 1 (
    echo.
    echo [ERROR] Tests failed. See output above.
    pause
    exit /b 1
)

echo.
echo [TESTS] All tests passed!

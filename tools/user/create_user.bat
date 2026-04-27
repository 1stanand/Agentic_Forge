@echo off
REM Create a new user
echo [CREATE_USER] Interactive user creation
cd /d %~dp0..\..\

echo.
echo Usage: create_user.bat [--username NAME] [--display "DISPLAY NAME"] [--admin]
echo.
echo Examples:
echo   create_user.bat --username anand --display "Anand Singh" --admin
echo   create_user.bat --username qa_user --display "QA User"
echo.

python -m forge.scripts.create_user %*

if errorlevel 1 (
    echo.
    echo [ERROR] User creation failed.
    pause
    exit /b 1
)

echo.
echo [CREATE_USER] Complete!

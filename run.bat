@echo off
REM 3x3 Speed Cube Timer - Windows Launcher
REM Auto-creates a virtual environment and launches the app.

setlocal enabledelayedexpansion

cd /d "%~dp0"

set VENV_DIR=%~dp0.venv

if not exist "%VENV_DIR%\Scripts\python.exe" (
    echo [3x3 Timer] Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to create virtual environment. Make sure Python 3.10+ is installed.
        pause
        exit /b 1
    )
    echo [3x3 Timer] Installing dependencies...
    "%VENV_DIR%\Scripts\python.exe" -m pip install -e . >nul 2>&1
    if !errorlevel! neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo [3x3 Timer] Starting application...
"%VENV_DIR%\Scripts\python.exe" run.py
if !errorlevel! neq 0 (
    echo [ERROR] Application exited with an error.
    pause
    exit /b 1
)

pause
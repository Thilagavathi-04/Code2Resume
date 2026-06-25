@echo off
REM Navigate to project root
cd /d "%~dp0.."

REM Configure uv to use 'env' directory
set UV_PROJECT_ENVIRONMENT=env

REM Run the application using uv
REM This will automatically create the venv and install dependencies if needed
uv run python -m backend.app
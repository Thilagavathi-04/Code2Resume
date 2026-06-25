@echo off
REM Start Full Stack Application
REM This script starts both the FastAPI backend and React frontend

cd /d "%~dp0\.."

echo ================================================
echo    Starting Code2Resume Full Stack Application
echo ================================================
echo.
echo Backend API: http://localhost:8001
echo Frontend: http://localhost:5173
echo.

REM Start Backend in new window
echo Starting FastAPI Backend...
start "Code2Resume Backend" cmd /k "uv run uvicorn backend.app:app --host 0.0.0.0 --port 8001 --reload"

REM Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

REM Start Frontend in new window
echo Starting React Frontend...
start "Code2Resume Frontend" cmd /k "cd frontend-react && npm run dev"

echo.
echo ================================================
echo    Application is running!
echo ================================================
echo Backend API: http://localhost:8001
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8001/docs
echo.
echo Close the terminal windows to stop the servers
echo.
pause

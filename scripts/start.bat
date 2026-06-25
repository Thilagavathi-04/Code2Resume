@echo off
REM Code2Resume Startup Script with Database Check
echo 🚀 Starting Code2Resume...

REM Navigate to project root
cd /d "%~dp0.."

REM Check if virtual environment exists
if not exist "env" (
    echo ❌ Virtual environment not found. Please run scripts\setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
call env\Scripts\activate.bat

REM Check if database exists
if not exist "users.db" (
    echo 📦 Database not found. Initializing...
    python scripts\init_db.py
    if %ERRORLEVEL% neq 0 (
        echo ❌ Database initialization failed!
        pause
        exit /b 1
    )
) else (
    echo ✓ Database found
)

REM Verify database schema
echo 🔍 Verifying database schema...
python tests\test_db.py
if %ERRORLEVEL% neq 0 (
    echo ⚠️  Database schema mismatch detected!
    
    :ask_reset
    set /p "response=Reset database? (yes/no): "
    if /i "%response%"=="yes" (
        echo 🔄 Resetting database...
        python scripts\init_db.py
        python tests\test_db.py
    ) else if /i "%response%"=="no" (
        echo ❌ Cannot continue with invalid schema
        pause
        exit /b 1
    ) else (
        goto ask_reset
    )
)

REM Start the server
echo.
echo ✨ Starting FastAPI server...
echo 🌐 Server will be available at: http://localhost:8001
echo 📝 Login page: http://localhost:8001/
echo 📝 Register page: http://localhost:8001/register
echo.
echo Press CTRL+C to stop the server
echo ─────────────────────────────────────────────────────

python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8001
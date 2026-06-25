@echo off
REM Code2Resume Setup Script
echo 🚀 Setting up Code2Resume with uv...

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ uv is not installed. Please install it: https://github.com/astral-sh/uv
    echo    Visit: https://github.com/astral-sh/uv#installation and follow Windows instructions
    pause
    exit /b 1
)

echo ✅ uv detected

REM Configure uv to use 'env' directory
set UV_PROJECT_ENVIRONMENT=env

REM Install Python dependencies
echo 📥 Installing Python dependencies...
uv sync

echo ✅ Setup complete! Run ..\run.bat to start the app.

REM Change to backend directory to check Ollama
cd ..\backend

REM Check if Ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Ollama is not installed. Please install Ollama first:
    echo    Visit: https://ollama.ai
    echo    Download and install Ollama for Windows
    pause
    exit /b 1
)
echo ✅ Ollama detected

REM Check if Ollama service is running
curl -s http://localhost:11434/api/version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo 🔄 Starting Ollama service...
    start /b ollama serve
    timeout /t 3 /nobreak >nul
    
    curl -s http://localhost:11434/api/version >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        echo ❌ Failed to start Ollama service
        echo Please try running: ollama serve
        pause
        exit /b 1
    )
)
echo ✅ Ollama service is running

REM Check if default model exists
echo 🔍 Checking for required models...
ollama list | findstr "gemma2:9b" >nul
if %ERRORLEVEL% neq 0 (
    echo 📥 Pulling gemma2:9b model...
    echo This may take several minutes...
    ollama pull gemma2:9b
    if %ERRORLEVEL% neq 0 (
        echo ⚠️ Failed to pull gemma2:9b, trying fallback model...
        ollama pull llama3.1:8b
    )
) else (
    echo ✅ gemma2:9b model found
)

echo.
echo 🎉 Setup completed successfully!
echo.
echo To start the application:
echo   1. Run: ..\run.bat
echo   2. Open browser: http://localhost:8000
echo.
pause
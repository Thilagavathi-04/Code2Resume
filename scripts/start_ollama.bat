@echo off
REM Script to start Ollama and ensure qwen2.5-coder:3b model is available

echo 🚀 Starting Ollama service...

REM Check if Ollama is installed
where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ Ollama is not installed!
    echo Please install it from: https://ollama.ai
    pause
    exit /b 1
)

REM Check if Ollama service is running by trying to connect
curl -s http://localhost:11434/api/version >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Starting Ollama server...
    start /b ollama serve
    timeout /t 3 /nobreak >nul
    
    REM Wait for service to be ready
    :wait_for_ollama
    curl -s http://localhost:11434/api/version >nul 2>nul
    if %ERRORLEVEL% neq 0 (
        timeout /t 1 /nobreak >nul
        goto wait_for_ollama
    )
    echo ✅ Ollama server started
) else (
    echo ✅ Ollama server is already running
)

REM Check if model exists
echo 🔍 Checking for qwen2.5-coder:3b model...
ollama list | findstr "qwen2.5-coder:3b" >nul
if %ERRORLEVEL%==0 (
    echo ✅ Model qwen2.5-coder:3b is already available
) else (
    echo 📥 Model not found. Pulling qwen2.5-coder:3b...
    echo This may take a few minutes depending on your internet speed...
    ollama pull qwen2.5-coder:3b
    
    if %ERRORLEVEL%==0 (
        echo ✅ Model qwen2.5-coder:3b pulled successfully!
    ) else (
        echo ❌ Failed to pull model
        pause
        exit /b 1
    )
)

echo.
echo 🎉 Ollama is ready!
echo Model available: qwen2.5-coder:3b
echo Server running at: http://localhost:11434
echo.
pause
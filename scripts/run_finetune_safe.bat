@echo off
echo 🧹 Preparing GPU for Fine-tuning
echo ================================
echo.

REM Check if nvidia-smi is available
where nvidia-smi >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ NVIDIA GPU not detected or drivers not installed
    echo Please ensure you have:
    echo   1. NVIDIA GPU
    echo   2. Latest NVIDIA drivers
    echo   3. nvidia-smi in PATH
    pause
    exit /b 1
)

REM Check current GPU usage
echo Current GPU Memory Usage:
for /f "skip=1 tokens=1,2" %%a in ('nvidia-smi --query-gpu^=memory.used^,memory.total --format^=csv^,noheader^,nounits') do (
    set USED=%%a
    set TOTAL=%%b
)

echo Used: %USED%MB / %TOTAL%MB
echo.

if %USED% gtr 1000 (
    echo ⚠️  High GPU memory usage detected!
    echo.
    echo Recommendations to free up VRAM:
    echo   1. Close web browsers ^(especially Chrome/Edge/Firefox^)
    echo   2. Close other GPU applications
    echo   3. Restart if needed
    echo.
    echo Current GPU processes:
    nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv
    echo.
    
    :ask_continue
    set /p "continue=Try to continue anyway? (y/n): "
    if /i "%continue%"=="n" (
        echo Exiting...
        exit /b 1
    )
    if /i not "%continue%"=="y" (
        goto ask_continue
    )
)

echo 🚀 GPU memory looks good. Starting fine-tuning...
echo.

REM Activate environment
if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
) else (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Check CUDA availability
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"

echo.
echo Starting fine-tuning with background logging...
python fine_tune.py > finetune_run.log 2>&1

if %ERRORLEVEL%==0 (
    echo.
    echo ✅ Fine-tuning completed successfully!
    echo.
    echo 📁 Model saved to: .\lora_model
    echo.
    echo Next steps to use with Ollama:
    echo   1. Merge LoRA weights: python merge_lora.py
    echo   2. Create Modelfile: Use Modelfile_resume template
    echo   3. Build Ollama model: ollama create resume:latest -f Modelfile_resume
) else (
    echo ❌ Fine-tuning failed! Check finetune_run.log for details
)

echo.
pause
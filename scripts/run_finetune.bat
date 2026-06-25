@echo off
echo 🚀 Starting Qwen2.5-Coder-3B Fine-tuning
echo ========================================
echo.
echo ⚠️  Important Notes:
echo   - This will use your GPU
echo   - Expected time: 15-30 minutes
echo   - Memory usage: ~3.5GB VRAM
echo.
pause

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
echo Starting fine-tuning...
python fine_tune.py

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
    echo ❌ Fine-tuning failed!
)

echo.
pause
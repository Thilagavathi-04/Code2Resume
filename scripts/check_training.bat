@echo off
echo 📊 Fine-tuning Progress Monitor
echo ================================
echo.

set LOG_FILE=finetune_run.log

if not exist "%LOG_FILE%" (
    echo ❌ Log file not found: %LOG_FILE%
    echo Make sure fine-tuning is running
    pause
    exit /b 1
)

echo Recent output:
echo ---
REM Show last 30 lines of log file (Windows equivalent of tail -30)
powershell "Get-Content '%LOG_FILE%' | Select-Object -Last 30"
echo ---
echo.

REM Extract training steps if available
for /f "delims=" %%i in ('findstr "Step [0-9]*/60" "%LOG_FILE%"') do set STEPS=%%i
if defined STEPS (
    echo Current: %STEPS%
)

REM Check for completion
findstr /c:"Fine-tuning complete" "%LOG_FILE%" >nul
if %ERRORLEVEL%==0 (
    echo ✅ Training completed!
    goto :end
)

findstr /c:"Error" /c:"Traceback" /c:"Failed" "%LOG_FILE%" >nul
if %ERRORLEVEL%==0 (
    echo ❌ Error detected in training!
    goto :end
)

echo 🔄 Training in progress...

:end
echo.
echo Press any key to refresh, Ctrl+C to exit
pause >nul
goto :eof
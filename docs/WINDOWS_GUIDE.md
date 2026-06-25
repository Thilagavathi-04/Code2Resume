# Windows Setup Guide - Code2Resume

## 🚀 Getting Started on Windows

This project now includes Windows batch files (`.bat`) that provide the same functionality as the original shell scripts (`.sh`). 

### 📦 Prerequisites

1. **Python 3.8+** - Download from [python.org](https://python.org)
2. **Git** - Download from [git-scm.com](https://git-scm.com)
3. **uv** - Python package manager
   - Visit: https://github.com/astral-sh/uv#installation
   - Follow Windows installation instructions
4. **Ollama** - Local LLM server
   - Download from: https://ollama.ai
   - Install the Windows version

### 📁 Available Windows Scripts

| Batch File | Shell Equivalent | Purpose |
|------------|------------------|---------|
| `Scrpts\setup.bat` | `Scrpts/setup.sh` | Initial project setup and dependency installation |
| `Scrpts\start.bat` | `Scrpts/start.sh` | Start the application with database checks |
| `run.bat` | `run.sh` | Quick application startup |
| `start_ollama.bat` | `start_ollama.sh` | Start Ollama service and download models |
| `install_finetune_deps.bat` | `install_finetune_deps.sh` | Install fine-tuning dependencies |
| `run_finetune.bat` | `run_finetune.sh` | Start model fine-tuning |
| `run_finetune_safe.bat` | `run_finetune_safe.sh` | Safe fine-tuning with GPU memory checks |
| `check_training.bat` | `check_training.sh` | Monitor fine-tuning progress |

## 🎯 Quick Start (Windows)

### Step 1: Initial Setup
```cmd
REM Clone the repository
git clone <repository-url>
cd Code2Resume

REM Run the setup script
Scrpts\setup.bat
```

### Step 2: Start Ollama (First Time)
```cmd
start_ollama.bat
```

### Step 3: Start the Application
```cmd
REM Option 1: Full startup with database checks (recommended)
Scrpts\start.bat

REM Option 2: Quick startup
run.bat
```

### Step 4: Access the Application
- **Main App**: http://localhost:8001/
- **Register**: http://localhost:8001/register
- **Dashboard**: http://localhost:8001/dashboard

## 🤖 Fine-tuning on Windows

### Install Fine-tuning Dependencies
```cmd
install_finetune_deps.bat
```

### Run Fine-tuning (Safe Mode - Recommended)
```cmd
run_finetune_safe.bat
```

### Monitor Training Progress
```cmd
check_training.bat
```

## 🛠️ Windows-Specific Features

### GPU Memory Monitoring
The Windows batch files include GPU memory monitoring using `nvidia-smi`:
- Checks available VRAM before fine-tuning
- Warns if GPU memory usage is high
- Provides recommendations to free up memory

### Error Handling
- Proper exit codes and error messages
- Pause commands for better user experience
- Clear instructions when dependencies are missing

### Path Handling
- Uses Windows path separators (`\` instead of `/`)
- Handles spaces in file paths correctly
- Uses Windows-specific commands (`where` instead of `command -v`)

## ❌ Troubleshooting Windows Issues

### "uv is not recognized"
```cmd
REM Install uv using PowerShell (run as Administrator)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### "ollama is not recognized"
1. Download Ollama from https://ollama.ai
2. Install the Windows version
3. Restart your command prompt

### "nvidia-smi is not recognized"
1. Update NVIDIA drivers from nvidia.com
2. Ensure CUDA is installed
3. Add NVIDIA tools to PATH

### Virtual Environment Issues
```cmd
REM If virtual environment fails to activate
pip install virtualenv
python -m venv env
env\Scripts\activate.bat
```

## 📋 Command Reference

### Database Management
```cmd
REM Initialize database
python init_db.py

REM Test database
python test_db.py

REM Reset database (delete users.db first)
del users.db
python init_db.py
```

### Ollama Management
```cmd
REM Check Ollama status
ollama list

REM Pull specific model
ollama pull qwen2.5-coder:3b

REM Start Ollama service manually
ollama serve
```

## 🔄 Migration from Linux/macOS

If you're moving from Linux/macOS to Windows:

1. **Dependencies**: All Python dependencies remain the same
2. **Scripts**: Use `.bat` files instead of `.sh` files
3. **Paths**: The project structure is identical
4. **Database**: SQLite database files are cross-platform compatible

## 🎉 Success Indicators

You'll know everything is working when you see:
- ✅ Virtual environment activated
- ✅ Database schema verified  
- ✅ Ollama service running
- ✅ FastAPI server started
- 🌐 Server available at http://localhost:8001

## 💡 Tips for Windows Users

1. **Run as Administrator** if you encounter permission issues
2. **Windows Defender** might flag some operations - add project folder to exclusions
3. **Use Command Prompt or PowerShell** - avoid Git Bash for batch files
4. **GPU Drivers** must be up-to-date for fine-tuning features
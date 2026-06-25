# Project Structure

## 📁 New Directory Organization

```
Code2Resume/
├── backend/              # Main application backend
│   ├── config/          # Configuration settings
│   ├── models/          # Data models and LLM handlers
│   └── services/        # Business logic services
│
├── frontend/            # Web interface
│   ├── static/         # CSS, JavaScript, assets
│   └── template/       # HTML templates
│
├── scripts/            # All executable scripts
│   ├── *.sh           # Linux/Mac shell scripts
│   ├── *.bat          # Windows batch scripts
│   └── init_db.py     # Database initialization
│
├── fine-tuning/        # Model fine-tuning
│   ├── configs/       # Fine-tuning configurations
│   ├── scripts/       # Fine-tuning Python scripts
│   ├── Modelfile      # Ollama model configuration
│   └── combined_train.jsonl  # Combined training data
│
├── data/               # All data files
│   ├── Git_details/   # User GitHub data
│   ├── resumes/       # Generated resume files
│   ├── outputs/       # Training outputs/checkpoints
│   ├── lora_model/    # Fine-tuned LoRA adapters
│   ├── LateX_template/  # Resume LaTeX templates
│   └── fonts/         # Font files
│
├── docs/              # Documentation
│   ├── FINETUNING_GUIDE.md
│   ├── SETUP_GUIDE.md
│   └── WINDOWS_GUIDE.md
│
├── tests/             # Test files
│   ├── test_db.py
│   ├── test_app.py
│   └── validate_system.py
│
└── Root Files         # Configuration only
    ├── pyproject.toml
    ├── README.md
    └── index.html
```

## 🔄 What Changed

### Files Moved

1. **Scripts consolidated to `scripts/`**:
   - All `.sh` and `.bat` files from Scrpts/ → scripts/
   - init_db.py → scripts/

2. **Fine-tuning files to `fine-tuning/scripts/`**:
   - fine_tune.py
   - merge_lora.py
   - check_finetune_ready.py
   - test_formatting.py

3. **Documentation to `docs/`**:
   - FINETUNING_GUIDE.md
   - SETUP_GUIDE.md
   - WINDOWS_GUIDE.md

4. **Frontend files to `frontend/`**:
   - static/ → frontend/static/
   - template/ → frontend/template/

5. **Data files to `data/`**:
   - Git_details/ → data/Git_details/
   - resumes/ → data/resumes/
   - outputs/ → data/outputs/
   - lora_model/ → data/lora_model/
   - LateX_template/ → data/LateX_template/
   - fonts/ → data/fonts/

6. **Test files to `tests/`**:
   - Test_files/* → tests/

### Code Updates

All file path references have been updated in:

- **backend/app.py**: Updated paths for static, template, resumes, Git_details
- **backend/fine_tune_service.py**: Updated Git_details path
- **backend/services/agent_service.py**: Updated LateX_template path
- **fine-tuning/scripts/fine_tune.py**: Updated data paths (relative to new location)
- **fine-tuning/scripts/merge_lora.py**: Updated model paths
- **scripts/*.sh**: Updated to navigate to project root and use correct paths
- **scripts/*.bat**: Updated Windows batch scripts for new structure

## 🚀 How to Run

### Starting the Application

**Linux/Mac:**
```bash
cd /path/to/Code2Resume
./scripts/start.sh
```

**Windows:**
```cmd
cd C:\path\to\Code2Resume
scripts\start.bat
```

### Running Fine-tuning

**Linux/Mac:**
```bash
cd /path/to/Code2Resume
./scripts/run_finetune.sh
```

**Windows:**
```cmd
cd C:\path\to\Code2Resume
scripts\run_finetune.bat
```

### Database Initialization

**Linux/Mac:**
```bash
python scripts/init_db.py
```

**Windows:**
```cmd
python scripts\init_db.py
```

## ✅ Benefits of New Structure

1. **Cleaner Root**: Only essential config files in root directory
2. **Better Organization**: Related files grouped together
3. **Easier Navigation**: Clear separation of concerns
4. **Scalability**: Easy to add new features in appropriate folders
5. **Professional**: Industry-standard project structure

## 📝 Notes

- All scripts automatically navigate to project root, so they work from anywhere
- Data files are isolated in `data/` for easy backup/gitignore
- Frontend and backend are clearly separated
- Documentation is centralized in `docs/`
- Tests are organized in `tests/`

## 🔧 Developer Tips

- Run scripts from project root or use the scripts in `scripts/` folder
- Fine-tuning outputs go to `data/outputs/`
- Generated resumes are saved to `data/resumes/`
- User GitHub data is stored in `data/Git_details/{username}/`
- HTML templates are in `frontend/template/`
- Static assets (CSS, JS) are in `frontend/static/`

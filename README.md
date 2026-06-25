# Code2Resume

> Transform GitHub Profiles into AI-Powered, Domain-Specific Resumes

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=flat-square&logo=react&logoColor=black)](https://react.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)](https://tailwindcss.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](https://opensource.org/licenses/MIT)

---

## What is Code2Resume?

Code2Resume is a **privacy-first AI system** that analyzes your GitHub repositories and generates professional LaTeX resumes tailored to specific job roles. All processing happens locally on your machine using Llama 3.1.

### Key Features

| Feature | Description |
|---------|-------------|
| 🔍 **GitHub Analysis** | Automatically fetches and analyzes your repositories |
| 🤖 **AI-Powered** | Uses Llama 3.1 for intelligent project analysis |
| 📊 **Domain Classification** | Categorizes projects (ML, Full Stack, DevOps, etc.) |
| 💬 **Streaming Chat** | Real-time AI assistant with markdown support |
| 📄 **LaTeX Resumes** | Generates professional, downloadable .tex files |
| 🔒 **Privacy First** | All data stays on your machine |

---

## Why Code2Resume?

### vs. Manual Resume Writing

| Aspect | Manual | Code2Resume |
|--------|--------|-------------|
| Time | 8+ hours | 15 minutes |
| Accuracy | Manual recall | AI-extracted from code |
| Consistency | Hard to maintain | Always up-to-date |
| Domain Focus | Generic | Tailored to role |

### vs. Cloud AI Tools

| Aspect | Cloud Tools | Code2Resume |
|--------|-------------|-------------|
| Privacy | Data sent to servers | Everything local |
| Cost | API fees | Free |
| Customization | Limited | Fine-tune on your data |
| Internet | Required | Works offline |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend                              │
│  React 19 + Tailwind CSS 4 + Zustand                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Login     │  │  Dashboard  │  │   Resumes   │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend (FastAPI)                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │  Auth       │  │  Analysis   │  │  Resume Gen │          │
│  │  (JWT)      │  │  (Background)│  │  (RAG)      │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│   GitHub API    │ │   Ollama +      │ │   ChromaDB      │
│                 │ │   Llama 3.1     │ │   (Vector DB)   │
└─────────────────┘ └─────────────────┘ └─────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | React 19, Tailwind CSS 4, Zustand | UI components, styling, state management |
| **Backend** | FastAPI, SQLAlchemy, JWT | API server, database, authentication |
| **AI/ML** | Ollama, Llama 3.1, SentenceTransformers | LLM inference, embeddings |
| **Database** | ChromaDB, SQLite | Vector search, user data |
| **DevOps** | uv, Vite, npm | Package management, build tools |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+
- Ollama installed ([ollama.ai](https://ollama.ai))
- NVIDIA GPU (optional but recommended for performance)

### Installation

```bash
# Clone repository
git clone https://github.com/Mithrajith/Code2Resume.git
cd Code2Resume

# Install backend dependencies
uv sync

# Install frontend dependencies
cd frontend-react && npm install && cd ..

# Pull Llama 3.1 model
ollama pull llama3.1:8b

# Start the application
./scripts/run.sh
```

### Environment Variables

```bash
cp .env.example .env
```

```env
SECRET_KEY=your-secret-key-here
OLLAMA_HOST=http://localhost:11434
```

---

## Usage

1. **Register** with your GitHub credentials
2. **Analyze** your GitHub profile (click "Update from GitHub")
3. **Chat** with the AI about your projects
4. **Generate** domain-specific resumes
5. **Download** LaTeX files and compile with Overleaf

### Example Commands

- "List all my ML projects"
- "Generate machine learning engineer resume"
- "Show my tech stack"
- "What are my best projects?"

---

## API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/auth/register` | POST | Register new user |
| `/auth/login` | POST | Login and get JWT |
| `/auth/me` | GET | Get current user |
| `/auth/me` | PUT | Update user profile |

### Core Features

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/analyze` | POST | Start GitHub analysis |
| `/analysis-status/{job_id}` | GET | Check analysis progress |
| `/ask` | POST | Chat with AI (sync) |
| `/ask/stream` | POST | Chat with AI (streaming) |
| `/generate-resume` | POST | Generate LaTeX resume |
| `/resumes` | GET | List generated resumes |
| `/download-resume/{filename}` | GET | Download resume file |
| `/delete-resume/{filename}` | DELETE | Delete resume file |

### System

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/gpu-status` | GET | GPU information |

---

## Development

### Project Structure

```
Code2Resume/
├── backend/                 # FastAPI application
│   ├── app.py              # Main application
│   ├── database.py         # Database setup
│   ├── models/             # SQLAlchemy models
│   └── services/           # Business logic
│       ├── agent_service.py
│       ├── rag_service.py
│       └── github_service.py
├── frontend-react/         # React frontend
│   ├── src/
│   │   ├── api/            # API layer
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   └── store/          # Zustand stores
│   └── package.json
├── scripts/                # Startup scripts
├── data/                   # User data, models
├── docs/                   # Documentation
└── pyproject.toml          # Python dependencies
```

### Running in Development

```bash
# Terminal 1: Backend
./scripts/start.sh

# Terminal 2: Frontend
cd frontend-react && npm run dev
```

### Available Scripts

| Script | Description |
|--------|-------------|
| `./scripts/run.sh` | Start both backend and frontend |
| `./scripts/start.sh` | Start backend only |
| `./scripts/start-react.sh` | Start frontend only |
| `./scripts/setup.sh` | Initial project setup |

---

## Advantages

1. **Complete Privacy**: All processing happens locally, no cloud dependency
2. **Domain-Specific**: Automatically tailors resumes to job roles (ML, Full Stack, DevOps, etc.)
3. **RAG-Powered**: Uses your actual project data, no hallucination
4. **Streaming Chat**: Real-time AI assistance with markdown support
5. **Fine-Tuning Ready**: Train on your own data for better results
6. **LaTeX Output**: Professional, ATS-friendly resumes
7. **Open Source**: Free to use and modify

---

## Limitations

1. **GPU Required**: Optimal performance needs NVIDIA GPU (4GB+ VRAM)
2. **Model Size**: Llama 3.1:8b requires ~5GB disk space
3. **Rate Limits**: GitHub API has rate limits (5000 req/hour for authenticated users)
4. **Single User**: Currently designed for single-user local use
5. **No PDF Direct**: Generates .tex files, requires Overleaf or local LaTeX for PDF compilation

---

## Roadmap

- [ ] Docker containerization
- [ ] Multi-user support with PostgreSQL
- [ ] PDF generation integration
- [ ] ATS score analysis
- [ ] LinkedIn integration
- [ ] Template gallery with multiple styles
- [ ] Real-time collaboration
- [ ] Mobile responsive improvements

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Code Style

- **Python**: Follow PEP 8, use `black` formatter
- **JavaScript/React**: Follow ESLint rules, use functional components
- **Commits**: Use conventional commits format

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Ollama](https://ollama.ai/) - Local LLM server
- [Meta AI](https://llama.meta.com/) - Llama 3.1 model
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Unsloth](https://unsloth.ai/) - Efficient fine-tuning
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Tailwind CSS](https://tailwindcss.com/) - Utility-first CSS framework


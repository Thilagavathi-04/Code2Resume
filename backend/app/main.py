from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.auth import router as auth_router
from app.api.users import router as users_router
from app.api.resumes import router as resumes_router
from app.api.jobs import router as jobs_router
from app.api.interviews import router as interviews_router
from app.api.skill_gap import router as skill_gap_router
from app.api.v1_compat import router as v1_router

app = FastAPI(
    title="Code2Resume API v2",
    version=settings.APP_VERSION,
    description="AI-powered resume builder backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v2")
app.include_router(auth_router)
app.include_router(users_router, prefix="/api/v2")
app.include_router(resumes_router, prefix="/api/v2")
app.include_router(jobs_router, prefix="/api/v2")
app.include_router(interviews_router, prefix="/api/v2")
app.include_router(skill_gap_router, prefix="/api/v2")
app.include_router(v1_router)


@app.on_event("startup")
async def on_startup():
    await init_db()

    print(f"[startup] Using model: {settings.DEFAULT_MODEL} (timeout: {settings.LLM_TIMEOUT}s)")

    import ollama as _ollama
    try:
        _ollama.list()
        print("[startup] Ollama connection OK")
    except Exception as e:
        print(f"[startup] WARNING: Ollama is not reachable: {e}")
        print("[startup] Resume generation will fail until ollama is started (ollama serve)")

    try:
        from services.rag_service import RAGService
        rag = RAGService()
        rag._ensure_init()
        print("[startup] RAG service initialized")
    except Exception as e:
        print(f"[startup] WARNING: RAG init failed: {e}")


@app.get("/health")
async def health_check():
    import ollama as _ollama
    ollama_ok = False
    try:
        _ollama.list()
        ollama_ok = True
    except Exception:
        pass
    return {
        "status": "ok" if ollama_ok else "degraded",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "ollama": "connected" if ollama_ok else "disconnected",
    }

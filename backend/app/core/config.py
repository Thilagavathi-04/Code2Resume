from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Code2Resume"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    DATABASE_URL: str = ""
    DATABASE_ECHO: bool = False
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    OLLAMA_HOST: str = ""
    OLLAMA_BASE_URL: str = ""
    OLLAMA_MODEL: str = ""
    LLM_TIMEOUT: int = 180
    DEFAULT_MODEL: str = ""
    FALLBACK_MODEL: str = ""
    MAX_TOKENS: int = 1000
    TEMPERATURE: float = 0.7

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.0-flash"

    MAX_BULLET_POINTS: int = 5
    MIN_BULLET_POINTS: int = 3

    GITHUB_API_BASE: str = "https://api.github.com"
    GITHUB_TOKEN: Optional[str] = None

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"

    RETRIEVAL_BM25_WEIGHT: float = 0.4
    RETRIEVAL_EMBEDDING_WEIGHT: float = 0.4
    RETRIEVAL_METADATA_WEIGHT: float = 0.1
    RETRIEVAL_QUALITY_WEIGHT: float = 0.1
    RETRIEVAL_SIMILARITY_THRESHOLD: float = 0.72
    RETRIEVAL_TOP_N: int = 20
    RETRIEVAL_TOP_K: int = 5
    RERANKER_MODEL: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    KNOWLEDGE_GRAPH_PATH: str = "data/knowledge_graphs"
    MAX_CONTEXT_TOKENS: int = 4000
    TOKENIZER_MODEL: str = "cl100k_base"

    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8001",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()

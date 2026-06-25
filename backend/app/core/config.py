from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    APP_NAME: str = "Code2Resume"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+asyncpg://zypher:3066@localhost:5432/code2resume"
    DATABASE_ECHO: bool = False

    SECRET_KEY: str = "your-secret-key-keep-it-secret"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    GITHUB_API_BASE: str = "https://api.github.com"
    OLLAMA_HOST: str = "http://localhost:11434"
    DEFAULT_MODEL: str = "mistral:latest"
    FALLBACK_MODEL: str = "llama3.1:8b"

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-3.5-turbo"

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

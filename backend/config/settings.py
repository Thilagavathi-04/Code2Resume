import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
project_root = Path(__file__).parent.parent.parent
env_file = project_root / ".env"

if env_file.exists():
    load_dotenv(env_file)

class Settings:
    """Application settings loaded from environment variables with fallbacks"""
    
    def __init__(self):
        # Server Configuration
        self.host = os.getenv("HOST", "127.0.0.1")
        self.port = int(os.getenv("PORT", "8000"))
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # Ollama Configuration
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.default_model = os.getenv("DEFAULT_MODEL", "gemma2:9b")
        self.fallback_model = os.getenv("FALLBACK_MODEL", "llama3.1:8b")
        
        # OpenAI Configuration (Fallback)
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.openai_model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
        self.openai_fallback_model = os.getenv("OPENAI_FALLBACK_MODEL", "gpt-3.5-turbo-16k")
        
        # GitHub API Configuration
        self.github_api_base = os.getenv("GITHUB_API_BASE", "https://api.github.com")
        self.github_token = os.getenv("GITHUB_TOKEN")
        
        # Generation Configuration
        self.max_bullet_points = int(os.getenv("MAX_BULLET_POINTS", "10"))
        self.min_bullet_points = int(os.getenv("MIN_BULLET_POINTS", "5"))
        self.max_tokens = int(os.getenv("MAX_TOKENS", "10000"))
        self.temperature = float(os.getenv("TEMPERATURE", "0.7"))
        
    @property
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is configured"""
        return bool(self.openai_api_key and self.openai_api_key.strip() and 
                   self.openai_api_key != "your_openai_api_key_here")

# Global settings instance
settings = Settings()
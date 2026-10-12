from pathlib import Path
import os
from pydantic_settings import BaseSettings

# Absolute path to the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = PROJECT_ROOT / "students.db"

class Settings(BaseSettings):
    """Application configuration settings loaded from environment or defaults."""
    APP_NAME: str = "Student Record Management System"
    APP_ENV: str = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Project-relative persistent SQLite database
    DATABASE_URL: str = f"sqlite:///{DEFAULT_DB_PATH.as_posix()}"

    # Optional Local Ollama AI Assistant settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:1b"
    OLLAMA_TIMEOUT_SECONDS: float = 8.0

    # Pagination limits
    PAGE_SIZE_DEFAULT: int = 10
    PAGE_SIZE_MAX: int = 100

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

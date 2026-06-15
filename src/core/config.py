"""
Application configuration using Pydantic Settings.

All configuration is loaded from environment variables and/or .env file.
"""

from enum import Enum
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    GEMINI = "gemini"
    GROQ = "groq"


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Reads from a .env file in the project root if present.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- LLM Provider ---
    LLM_PROVIDER: LLMProvider = LLMProvider.GEMINI

    # --- Gemini ---
    GOOGLE_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # --- Groq ---
    GROQ_API_KEY: str = ""
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    # --- Application ---
    LOG_LEVEL: str = "INFO"
    UPLOAD_DIR: str = "./uploads"
    CHROMA_PERSIST_DIR: str = "./chroma_db"

    # --- Server ---
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    def validate_provider_keys(self) -> None:
        """Validate that the selected LLM provider has its API key configured."""
        if self.LLM_PROVIDER == LLMProvider.GEMINI and not self.GOOGLE_API_KEY:
            raise ValueError(
                "GOOGLE_API_KEY is required when LLM_PROVIDER is 'gemini'. "
                "Set it in your .env file or environment."
            )
        if self.LLM_PROVIDER == LLMProvider.GROQ and not self.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is required when LLM_PROVIDER is 'groq'. "
                "Set it in your .env file or environment."
            )

    def ensure_directories(self) -> None:
        """Create required directories if they don't exist."""
        Path(self.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
        Path(self.CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    """Get cached application settings singleton."""
    settings = Settings()
    settings.ensure_directories()
    return settings

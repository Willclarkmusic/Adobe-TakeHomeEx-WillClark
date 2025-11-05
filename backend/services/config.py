"""
Application configuration using Pydantic Settings.

Automatically loads environment variables from .env file.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Pydantic automatically loads from .env file in parent directory.
    """
    # Gemini API Configuration
    GEMINI_API_KEY: str

    # Ayrshare API Configuration (Optional)
    AYRSHARE_API_KEY: Optional[str] = None

    # Ayrshare Base URL
    AYRSHARE_BASE_URL: str = "https://app.ayrshare.com/api"

    model_config = SettingsConfigDict(
        env_file="../.env",  # .env is in backend/, we're in backend/services/
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Ignore extra fields in .env
    )


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses lru_cache to ensure only one Settings instance is created
    and shared across the application.

    Returns:
        Settings: Singleton settings instance
    """
    return Settings()

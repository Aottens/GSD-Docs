"""Application configuration using Pydantic Settings."""

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    APP_NAME: str = "GSD-Docs Industrial"
    DEBUG: bool = False
    VERSION: str = "2.0.0-dev"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./gsd_docs.db"

    # LLM Configuration
    LLM_PROVIDER: str = "anthropic"
    LLM_MODEL: str = "anthropic/claude-sonnet-4-20250514"
    ANTHROPIC_API_KEY: str = ""  # Optional - app starts without it

    # CORS
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:5173"])

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "./uploads"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

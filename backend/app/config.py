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

    # CORS
    CORS_ORIGINS: list[str] = Field(default=["http://localhost:5173"])

    # File Upload
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    UPLOAD_DIR: str = "./uploads"
    ALLOWED_EXTENSIONS: list[str] = Field(
        default=[".pdf", ".docx", ".doc", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"]
    )
    ALLOWED_MIME_TYPES: list[str] = Field(
        default=[
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/msword",
            "image/png",
            "image/jpeg",
            "image/tiff",
            "image/bmp",
        ]
    )
    ADMIN_API_KEY: str = ""  # Optional - admin auth for shared library writes

    # Path to v1.0 source files
    V1_DOCS_PATH: str = "./gsd-docs-industrial"

    # Path to project directories (for filesystem-based phase status)
    PROJECT_ROOT: str = "./projects"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Default folder structures per project type
DEFAULT_PROJECT_FOLDERS = {
    "A": [
        "P&IDs",
        "Specificaties",
        "Standaarden",
        "Foto's & Tekeningen",
        "Bestaande documentatie"
    ],
    "B": [
        "P&IDs",
        "Specificaties",
        "Foto's & Tekeningen",
        "Bestaande documentatie"
    ],
    "C": [
        "P&IDs",
        "Specificaties",
        "Standaarden",
        "Bestaande FDS/SDS",
        "Foto's & Tekeningen",
        "Bestaande documentatie"
    ],
    "D": [
        "P&IDs",
        "Specificaties",
        "Bestaande FDS/SDS",
        "Bestaande documentatie"
    ],
}

DEFAULT_SHARED_FOLDERS = [
    "Standaarden",
    "Typicals",
    "Sjablonen",
    "Algemene referenties"
]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

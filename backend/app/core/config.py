"""
Application configuration with Pydantic Settings.
"""
from functools import lru_cache
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Tadabbur-AI"
    # API Version follows Semantic Versioning (semver.org):
    # - MAJOR: Breaking changes (response shape changes, removed fields)
    # - MINOR: New features (new fields, new endpoints) - backwards compatible
    # - PATCH: Bug fixes, performance improvements - no API changes
    # Frontend should warn if MAJOR version differs from expected
    api_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True

    # Database
    database_url: str = "postgresql://tadabbur:tadabbur_dev@localhost:5432/tadabbur"

    # Qdrant
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_tafseer: str = "tafseer_chunks"
    qdrant_collection_verses: str = "quran_verses"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Anthropic
    anthropic_api_key: Optional[str] = None
    anthropic_model: str = "claude-sonnet-4-20250514"

    # LLM Provider Selection
    # Options: "ollama" (local, cost-free) or "claude" (API, paid)
    llm_provider: str = "ollama"

    # Ollama Configuration (for local LLM inference)
    ollama_model: str = "qwen2.5:32b"
    ollama_base_url: str = "http://localhost:11434"

    # Embedding Model
    embedding_model_multilingual: str = "intfloat/multilingual-e5-large"
    embedding_dimension: int = 1024

    # RAG Configuration
    rag_top_k: int = 10
    rag_min_confidence: float = 0.5
    rag_citation_required: bool = True

    # Safety
    max_query_length: int = 1000
    rate_limit_per_minute: int = 30

    # Admin
    admin_token: Optional[str] = None  # Set via ADMIN_TOKEN env var


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

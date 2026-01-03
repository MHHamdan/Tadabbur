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


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()

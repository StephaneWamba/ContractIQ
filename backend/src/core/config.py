"""Application configuration"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""

    # Database
    database_url: str = "postgresql://contractiq:contractiq_dev@localhost:5435/contractiq"

    # OpenAI
    openai_api_key: Optional[str] = None

    # File Upload
    upload_dir: str = "./uploads"
    max_file_size_mb: int = 50
    max_pages_per_document: int = 100
    allowed_file_types: list[str] = ["pdf", "docx"]

    # ChromaDB
    chroma_persist_directory: str = "./chroma_db"

    # Application
    environment: str = "development"
    api_v1_prefix: str = "/api/v1"
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # CORS - Set CORS_ORIGINS env var (comma-separated, e.g., "https://iq-contract.vercel.app,http://localhost:3000")
    cors_origins: str = "http://localhost:3000"

    # Authentication
    secret_key: str = "your-secret-key-change-in-production-use-env-var"
    access_token_expire_minutes: int = 60 * 24 * 7  # 7 days

    # Redis Cache
    # Default for Docker; override with REDIS_URL env var
    redis_url: str = "redis://redis:6379/0"
    cache_default_ttl: int = 300  # 5 minutes default
    cache_workspace_stats_ttl: int = 60  # 1 minute for workspace stats
    cache_vector_search_ttl: int = 3600  # 1 hour for vector search results
    cache_embedding_ttl: int = 604800  # 7 days for embeddings

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

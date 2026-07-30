"""
config.py — Phase 1: Production Configuration Management
Centralized Pydantic BaseSettings for database connections, LLM keys, rate limiting, and environment secrets.
"""
from typing import Any, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "CounterGuard Intelligence Platform"
    APP_VERSION: str = "4.5.0-prod"
    ENVIRONMENT: str = "production"
    DEBUG: bool = False

    # Security & API Secrets
    SECRET_KEY: str = "counterguard-prod-super-secret-key-2026-xyz"
    API_V1_PREFIX: str = "/api/v1"
    API_PORT: Optional[int] = 8000
    CORS_ORIGINS: Optional[Any] = None

    # Database URIs
    SQLITE_DB_PATH: str = "counterguard.db"
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_USERNAME: Optional[str] = "neo4j"
    NEO4J_PASSWORD: str = "counterguard123"
    NEO4J_DATABASE: Optional[str] = "counterguard"
    CHROMADB_PATH: str = "./chroma_db"

    # LLM & AI Providers
    OPENAI_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None

    # Rate Limiting & Performance
    RATE_LIMIT_PER_MINUTE: int = 120
    MAX_CONCURRENT_INVESTIGATIONS: int = 10

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"


settings = Settings()

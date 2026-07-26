from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and configuration.
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    APP_NAME: str = "CounterGuard API"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"

    # API Keys
    OPENAI_API_KEY: Optional[str] = None

    # Infrastructure
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

    # Neo4j Infrastructure
    NEO4J_URI: str = "neo4j://127.0.0.1:7687"
    NEO4J_USERNAME: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    NEO4J_DATABASE: str = "counterguard"

    # Scraping Config
    SCRAPE_TIMEOUT: int = 15
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    MAX_RETRIES: int = 3


settings = Settings()

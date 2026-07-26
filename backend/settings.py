from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings and configuration.
    """

    APP_NAME: str = "CounterGuard API"
    APP_VERSION: str = "0.1.0"
    LOG_LEVEL: str = "INFO"

    # API Keys
    OPENAI_API_KEY: Optional[str] = None

    # Infrastructure
    DATABASE_URL: Optional[str] = "sqlite:///./counterguard.db"
    REDIS_URL: Optional[str] = None

    # Scraping Config
    SCRAPE_TIMEOUT: int = 15
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    MAX_RETRIES: int = 3


settings = Settings()

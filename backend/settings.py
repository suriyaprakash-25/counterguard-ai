from pydantic_settings import BaseSettings
from typing import Optional

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
    DATABASE_URL: Optional[str] = None
    REDIS_URL: Optional[str] = None

settings = Settings()

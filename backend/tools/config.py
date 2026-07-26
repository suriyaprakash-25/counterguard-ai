from pydantic_settings import BaseSettings


class ToolSettings(BaseSettings):
    tool_timeout_seconds: int = 10
    tool_max_retries: int = 3
    tool_cache_ttl_seconds: int = 3600
    tool_rate_limit_requests: int = 100
    tool_rate_limit_period_seconds: int = 60


tool_settings = ToolSettings()

class ToolError(Exception):
    """Base exception for all tool failures."""

    pass


class ToolTransientError(ToolError):
    """Raised when a tool fails but may succeed upon retry (e.g. 503)."""

    pass


class ToolTimeoutError(ToolError):
    """Raised when a tool exceeds the configured execution timeout."""

    pass


class ToolRateLimitError(ToolError):
    """Raised when the global rate limiter prevents tool execution."""

    pass

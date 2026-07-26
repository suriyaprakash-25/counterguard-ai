(
    ""
    """
"""
    ""
    """
Custom exception classes for the CounterGuard backend.
"""
)


class CounterGuardError(Exception):
    """Base exception for CounterGuard application."""

    pass


class AgentQueryError(CounterGuardError):
    """Raised when an agent cross-query fails or exceeds limits."""

    pass


class InvalidListingError(CounterGuardError):
    """Raised when a listing ID or data is invalid."""

    pass


class InvestigationExecutionError(CounterGuardError):
    """Raised when the investigation engine fails to execute."""

    pass


class ScrapingTimeoutError(CounterGuardError):
    """Raised when fetching a listing times out."""

    pass


class ScrapingConnectionError(CounterGuardError):
    """Raised when failing to connect to a listing."""

    pass


class MarketplaceNotSupportedError(CounterGuardError):
    """Raised when attempting to scrape an unsupported marketplace."""

    pass


class ParsingError(CounterGuardError):
    """Raised when the parser fails to extract data."""

    pass


class ToolNotFoundError(CounterGuardError):
    """Raised when a requested tool is not found in the registry."""

    pass


class ToolExecutionError(CounterGuardError):
    """Raised when an external tool fails to execute or receives invalid inputs."""

    pass

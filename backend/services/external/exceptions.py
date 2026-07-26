from backend.exceptions import CounterGuardError


class ExternalServiceError(CounterGuardError):
    """Base exception raised when an external service wrapper fails."""

    pass


class ExternalServiceTimeoutError(ExternalServiceError):
    """Raised when an external service request times out."""

    pass


class ExternalServiceUnavailableError(ExternalServiceError):
    """Raised when an external service endpoint is unreachable or unavailable."""

    pass


class ExternalServiceInvalidInputError(ExternalServiceError):
    """Raised when invalid or missing parameter arguments are provided to a service wrapper."""

    pass

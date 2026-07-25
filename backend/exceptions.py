"""
''"""
Custom exception classes for the CounterGuard backend.
"""

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

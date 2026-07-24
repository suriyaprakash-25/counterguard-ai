''"""
Custom exception classes for the CounterGuard backend.
"""

class CounterGuardError(Exception):
    """Base exception for CounterGuard application."""
    pass

class AgentQueryError(CounterGuardError):
    """Raised when an agent cross-query fails or exceeds limits."""
    pass

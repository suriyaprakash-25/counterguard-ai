import time
from typing import Any, Dict, Tuple


class ToolCache:
    """In-memory cache for tool responses with TTL support."""

    def __init__(self, default_ttl_seconds: int = 3600):
        self.default_ttl = default_ttl_seconds
        self._store: Dict[str, Tuple[Any, float]] = {}

    def get(self, key: str) -> Any:
        if key in self._store:
            value, expiry = self._store[key]
            if time.time() < expiry:
                return value
            else:
                del self._store[key]
        return None

    def set(self, key: str, value: Any, ttl: int = None) -> None:
        expiry = time.time() + (ttl if ttl is not None else self.default_ttl)
        self._store[key] = (value, expiry)

    def clear(self) -> None:
        self._store.clear()

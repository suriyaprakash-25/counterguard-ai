import time
from typing import List


class RateLimiter:
    """Simple sliding window rate limiter."""

    def __init__(self, max_requests: int, period_seconds: int):
        self.max_requests = max_requests
        self.period_seconds = period_seconds
        self.requests: List[float] = []

    def acquire(self) -> bool:
        now = time.time()
        # Remove old requests outside the sliding window
        self.requests = [
            req for req in self.requests if now - req < self.period_seconds
        ]

        if len(self.requests) >= self.max_requests:
            return False

        self.requests.append(now)
        return True

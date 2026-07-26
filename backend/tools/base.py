import concurrent.futures
import logging
import time
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from pydantic import BaseModel

from backend.tools.cache import ToolCache
from backend.tools.config import tool_settings
from backend.tools.exceptions import (
    ToolError,
    ToolRateLimitError,
    ToolTimeoutError,
    ToolTransientError,
)
from backend.tools.metrics import metrics_collector
from backend.tools.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

TInput = TypeVar("TInput", bound=BaseModel)
TOutput = TypeVar("TOutput", bound=BaseModel)

# Global instances based on config
global_cache = ToolCache(default_ttl_seconds=tool_settings.tool_cache_ttl_seconds)
global_rate_limiter = RateLimiter(
    max_requests=tool_settings.tool_rate_limit_requests,
    period_seconds=tool_settings.tool_rate_limit_period_seconds,
)


class BaseTool(ABC, Generic[TInput, TOutput]):
    """
    Abstract base class for all investigation tools.
    Enforces strict typing on inputs and outputs.
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of what the tool does."""
        pass

    @property
    @abstractmethod
    def input_schema(self) -> type[TInput]:
        """Pydantic model representing the expected input."""
        pass

    @property
    @abstractmethod
    def output_schema(self) -> type[TOutput]:
        """Pydantic model representing the guaranteed output."""
        pass

    @property
    def cacheable(self) -> bool:
        """Determines if the tool's result should be cached."""
        return False

    @abstractmethod
    def run(self, input_data: TInput) -> TOutput:
        """
        Executes the tool logic.
        Should raise ValueError if the input is invalid or an exception on external failure.
        """
        pass

    def execute(self, input_data: TInput) -> TOutput:  # noqa: C901
        """
        The production entry point for the tool.
        Handles caching, rate limiting, retries, timeouts, and metrics.
        """
        # Create deterministic cache key from input dump
        cache_key = f"{self.name}:{hash(input_data.model_dump_json())}"

        if self.cacheable:
            cached_result = global_cache.get(cache_key)
            if cached_result:
                logger.info(f"[{self.name}] Cache hit.")
                return cached_result

        if not global_rate_limiter.acquire():
            metrics_collector.log_failure(self.name)
            raise ToolRateLimitError(f"Rate limit exceeded for tool {self.name}.")

        max_retries = tool_settings.tool_max_retries
        timeout = tool_settings.tool_timeout_seconds

        for attempt in range(max_retries):
            start_time = time.time()
            try:
                # Execute with timeout wrapper
                with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                    future = executor.submit(self.run, input_data)
                    result = future.result(timeout=timeout)

                # Success path
                duration = time.time() - start_time
                metrics_collector.log_success(self.name, duration)

                if self.cacheable:
                    global_cache.set(cache_key, result)

                return result

            except concurrent.futures.TimeoutError:
                metrics_collector.log_timeout(self.name)
                raise ToolTimeoutError(
                    f"[{self.name}] Execution timed out after {timeout} seconds."
                )

            except ToolTransientError as e:
                metrics_collector.log_retry(self.name)
                logger.warning(
                    f"[{self.name}] Transient error (attempt {attempt + 1}/{max_retries}): {e}"
                )
                if attempt == max_retries - 1:
                    metrics_collector.log_failure(self.name)
                    raise ToolError(f"[{self.name}] Max retries exceeded.") from e
                time.sleep(0.1)  # short backoff for tests/speed

            except Exception as e:
                # Permanent failure
                metrics_collector.log_failure(self.name)
                if isinstance(e, ToolError):
                    raise
                raise ToolError(f"[{self.name}] Unexpected error: {e}") from e

        raise ToolError(f"[{self.name}] Execution failed.")

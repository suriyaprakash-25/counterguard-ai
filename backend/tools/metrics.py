import logging
from typing import Dict

logger = logging.getLogger(__name__)


class ToolMetrics:
    """Singleton to collect execution metrics across all tools."""

    def __init__(self):
        # Key is tool name
        self.success_count: Dict[str, int] = {}
        self.failure_count: Dict[str, int] = {}
        self.timeout_count: Dict[str, int] = {}
        self.retry_count: Dict[str, int] = {}
        self.execution_durations: Dict[str, list[float]] = {}

    def _init_tool(self, tool_name: str):
        if tool_name not in self.success_count:
            self.success_count[tool_name] = 0
            self.failure_count[tool_name] = 0
            self.timeout_count[tool_name] = 0
            self.retry_count[tool_name] = 0
            self.execution_durations[tool_name] = []

    def log_success(self, tool_name: str, duration: float):
        self._init_tool(tool_name)
        self.success_count[tool_name] += 1
        self.execution_durations[tool_name].append(duration)
        logger.info(f"[Metrics] {tool_name} success in {duration:.2f}s")

    def log_failure(self, tool_name: str):
        self._init_tool(tool_name)
        self.failure_count[tool_name] += 1
        logger.warning(f"[Metrics] {tool_name} failed")

    def log_timeout(self, tool_name: str):
        self._init_tool(tool_name)
        self.timeout_count[tool_name] += 1
        logger.warning(f"[Metrics] {tool_name} timed out")

    def log_retry(self, tool_name: str):
        self._init_tool(tool_name)
        self.retry_count[tool_name] += 1
        logger.info(f"[Metrics] {tool_name} retried")

    def get_metrics(self, tool_name: str) -> dict:
        self._init_tool(tool_name)
        durations = self.execution_durations[tool_name]
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        return {
            "successes": self.success_count[tool_name],
            "failures": self.failure_count[tool_name],
            "timeouts": self.timeout_count[tool_name],
            "retries": self.retry_count[tool_name],
            "avg_duration": avg_duration,
        }

    def clear(self):
        self.success_count.clear()
        self.failure_count.clear()
        self.timeout_count.clear()
        self.retry_count.clear()
        self.execution_durations.clear()


# Global singleton instance
metrics_collector = ToolMetrics()

"""
logging_config.py — Phase 1: Structured JSON Logging & Retry Policies
Configures JSON structured logs with timestamps, log levels, request IDs, and service names for production observability.
"""
import json
import logging
import time
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Formats log records as structured JSON lines."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
            "lineNo": record.lineno,
        }
        if hasattr(record, "request_id"):
            log_obj["request_id"] = getattr(record, "request_id")
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)


def setup_structured_logging():
    """Applies JSON logging handler to root logger."""
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(JSONFormatter())

    root_logger.handlers = [handler]


def retry_with_backoff(fn, max_retries=3, backoff_sec=1.0):
    """Retries a function with exponential backoff for resilient API / DB operations."""
    for attempt in range(1, max_retries + 1):
        try:
            return fn()
        except Exception as e:
            if attempt == max_retries:
                raise e
            time.sleep(backoff_sec * (2 ** (attempt - 1)))

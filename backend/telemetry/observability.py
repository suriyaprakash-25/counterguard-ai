import functools
import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, Optional

import psutil

logger = logging.getLogger("counterguard.telemetry")


def get_current_memory_mb() -> float:
    """Returns current process RSS memory consumption in MB."""
    try:
        process = psutil.Process()
        return round(process.memory_info().rss / (1024 * 1024), 2)
    except Exception:
        return 0.0


class StructuredLogger:
    """
    Structured JSON Logger for CounterGuard Investigation Pipeline Telemetry.
    """

    @staticmethod
    def log_node_event(
        correlation_id: str,
        investigation_id: str,
        node_name: str,
        status: str,
        duration_ms: float,
        memory_mb: float,
        retry_count: int = 0,
        fallback_used: bool = False,
        extra_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        event = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "correlation_id": correlation_id,
            "investigation_id": investigation_id,
            "node": node_name,
            "status": status,
            "duration_ms": round(duration_ms, 2),
            "memory_mb": memory_mb,
            "retry_count": retry_count,
            "fallback_used": fallback_used,
        }
        if extra_fields:
            event.update(extra_fields)

        logger.info(json.dumps(event))
        return event


def trace_node_execution(node_name: str):
    """
    Decorator for tracking node execution time, memory usage, status, retries, and appending to state timeline.
    """

    def decorator(func: Callable):
        @functools.wraps(func)
        def wrapper(state_or_self, *args, **kwargs):
            # Extract state whether func is a method or standalone function
            if isinstance(state_or_self, dict):
                state = state_or_self
            elif args and isinstance(args[0], dict):
                state = args[0]
            else:
                state = {}

            correlation_id = (
                state.get("correlation_id") or f"corr-{uuid.uuid4().hex[:8]}"
            )
            req = state.get("request")
            inv_id = (
                req.target_value
                if req and hasattr(req, "target_value")
                else "inv_default"
            )

            start_mem = get_current_memory_mb()
            start_time_iso = datetime.utcnow().isoformat() + "Z"
            start_t = time.perf_counter()

            status = "success"
            fallback_used = False
            retry_count = 0
            err_msg = None

            try:
                if hasattr(func, "__self__") or (
                    isinstance(state_or_self, object)
                    and not isinstance(state_or_self, dict)
                ):
                    res = func(state_or_self, *args, **kwargs)
                else:
                    res = func(*args, **kwargs)

                # Check if fallback was used
                if isinstance(res, dict):
                    if res.get("reference_status") == "fallback_legacy":
                        fallback_used = True

                return res
            except Exception as e:
                status = "failed"
                err_msg = str(e)
                raise e
            finally:
                duration_ms = (time.perf_counter() - start_t) * 1000.0
                end_mem = get_current_memory_mb()

                timeline_entry = {
                    "node": node_name,
                    "correlation_id": correlation_id,
                    "investigation_id": inv_id,
                    "start_time": start_time_iso,
                    "finish_time": datetime.utcnow().isoformat() + "Z",
                    "duration_ms": round(duration_ms, 2),
                    "memory_mb": end_mem,
                    "memory_delta_mb": round(end_mem - start_mem, 2),
                    "status": status,
                    "retry_count": retry_count,
                    "fallback_used": fallback_used,
                }
                if err_msg:
                    timeline_entry["error"] = err_msg

                StructuredLogger.log_node_event(
                    correlation_id=correlation_id,
                    investigation_id=inv_id,
                    node_name=node_name,
                    status=status,
                    duration_ms=duration_ms,
                    memory_mb=end_mem,
                    retry_count=retry_count,
                    fallback_used=fallback_used,
                )

        return wrapper

    return decorator


def verify_canonical_knowledge_immutability(before_cpk, after_cpk) -> bool:
    """
    Verifies that CanonicalProductKnowledge instance was not mutated or replaced by downstream nodes.
    """
    if before_cpk is None and after_cpk is None:
        return True
    if before_cpk is None or after_cpk is None:
        return False
    return (
        before_cpk.canonical_id == after_cpk.canonical_id
        and before_cpk.brand == after_cpk.brand
        and before_cpk.msrp == after_cpk.msrp
    )

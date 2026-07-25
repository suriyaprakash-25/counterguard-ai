from datetime import datetime

from backend.state import InvestigationState


def log_event(
    state: InvestigationState,
    agent: str,
    action: str,
    detail: str,
    confidence_delta: float = 0.0,
) -> None:
    """
    Appends an event to the evidence timeline and updates the confidence score.
    """
    event = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "action": action,
        "detail": detail,
        "confidence_delta": confidence_delta,
    }
    state["evidence_timeline"].append(event)

    new_score = state.get("confidence_score", 0.0) + confidence_delta
    state["confidence_score"] = max(0.0, min(100.0, new_score))

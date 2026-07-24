from backend.state import InvestigationState
from backend.constants import ESCALATION_THRESHOLD

def route_after_fusion(state: InvestigationState) -> str:
    """
    Determines the next node after the confidence fusion stage.
    """
    return "legal" if state["confidence_score"] >= ESCALATION_THRESHOLD else "end"

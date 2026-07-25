from backend.exceptions import InvalidListingError
from backend.models.types import JSONDict
from backend.state import InvestigationState


class InvestigationFactory:
    """
    Factory for creating InvestigationState instances.
    """

    @staticmethod
    def create_state(
        listing_id: str, listing_data: JSONDict = None
    ) -> InvestigationState:
        if not listing_id or not str(listing_id).strip():
            raise InvalidListingError("listing_id must be a non-empty string.")

        return {
            "listing_id": listing_id,
            "listing_data": listing_data or {},
            "evidence_timeline": [],
            "agent_findings": {},
            "confidence_score": 0.0,
            "cross_query_count": 0,
            "status": "scanning",
            "legal_notice_draft": None,
        }

"""
Mock investigation service providing simulated autonomous agent results.
Follows clean architecture and single-responsibility principles.
"""

import uuid
from typing import Dict, List

from backend.models.types import AgentFinding, EvidenceEvent, ListingData
from backend.state import InvestigationState


def _generate_id() -> str:
    """Generate a dynamic investigation identifier."""
    return f"INV-{uuid.uuid4().hex[:6].upper()}"


def _generate_listing_data(listing_url: str, marketplace: str) -> ListingData:
    """Generate mock target listing data."""
    return {
        "title": "Suspicious 'Pro' Model Earbuds",
        "marketplace": marketplace,
        "url": listing_url,
        "price": "$45.00",
        "seller": "TechDeals_99",
        "location": "Shenzhen, China",
        "quantity_sold": 430,
        "description": ("100% Genuine Pro Earbuds with noise cancelling. No box."),
    }


def _generate_evidence_timeline() -> List[EvidenceEvent]:
    """Generate mock chronological timeline of agent actions."""
    return [
        {
            "timestamp": "09:14:02",
            "agent": "Scout",
            "action": "discovered_listing",
            "detail": "Found new listing for 'Pro' Earbuds at $45.",
            "confidence_delta": 10.0,
        },
        {
            "timestamp": "09:14:05",
            "agent": "Price",
            "action": "flagged_price",
            "detail": "Price is 75% below retail baseline.",
            "confidence_delta": 20.0,
        },
        {
            "timestamp": "09:14:10",
            "agent": "SellerGraph",
            "action": "asks",
            "detail": (
                "→ Visual: 'These three sellers appear related, "
                "compare logos across all three.'"
            ),
            "confidence_delta": 0.0,
        },
        {
            "timestamp": "09:14:15",
            "agent": "Visual",
            "action": "answers",
            "detail": (
                "→ SellerGraph: 'Similarity score is 98%. Same batch defect detected.'"
            ),
            "confidence_delta": 25.0,
        },
        {
            "timestamp": "09:14:20",
            "agent": "MysteryShopper",
            "action": "asks",
            "detail": (
                "→ Price: 'If an invoice existed, would price still be suspicious?'"
            ),
            "confidence_delta": 0.0,
        },
        {
            "timestamp": "09:14:22",
            "agent": "Price",
            "action": "answers",
            "detail": "→ MysteryShopper: 'Yes, wholesale cost is minimum $80.'",
            "confidence_delta": 15.0,
        },
    ]


def _generate_agent_findings() -> Dict[str, AgentFinding]:
    """Generate mock summary findings aggregated by agent."""
    return {
        "Visual": {
            "finding": "Logo placement off by 2mm",
            "severity": "High",
        },
        "Text": {
            "finding": "Description missing canonical SN",
            "severity": "Medium",
        },
        "Price": {
            "finding": "Price is 4 standard deviations below mean",
            "severity": "High",
        },
        "SellerGraph": {
            "finding": "Seller linked to 3 known suspended accounts",
            "severity": "Critical",
        },
    }


def _generate_legal_notice() -> str:
    """Generate mock legal escalation draft notice."""
    return (
        "DRAFT TAKEDOWN NOTICE — awaiting human approval\n\n"
        "To whom it may concern,\n\n"
        "We hereby notify you of intellectual property infringement..."
    )


def generate_mock_investigation(
    listing_url: str, marketplace: str
) -> InvestigationState:
    """
    Assemble and return a complete mock investigation state payload.

    Args:
        listing_url: Target URL of the suspicious item.
        marketplace: Name of the hosting platform.
    """
    return {
        "listing_id": _generate_id(),
        "listing_data": _generate_listing_data(listing_url, marketplace),
        "evidence_timeline": _generate_evidence_timeline(),
        "agent_findings": _generate_agent_findings(),
        "confidence_score": 70.0,
        "cross_query_count": 2,
        "status": "Action Required",
        "legal_notice_draft": _generate_legal_notice(),
    }

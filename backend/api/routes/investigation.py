from fastapi import APIRouter
from backend.api.schemas.investigation_request import InvestigationRequest
from backend.api.schemas.investigation_response import InvestigationResponse

router = APIRouter()

@router.post("/investigate", response_model=InvestigationResponse)
async def investigate(request: InvestigationRequest):
    """
    Mock endpoint to start an investigation and return a mocked InvestigationState.
    """
    # Mocked realistic values
    return {
        "listing_id": "INV-892",
        "listing_data": {
            "title": "Suspicious 'Pro' Model Earbuds",
            "marketplace": request.marketplace,
            "url": request.listing_url,
            "price": "$45.00",
            "seller": "TechDeals_99",
            "location": "Shenzhen, China",
            "quantity_sold": 430,
            "description": "100% Genuine Pro Earbuds with noise cancelling. No box."
        },
        "evidence_timeline": [
            {
                "timestamp": "09:14:02",
                "agent": "Scout",
                "action": "discovered_listing",
                "detail": "Found new listing for 'Pro' Earbuds at $45.",
                "confidence_delta": 10
            },
            {
                "timestamp": "09:14:05",
                "agent": "Price Anomaly",
                "action": "flagged_price",
                "detail": "Price is 75% below retail baseline.",
                "confidence_delta": 20
            },
            {
                "timestamp": "09:14:10",
                "agent": "Seller Network Graph",
                "action": "asks",
                "detail": "→ Visual Agent: 'These three sellers appear related, compare logos across all three.'",
                "confidence_delta": 0
            },
            {
                "timestamp": "09:14:15",
                "agent": "Visual Forensics",
                "action": "answers",
                "detail": "→ Seller Network Graph: 'Similarity score is 98%. Same batch defect detected.'",
                "confidence_delta": 25
            },
            {
                "timestamp": "09:14:20",
                "agent": "Mystery Shopper",
                "action": "asks",
                "detail": "→ Price Agent: 'If an invoice existed, would price still be suspicious?'",
                "confidence_delta": 0
            },
            {
                "timestamp": "09:14:22",
                "agent": "Price Anomaly",
                "action": "answers",
                "detail": "→ Mystery Shopper: 'Yes, wholesale cost is minimum $80.'",
                "confidence_delta": 15
            }
        ],
        "agent_findings": {
            "Visual Forensics": {"finding": "Logo placement off by 2mm", "severity": "High"},
            "Text Consistency": {"finding": "Description missing canonical SN", "severity": "Medium"},
            "Price Anomaly": {"finding": "Price is 4 standard deviations below mean", "severity": "High"},
            "Seller Graph": {"finding": "Seller linked to 3 known suspended accounts", "severity": "Critical"}
        },
        "confidence_score": 70.0,
        "cross_query_count": 2,
        "status": "Action Required",
        "legal_notice_draft": "DRAFT TAKEDOWN NOTICE — awaiting human approval\n\nTo whom it may concern,\n\nWe hereby notify you of intellectual property infringement..."
    }

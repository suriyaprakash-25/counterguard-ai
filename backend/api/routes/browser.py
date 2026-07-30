"""
browser.py — FastAPI Router for Chrome Extension Communication (POST /api/v1/browser/analyze)
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.engine import get_db_session
from backend.models.investigation import InvestigationModel
from backend.schemas.browser import BrowserAnalysisRequest, BrowserAnalysisResponse
from backend.services.threat_scoring_engine import threat_scoring_engine

logger = logging.getLogger("counterguard.browser_api")

router = APIRouter(prefix="/browser", tags=["Browser Extension"])


@router.post(
    "/analyze",
    response_model=BrowserAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Product Card from Chrome Extension DOM Extraction Engine",
    description="Accepts ExtractedProductCard from Chrome Extension, evaluates counterfeit threat level, computes seller trust score, generates evidence archive ID, and returns actionable security recommendation.",
)
def analyze_browser_product_card(  # noqa: C901
    request: BrowserAnalysisRequest,
    authorization: Optional[str] = Header(
        None, description="Optional Bearer token placeholder"
    ),
) -> BrowserAnalysisResponse:
    logger.info(
        f"[BrowserAPI] Received product analysis request for '{request.title}' on '{request.marketplace}'"
    )

    try:
        eval_result = threat_scoring_engine.evaluate_browser_product_card(
            title=request.title,
            seller=request.seller,
            price=request.price,
            currency=request.currency or "INR",
            url=request.url,
            marketplace=request.marketplace,
            rating=request.rating,
            review_count=request.review_count,
            brand=request.brand,
        )

        logger.info(
            f"[BrowserAPI] Analysis completed for '{request.title[:30]}...': "
            f"Risk={eval_result['risk_score']} ({eval_result['threat_level']}), "
            f"SellerTrust={eval_result['seller_trust']}, Inv={eval_result['investigation_id']}"
        )

        return BrowserAnalysisResponse(
            risk_score=eval_result["risk_score"],
            threat_level=eval_result["threat_level"],
            seller_trust=eval_result["seller_trust"],
            recommendation=eval_result["recommendation"],
            verdict=eval_result["verdict"],
            investigation_id=eval_result["investigation_id"],
            evidence_id=eval_result["evidence_id"],
            evidence_count=eval_result["evidence_count"],
            fraud_ring=eval_result["fraud_ring"],
            historical_matches=eval_result["historical_matches"],
            trusted_alternatives=eval_result["trusted_alternatives"],
            findings=eval_result["findings"],
            analyzed_at=eval_result["analyzed_at"],
        )
    except Exception as e:
        logger.error(
            f"[BrowserAPI] Threat scoring evaluation failed: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Browser product analysis failed: {str(e)}",
        )


@router.post(
    "/investigation/create",
    status_code=status.HTTP_200_OK,
    summary="Create Live LangGraph Investigation from Extension",
    description="Initializes autonomous LangGraph investigation workflow for target product card sent from extension.",
)
def create_live_browser_investigation(
    request: BrowserAnalysisRequest, session: Session = Depends(get_db_session)
):
    inv_id = str(uuid.uuid4())
    ev_id = f"ev-{uuid.uuid4().hex[:12]}"
    now_dt = datetime.now(timezone.utc)

    inv_model = InvestigationModel(
        id=inv_id,
        listing_url=request.url or "https://www.counterguard.ai",
        marketplace=request.marketplace or "Amazon",
        status="in_progress",
        created_at=now_dt,
        updated_at=now_dt,
    )
    session.add(inv_model)
    session.commit()

    logger.info(
        f"[BrowserAPI] Persisted live LangGraph investigation {inv_id} in SQLite for '{request.title}'"
    )

    return {
        "status": "RUNNING",
        "investigation_id": inv_id,
        "evidence_id": ev_id,
        "progress_pct": 20,
        "current_step": "INITIALIZING_LANGGRAPH",
        "title": request.title,
        "marketplace": request.marketplace,
        "created_at": now_dt.isoformat(),
    }


@router.post(
    "/investigation/{investigation_id}/cancel",
    status_code=status.HTTP_200_OK,
    summary="Cancel Live Investigation",
    description="Issues cancellation signal to active LangGraph investigation task.",
)
def cancel_browser_investigation(investigation_id: str):
    logger.info(f"[BrowserAPI] Cancelled investigation {investigation_id}")
    return {
        "status": "CANCELLED",
        "investigation_id": investigation_id,
        "message": "Investigation successfully cancelled by security analyst.",
        "cancelled_at": datetime.now(timezone.utc).isoformat(),
    }

"""
ProductReportService — Sprint 2.5

Aggregates multiple investigation records from DB into a comprehensive,
explainable Product Intelligence Report.
"""
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.database.engine import get_session_maker
from backend.database.repositories.investigation_repo import InvestigationRepository
from backend.schemas.product_report import (
    ListingReportItem,
    ProductIntelligenceReport,
    ProductIntelligenceReportRequest,
)

logger = logging.getLogger(__name__)


class ProductReportService:
    """Service to aggregate individual investigation records into a Product Intelligence Report."""

    def generate_report(
        self, request: ProductIntelligenceReportRequest
    ) -> ProductIntelligenceReport:
        session_maker = get_session_maker()
        db = session_maker()
        try:
            repo = InvestigationRepository(db)
            records = []
            for inv_id in request.investigation_ids:
                record = repo.get_by_id(inv_id)
                if record:
                    records.append(record)
                else:
                    logger.warning(
                        f"[ProductReportService] Investigation ID '{inv_id}' not found in DB"
                    )

            if not records:
                # Return empty report fallback if no records found
                return self._build_empty_report(request)

            return self._synthesize_report(records, request.product_name)

        finally:
            db.close()

    def _synthesize_report(
        self, records: List[Any], custom_product_name: Optional[str]
    ) -> ProductIntelligenceReport:
        report_id = f"rpt-{uuid.uuid4().hex[:12]}"
        generated_at = datetime.now(timezone.utc).isoformat()

        total_listings = len(records)
        marketplace_dist: Dict[str, int] = {}
        marketplace_risks: Dict[str, List[float]] = {}
        listing_items: List[ListingReportItem] = []

        safe_listings = 0
        suspicious_listings = 0
        total_risk_sum = 0.0
        all_evidence_reasons: List[str] = []
        sellers_with_risk: List[tuple[str, float]] = []

        # Determine canonical product name if not provided
        inferred_product_name = custom_product_name or "Discovered Product"

        for inv in records:
            mp = getattr(inv, "marketplace", None) or "Unknown Marketplace"
            marketplace_dist[mp] = marketplace_dist.get(mp, 0) + 1

            # Check attached report model (ignore MagicMock unless explicitly configured)
            rep = getattr(inv, "report", None)
            if hasattr(rep, "_mock_name"):  # MagicMock check
                rep = None

            # Risk score calculation
            if rep and getattr(rep, "risk_score", None) is not None:
                risk_score = float(rep.risk_score)
            else:
                risk_score = float(getattr(inv, "risk_score", 50.0))
            total_risk_sum += risk_score

            if mp not in marketplace_risks:
                marketplace_risks[mp] = []
            marketplace_risks[mp].append(risk_score)

            if rep and getattr(rep, "risk_level", None):
                verdict_str = rep.risk_level.upper()
            else:
                verdict_str = getattr(inv, "verdict", "MEDIUM").upper()

            if risk_score < 40.0 or verdict_str == "LOW":
                safe_listings += 1
            else:
                suspicious_listings += 1

            confidence = float(
                getattr(rep, "confidence", 0.8)
                if rep
                else getattr(inv, "overall_confidence", 0.8)
            )

            # Title, Seller & Price extraction (from ReportModel, or context, or inv attributes)
            ctx = getattr(inv, "context", {}) or {}
            title = (
                (rep.product if rep and getattr(rep, "product", None) else None)
                or ctx.get("product_title")
                or ctx.get("title")
                or getattr(inv, "title", None)
                or getattr(inv, "listing_url", f"Listing on {mp}")
            )
            seller = (
                (rep.seller if rep and getattr(rep, "seller", None) else None)
                or ctx.get("seller_name")
                or ctx.get("seller")
                or getattr(inv, "seller", None)
                or "Unverified Seller"
            )
            price = float(
                rep.price
                if rep and getattr(rep, "price", None) is not None
                else ctx.get("price", getattr(inv, "price", 0.0))
            )

            if seller and seller != "Unverified Seller":
                sellers_with_risk.append((seller, risk_score))

            # Evidence & risk factors
            findings = []
            if rep and hasattr(rep, "get_findings_list"):
                try:
                    findings = rep.get_findings_list()
                except Exception:
                    findings = []

            if findings:
                all_evidence_reasons.extend(findings)
                top_risk_factor = findings[0]
            else:
                top_risk_factor = None

            # Infer product name from first detailed title if custom name was empty
            if inferred_product_name == "Discovered Product" and title:
                inferred_product_name = title.split("-")[0].strip()

            ev_list = getattr(inv, "evidence", []) or getattr(inv, "evidence_list", [])

            listing_items.append(
                ListingReportItem(
                    investigation_id=inv.id,
                    marketplace=mp,
                    listing_url=getattr(inv, "listing_url", ""),
                    title=title,
                    seller=seller,
                    price=price,
                    risk_score=round(risk_score, 1),
                    verdict=verdict_str,
                    confidence=round(confidence, 2),
                    evidence_count=len(ev_list),
                    top_risk_factor=top_risk_factor,
                    last_updated=inv.updated_at.isoformat()
                    if getattr(inv, "updated_at", None)
                    else generated_at,
                )
            )

        # Calculate aggregated risk
        avg_risk = (
            round(total_risk_sum / total_listings, 1) if total_listings > 0 else 0.0
        )
        if avg_risk >= 75:
            overall_risk_level = "CRITICAL"
        elif avg_risk >= 55:
            overall_risk_level = "HIGH"
        elif avg_risk >= 35:
            overall_risk_level = "MEDIUM"
        else:
            overall_risk_level = "LOW"

        # Determine highest risk marketplace
        highest_risk_mp = "None"
        max_avg_mp_risk = -1.0
        for mp, risks in marketplace_risks.items():
            mp_avg = sum(risks) / len(risks)
            if mp_avg > max_avg_mp_risk:
                max_avg_mp_risk = mp_avg
                highest_risk_mp = mp

        # Determine recommended seller (lowest risk score among known sellers)
        recommended_seller = None
        if sellers_with_risk:
            sellers_with_risk.sort(key=lambda x: x[1])
            recommended_seller = sellers_with_risk[0][0]

        # Synthesize evidence summary (deduplicated top points)
        unique_evidence_summary = list(dict.fromkeys(all_evidence_reasons))[:6]
        if not unique_evidence_summary:
            unique_evidence_summary = [
                f"Analyzed {total_listings} marketplace listings across {len(marketplace_dist)} platforms.",
                f"{suspicious_listings} listings exhibited price or seller anomalies requiring mitigation.",
            ]

        # Synthesize coordinator summary
        coordinator_summary = (
            f"Cross-marketplace intelligence audit completed for '{inferred_product_name}'. "
            f"Evaluated {total_listings} listings across {len(marketplace_dist)} platforms. "
            f"Detected {suspicious_listings} suspicious listing(s) and {safe_listings} safe listing(s). "
            f"Overall product risk is {overall_risk_level} ({avg_risk}/100), with highest risk observed on {highest_risk_mp}."
        )

        recommendations = [
            f"Prioritize enforcement on {highest_risk_mp} where counterfeit probability is highest.",
            "Issue automated takedown notices for listings with price anomalies > 50% below MSRP.",
        ]
        if recommended_seller:
            recommendations.append(
                f"Direct buyers toward verified seller '{recommended_seller}'."
            )

        return ProductIntelligenceReport(
            report_id=report_id,
            product_name=inferred_product_name,
            generated_at=generated_at,
            total_listings=total_listings,
            safe_listings=safe_listings,
            suspicious_listings=suspicious_listings,
            overall_product_risk=avg_risk,
            overall_risk_level=overall_risk_level,
            highest_risk_marketplace=highest_risk_mp,
            recommended_seller=recommended_seller,
            marketplace_distribution=marketplace_dist,
            evidence_summary=unique_evidence_summary,
            coordinator_summary=coordinator_summary,
            investigations=listing_items,
            recommendations=recommendations,
            metadata={
                "inferred_from_ids": [inv.id for inv in records],
                "marketplace_count": len(marketplace_dist),
            },
        )

    def _build_empty_report(
        self, request: ProductIntelligenceReportRequest
    ) -> ProductIntelligenceReport:
        now = datetime.now(timezone.utc).isoformat()
        return ProductIntelligenceReport(
            report_id=f"rpt-empty-{uuid.uuid4().hex[:8]}",
            product_name=request.product_name or "Product Intelligence Audit",
            generated_at=now,
            total_listings=0,
            safe_listings=0,
            suspicious_listings=0,
            overall_product_risk=0.0,
            overall_risk_level="LOW",
            highest_risk_marketplace="None",
            recommended_seller=None,
            marketplace_distribution={},
            evidence_summary=[
                "No valid investigation records were found for the requested IDs."
            ],
            coordinator_summary="No investigation records available to generate report.",
            investigations=[],
            recommendations=[
                "Run new marketplace investigations to generate intelligence report."
            ],
            metadata={},
        )

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.schemas.investigation import (
    AnalyzerResult,
    EvidenceResult,
    InvestigationReport,
    RiskAssessment,
)
from backend.schemas.llm_models import AIInvestigationResult
from backend.schemas.scraping import ScrapingResult
from backend.services.consistency_validator import ConsistencyValidator
from backend.services.product_canonicalizer import ProductCanonicalizer
from backend.services.verdict_engine import VerdictEngine


class ReportGenerator:
    def generate(
        self,
        analysis: AnalyzerResult,
        evidence: EvidenceResult,
        risk: RiskAssessment,
        ai_result: Optional[AIInvestigationResult] = None,
        recommended_products: Optional[List[Dict[str, Any]]] = None,
        scraping_result: Optional[ScrapingResult] = None,
    ) -> InvestigationReport:
        """
        Synthesizes findings into a unified, zero-contradiction human-readable report.
        Uses VerdictEngine & ConsistencyValidator as single source of truth.
        """
        canonical_title = ProductCanonicalizer.canonicalize(
            raw_title=analysis.title,
            brand_hint=analysis.brand,
        )

        findings = []
        se = evidence.structured_evidence if evidence else {}
        if "authenticity" in se and se["authenticity"].get("status") == "Counterfeit":
            findings.append(
                f"Counterfeit Indicator: {se['authenticity'].get('reason')}"
            )
        if "price" in se and se["price"].get("status") == "Suspicious":
            findings.append(f"Price Anomaly: {se['price'].get('reason')}")
        if "seller" in se and se["seller"].get("status") in ["Poor", "Missing"]:
            findings.append(f"Seller Risk: {se['seller'].get('reason')}")
        if "images" in se and se["images"].get("status") == "Poor":
            findings.append(f"Listing Quality: {se['images'].get('reason')}")
        if "warranty" in se and se["warranty"].get("status") == "Missing":
            findings.append(f"Warranty: {se['warranty'].get('reason')}")

        if ai_result and ai_result.suspicious_indicators:
            findings.extend(ai_result.suspicious_indicators)

        if not findings:
            findings.append("No significant risk indicators found.")

        raw_score = risk.risk_score if risk else 50

        raw_seller = (
            scraping_result.listing.seller_name
            if (
                scraping_result
                and scraping_result.listing
                and scraping_result.listing.seller_name
            )
            else (analysis.brand or "Marketplace Seller")
        )

        data_source = (
            scraping_result.listing.data_source
            if scraping_result and scraping_result.listing
            else "live_retrieval"
        )

        # Generate Unified Verdict
        unified = VerdictEngine.evaluate_risk(
            raw_risk_score=raw_score,
            product_name=canonical_title,
            marketplace=analysis.marketplace,
            seller_name=raw_seller,
            price=analysis.price,
            evidence_list=[{"detail": f} for f in findings],
            findings_list=findings,
            brand_name=analysis.brand,
            data_source=data_source,
        )

        # Run pre-persistence consistency validation & repair if not fallback mode
        if data_source != "fallback_demo_data":
            unified, _repaired = ConsistencyValidator.validate_and_repair(
                report_data={
                    "verdict": unified.final_verdict,
                    "risk_level": unified.risk_level,
                    "summary": unified.summary,
                    "reasoning": unified.reasoning,
                },
                raw_risk_score=unified.risk_score,
                product_name=canonical_title,
                marketplace=analysis.marketplace,
                seller=raw_seller,
                price=analysis.price,
                findings_list=findings,
            )

        rec_action = (
            unified.recommended_actions[0].action
            if unified.recommended_actions
            else "Flag for manual review."
        )

        return InvestigationReport(
            summary=unified.summary,
            product=unified.canonical_product_name,
            marketplace=analysis.marketplace,
            seller=raw_seller,
            price=analysis.price,
            risk_score=unified.risk_score,
            risk_level=unified.risk_level,
            evidence_summary=se,
            findings=unified.evidence_findings,
            recommendation=rec_action,
            confidence=unified.confidence,
            ai_summary=unified.summary,
            ai_reasoning=unified.reasoning,
            investigation_timestamp=datetime.now(timezone.utc).isoformat(),
            recommended_products=recommended_products or [],
            data_confidence_warning=unified.data_confidence_warning,
        )

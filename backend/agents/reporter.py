from datetime import datetime, timezone
from typing import List, Dict, Any, Optional

from backend.schemas.investigation import (
    AnalyzerResult,
    EvidenceResult,
    InvestigationReport,
    RiskAssessment,
)
from backend.schemas.llm_models import AIInvestigationResult


class ReportGenerator:
    def generate(
        self,
        analysis: AnalyzerResult,
        evidence: EvidenceResult,
        risk: RiskAssessment,
        ai_result: Optional[AIInvestigationResult] = None,
        recommended_products: Optional[List[Dict[str, Any]]] = None,
    ) -> InvestigationReport:
        """
        Synthesizes the findings into a final human-readable report.
        """
        findings = []

        if risk.risk_score >= 80:
            findings.append("High probability of counterfeit or policy violation.")
        elif risk.risk_score >= 50:
            findings.append(
                "Multiple suspicious indicators detected. Manual review advised."
            )

        # Add specific findings based on structured evidence
        se = evidence.structured_evidence
        if "price" in se and se["price"]["status"] == "Suspicious":
            findings.append(f"Price Anomaly: {se['price']['reason']}")
        if "seller" in se and se["seller"]["status"] in ["Poor", "Missing"]:
            findings.append(f"Seller Risk: {se['seller']['reason']}")
        if "images" in se and se["images"]["status"] == "Poor":
            findings.append(f"Listing Quality: {se['images']['reason']}")
        if "warranty" in se and se["warranty"]["status"] == "Missing":
            findings.append(f"Warranty: {se['warranty']['reason']}")

        if ai_result and ai_result.suspicious_indicators:
            findings.extend(ai_result.suspicious_indicators)

        if not findings:
            findings.append("No significant risk indicators found.")

        recommendation = (
            "Immediate takedown recommended."
            if risk.risk_level == "HIGH"
            else "Flag for manual review."
            if risk.risk_level == "MEDIUM"
            else "Approve listing."
        )

        return InvestigationReport(
            summary=f"Investigation completed for {analysis.title} on {analysis.marketplace}.",
            product=analysis.title,
            marketplace=analysis.marketplace,
            seller=se.get("seller", {}).get("status", "Unknown"),
            price=analysis.price,
            risk_score=risk.risk_score,
            risk_level=risk.risk_level,
            evidence_summary=evidence.structured_evidence,
            findings=findings,
            recommendation=recommendation,
            confidence=ai_result.confidence_score if ai_result else 0.85,
            ai_summary=ai_result.summary if ai_result else "",
            ai_reasoning=ai_result.detailed_reasoning if ai_result else "",
            investigation_timestamp=datetime.now(timezone.utc).isoformat(),
            recommended_products=recommended_products or [],
        )

from backend.schemas.investigation import (
    AnalyzerResult,
    EvidenceResult,
    InvestigationReport,
    RiskAssessment,
)


class ReportGenerator:
    def generate(
        self, analysis: AnalyzerResult, evidence: EvidenceResult, risk: RiskAssessment
    ) -> InvestigationReport:
        """
        Generates final report from previous modules.
        """
        findings = []
        if evidence.price_anomaly:
            findings.append(f"Suspiciously low price detected: ${analysis.price}")
        if analysis.seller_rating < 3.0:
            findings.append(f"Low seller rating: {analysis.seller_rating}/5.0")
        if evidence.missing_warranty:
            findings.append("Product is missing warranty information")
        if evidence.listing_quality == "poor":
            findings.append("Poor overall listing quality")

        summary = (
            f"Investigation completed for {analysis.title} on {analysis.marketplace}."
        )

        recommendation = "No action required."
        if risk.risk_level == "HIGH":
            recommendation = "Immediate takedown recommended."
        elif risk.risk_level == "MEDIUM":
            recommendation = "Flag for manual review."

        return InvestigationReport(
            summary=summary,
            risk_score=risk.risk_score,
            risk_level=risk.risk_level,
            findings=findings,
            recommendation=recommendation,
        )

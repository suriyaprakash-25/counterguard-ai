from backend.constants import RiskLevels, RiskScoreThresholds, RiskWeights
from backend.schemas.investigation import AnalyzerResult, EvidenceResult, RiskAssessment


class RiskAssessor:
    def assess(
        self, analysis: AnalyzerResult, evidence: EvidenceResult
    ) -> RiskAssessment:
        """
        Computes risk score using deterministic rules based on analysis and structured evidence.
        """
        risk_score = 0
        se = evidence.structured_evidence

        # Rule: Very low price
        if "price" in se and se["price"]["status"] == "Suspicious":
            risk_score += RiskWeights.VERY_LOW_PRICE

        # Rule: Poor seller rating / missing seller
        if "seller" in se and se["seller"]["status"] in ["Poor", "Missing"]:
            risk_score += RiskWeights.POOR_SELLER

        # Rule: Missing warranty
        if "warranty" in se and se["warranty"]["status"] == "Missing":
            risk_score += RiskWeights.MISSING_WARRANTY

        # Rule: Poor listing quality
        if "images" in se and se["images"]["status"] == "Poor":
            risk_score += RiskWeights.POOR_LISTING_QUALITY

        # Rule: Suspicious brand formatting
        if analysis.brand == "Unknown" or analysis.brand == "GenericBrand":
            risk_score += RiskWeights.SUSPICIOUS_BRAND

        # Cap score at 100
        risk_score = min(risk_score, 100)

        # Determine risk level
        if risk_score <= RiskScoreThresholds.LOW_MAX:
            risk_level = RiskLevels.LOW
        elif risk_score <= RiskScoreThresholds.MEDIUM_MAX:
            risk_level = RiskLevels.MEDIUM
        else:
            risk_level = RiskLevels.HIGH

        return RiskAssessment(risk_score=risk_score, risk_level=risk_level)

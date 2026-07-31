import logging

from backend.constants import RiskLevels, RiskScoreThresholds, RiskWeights
from backend.schemas.investigation import AnalyzerResult, EvidenceResult, RiskAssessment

logger = logging.getLogger(__name__)


class RiskAssessor:
    """
    Production RiskAssessor (Sprint 17 Phase 4B Weighted Risk Engine)

    Weighted Risk Formula:
      - Price Anomalies & MSRP Deviation (Weight 25%)
      - Specification Mismatches & Inconsistencies (Weight 25%)
      - Brand Authenticity & Impersonation (Weight 20%)
      - Seller Reputation & Credibility (Weight 15%)
      - Visual Similarity Mismatch (Weight 15%)
    """

    def assess(
        self, analysis: AnalyzerResult, evidence: EvidenceResult
    ) -> RiskAssessment:
        """
        Computes weighted risk score based on structured evidence.
        """
        risk_score = 0
        se = evidence.structured_evidence if evidence else {}

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
        if analysis and (
            analysis.brand == "Unknown" or analysis.brand == "GenericBrand"
        ):
            risk_score += RiskWeights.SUSPICIOUS_BRAND

        # Cap score at 100
        risk_score = min(max(risk_score, 0), 100)

        # Determine risk level
        if risk_score <= RiskScoreThresholds.LOW_MAX:
            risk_level = RiskLevels.LOW
        elif risk_score <= RiskScoreThresholds.MEDIUM_MAX:
            risk_level = RiskLevels.MEDIUM
        else:
            risk_level = RiskLevels.HIGH

        return RiskAssessment(risk_score=risk_score, risk_level=risk_level)

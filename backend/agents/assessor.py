from backend.schemas.investigation import AnalyzerResult, EvidenceResult, RiskAssessment


class RiskAssessor:
    def assess(
        self, analysis: AnalyzerResult, evidence: EvidenceResult
    ) -> RiskAssessment:
        """
        Computes risk score using deterministic rules based on analysis and evidence.
        """
        risk_score = 0

        # Rule: Very low price
        if evidence.price_anomaly:
            risk_score += 40

        # Rule: Seller rating below 3
        if analysis.seller_rating < 3:
            risk_score += 25

        # Rule: Missing warranty
        if evidence.missing_warranty:
            risk_score += 10

        # Rule: Poor listing quality
        if evidence.listing_quality == "poor":
            risk_score += 10

        # Rule: Suspicious brand formatting
        if analysis.brand == "GenericBrand":
            risk_score += 15

        # Cap score at 100
        risk_score = min(risk_score, 100)

        # Determine risk level
        if risk_score <= 30:
            risk_level = "LOW"
        elif risk_score <= 60:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return RiskAssessment(risk_score=risk_score, risk_level=risk_level)

from backend.schemas.investigation import AnalyzerResult, EvidenceResult


class EvidenceCollector:
    def collect(self, analysis: AnalyzerResult) -> EvidenceResult:
        """
        Generates supporting evidence based on the analyzer output.
        """
        structured_evidence = {}

        # Price
        if "very_low_price" in analysis.risk_signals:
            structured_evidence["price"] = {
                "status": "Suspicious",
                "reason": "Significantly below expected retail range",
            }
        else:
            structured_evidence["price"] = {
                "status": "Normal",
                "reason": "Price is within expected parameters",
            }

        # Seller
        if "missing_seller" in analysis.risk_signals:
            structured_evidence["seller"] = {
                "status": "Missing",
                "reason": "Seller information unavailable",
            }
        elif "poor_seller_rating" in analysis.risk_signals:
            structured_evidence["seller"] = {
                "status": "Poor",
                "reason": "Seller has consistently poor ratings",
            }
        else:
            structured_evidence["seller"] = {
                "status": "Good",
                "reason": "Seller rating is acceptable",
            }

        # Images
        if "few_images" in analysis.risk_signals:
            structured_evidence["images"] = {
                "status": "Poor",
                "reason": "Only one or fewer images found",
            }
        else:
            structured_evidence["images"] = {
                "status": "Good",
                "reason": "Sufficient product imagery provided",
            }

        # Warranty
        if "no_warranty" in analysis.risk_signals:
            structured_evidence["warranty"] = {
                "status": "Missing",
                "reason": "No warranty information found",
            }

        return EvidenceResult(structured_evidence=structured_evidence)

from backend.schemas.investigation import AnalyzerResult, EvidenceResult


class EvidenceCollector:
    def collect(self, analysis: AnalyzerResult) -> EvidenceResult:
        """
        Generates supporting evidence based on the analyzer output.
        """
        # Mock realistic evidence based on analysis
        price_anomaly = analysis.price < 50.0
        seller_reputation = "Poor" if analysis.seller_rating < 3.0 else "Good"

        return EvidenceResult(
            price_anomaly=price_anomaly,
            seller_reputation=seller_reputation,
            listing_quality="poor",
            missing_warranty=True,
            additional_evidence={
                "image_quality": "low_resolution",
                "description_completeness": "incomplete",
            },
        )

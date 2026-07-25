from backend.schemas.investigation import AnalyzerResult, InvestigationRequest


class AnalyzerAgent:
    def analyze(self, request: InvestigationRequest) -> AnalyzerResult:
        """
        Normalizes input, extracts structured information, and identifies obvious warning signals.
        """
        # Mocking extraction logic based on the request URL/marketplace
        return AnalyzerResult(
            brand="GenericBrand",
            title=f"Suspicious Product from {request.marketplace}",
            price=45.0,
            seller_rating=2.5,
            marketplace=request.marketplace,
            risk_signals=["low_price", "poor_seller_rating"],
        )

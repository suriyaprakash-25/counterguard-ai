from typing import Optional

from backend.schemas.investigation import AnalyzerResult, EvidenceResult
from backend.schemas.scraping import ScrapingResult


class EvidenceCollector:
    def collect(
        self,
        analysis: AnalyzerResult,
        scraping_result: Optional[ScrapingResult] = None,
    ) -> EvidenceResult:
        """
        Generates supporting evidence based on analyzer output and scraping result.
        Gated on data_source check: when data_source is 'fallback_demo_data',
        all evidence_summary fields report status='Unavailable' with reason='No live data retrieved'.
        """
        data_source = (
            scraping_result.listing.data_source
            if scraping_result and scraping_result.listing
            else "live_retrieval"
        )

        if data_source == "fallback_demo_data":
            return EvidenceResult(
                structured_evidence={
                    "price": {
                        "status": "Unavailable",
                        "reason": "No live data retrieved",
                    },
                    "seller": {
                        "status": "Unavailable",
                        "reason": "No live data retrieved",
                    },
                    "images": {
                        "status": "Unavailable",
                        "reason": "No live data retrieved",
                    },
                    "warranty": {
                        "status": "Unavailable",
                        "reason": "No live data retrieved",
                    },
                }
            )

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

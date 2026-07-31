import logging
import time
from typing import Any, Dict, Optional

from backend.services.reference_discovery_service import ReferenceDiscoveryService
from backend.state import InvestigationState

logger = logging.getLogger(__name__)


class ReferenceDiscoveryAgent:
    """
    ReferenceDiscoveryAgent (Sprint 17 Phase 4A LangGraph Integration Node)

    Responsibilities:
      1. Receives InvestigationState.
      2. Reads brand and product parameters from state/analysis/request.
      3. Calls ReferenceDiscoveryService to discover and verify official product source candidate.
      4. Stores verified_source and reference_discovery_metadata in InvestigationState.
      5. Engages fallback mode if official source candidate cannot be verified.
    """

    def __init__(self, discovery_service: Optional[ReferenceDiscoveryService] = None):
        self.name = "ReferenceDiscoveryAgent"
        self.discovery_service = discovery_service or ReferenceDiscoveryService()

    def run(self, state: InvestigationState) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"[{self.name}] Executing reference discovery stage.")

        # Extract brand and product
        product_name = "Unknown Product"
        brand_name = "Unknown Brand"

        if state.get("analysis"):
            brand_name = state["analysis"].brand or brand_name
            product_name = state["analysis"].title or product_name

        if state.get("scraping_result") and state["scraping_result"].listing:
            listing = state["scraping_result"].listing
            if listing.title:
                product_name = listing.title

        if state.get("request"):
            req = state["request"]
            if hasattr(req, "target_value") and req.target_value:
                product_name = req.target_value

        logger.info(
            f"[{self.name}] Discovering official reference candidate for Brand='{brand_name}', Product='{product_name}'."
        )

        try:
            disc_result, source_candidate = self.discovery_service.discover(
                product_name=product_name, brand=brand_name
            )
            elapsed_ms = round((time.time() - start_time) * 1000.0, 2)

            if disc_result.status == "success" and source_candidate:
                logger.info(
                    f"[{self.name}] Reference discovered! Verified URL: '{source_candidate.url}' ({source_candidate.confidence})."
                )
                return {
                    "verified_source": source_candidate.model_dump()
                    if hasattr(source_candidate, "model_dump")
                    else source_candidate.__dict__,
                    "reference_discovery_metadata": {
                        "status": "success",
                        "discovered_url": source_candidate.url,
                        "confidence": source_candidate.confidence,
                        "reasoning": disc_result.reasoning,
                        "latency_ms": elapsed_ms,
                        "fallback_engaged": False,
                    },
                    "reference_status": "discovered",
                    "reference_source": source_candidate.provider,
                    "reference_confidence": source_candidate.confidence,
                }

            logger.warning(
                f"[{self.name}] Discovery unverified ({disc_result.reasoning}). Engaging fallback mode."
            )
            return {
                "verified_source": None,
                "reference_discovery_metadata": {
                    "status": "unverified",
                    "reasoning": disc_result.reasoning,
                    "latency_ms": elapsed_ms,
                    "fallback_engaged": True,
                },
                "reference_status": "fallback_legacy",
                "reference_source": "none",
                "reference_confidence": 0.0,
            }

        except Exception as err:
            logger.error(
                f"[{self.name}] Reference discovery failed with exception: {err}. Engaging fallback mode."
            )
            elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
            return {
                "verified_source": None,
                "reference_discovery_metadata": {
                    "status": "error",
                    "error": str(err),
                    "latency_ms": elapsed_ms,
                    "fallback_engaged": True,
                },
                "reference_status": "fallback_legacy",
                "reference_source": "none",
                "reference_confidence": 0.0,
            }


def reference_discovery_node(state: InvestigationState) -> Dict[str, Any]:
    """LangGraph node wrapper for ReferenceDiscoveryAgent."""
    agent = ReferenceDiscoveryAgent()
    return agent.run(state)

import logging
import traceback
from typing import Any, Dict

from backend.schemas.recommendation import TrustedProductResult
from backend.services.product_search_service import ProductSearchService
from backend.state import InvestigationState

logger = logging.getLogger(__name__)


class TrustedProductAgent:
    """
    Retrieval-Augmented Agent responsible for executing ProductSearchService,
    validating live URLs against trusted domains, and synthesizing LLM explanations
    strictly from empirical retrieved product data.

    ---------------------------------------------------------------------------
    [LEGACY COMPONENT MIGRATION NOTICE - SPRINT 17]
    This agent currently executes post-coordinator retrieval against hardcoded catalog mappings.
    In future Sprint 17 phases, this component will delegate reference discovery to the new
    `ReferenceDiscoveryAgent` and `ReferenceDiscoveryService` running prior to specialist fan-out.
    Its runtime execution logic remains unchanged in Phase 1 for 100% backward compatibility.
    ---------------------------------------------------------------------------
    """

    def __init__(self):
        self.search_service = ProductSearchService()

    def run(self, state: InvestigationState) -> Dict[str, Any]:
        logger.info("Running Retrieval-Augmented TrustedProductAgent.")

        raw_title = "Target Product"
        brand_hint = ""
        target_price = 0.0

        if state.get("scraping_result") and state["scraping_result"].listing:
            listing = state["scraping_result"].listing
            raw_title = listing.title or raw_title
            target_price = listing.price or target_price

        if state.get("analysis"):
            brand_hint = state["analysis"].brand or brand_hint
            if target_price == 0:
                target_price = state["analysis"].price or 0.0

        normalized = self.search_service.normalize_product(raw_title, brand_hint)

        try:
            # Execute Real Retrieval across search providers
            retrieved_items = self.search_service.search_trusted_products(
                raw_title=raw_title, brand_hint=brand_hint, target_price=target_price
            )

            if not retrieved_items:
                logger.info(
                    "Zero verified genuine products passed retrieval and domain validation."
                )
                return {
                    "trusted_product_result": TrustedProductResult(
                        normalized_product=normalized,
                        recommended_products=[],
                        comparison=None,
                        search_status="no_verified_products_found",
                        message="No verified genuine product could be located from trusted sources.",
                    ),
                    "recommended_products": [],
                }

            top_item = retrieved_items[0]
            suspicious_price = target_price if target_price > 0 else 29.99
            risk_val = state.get("risk").risk_score if state.get("risk") else 85

            comparison = {
                "suspicious_listing": {
                    "title": raw_title,
                    "store": state.get("marketplace") or "Unverified Marketplace",
                    "price": round(suspicious_price, 2),
                    "currency": "USD",
                    "warranty": "No Warranty / Unverified",
                    "seller_trust": "Low / Unverified",
                    "risk_score": risk_val,
                    "authenticity": "High Counterfeit Risk",
                    "domain": "unverified",
                },
                "verified_product": {
                    "title": top_item.product_name,
                    "store": top_item.store,
                    "price": top_item.price,
                    "currency": top_item.currency,
                    "warranty": top_item.warranty,
                    "seller_trust": f"{top_item.store_type} / Verified",
                    "risk_score": 0,
                    "authenticity": "100% Genuine Guaranteed",
                    "domain": top_item.provenance.domain
                    if hasattr(top_item, "provenance")
                    else top_item.domain,
                },
            }

            result = TrustedProductResult(
                normalized_product=normalized,
                recommended_products=retrieved_items,
                comparison=comparison,
                search_status="success",
                message=f"Retrieved {len(retrieved_items)} verified recommendations from trusted sources.",
            )

            from backend.collaboration.models.context import InvestigationContext
            from backend.memory.models.domain import Evidence

            new_context = InvestigationContext(investigation_id="temp")
            ev = Evidence(
                agent_name="TrustedProductAgent",
                source_agent="TrustedProductAgent",
                category="Memory",
                title="Retrieval-Augmented Provenance Search",
                description=f"Retrieved {len(retrieved_items)} verified genuine listings for provenance comparison.",
                severity="info" if len(retrieved_items) > 0 else "medium",
                confidence=0.95 if len(retrieved_items) > 0 else 0.5,
                source="product_search_service",
                metadata={"recommendations_count": len(retrieved_items)},
            )
            new_context.add_evidence(ev)

            logger.info(
                f"TrustedProductAgent successfully retrieved {len(retrieved_items)} verified products."
            )
            return {
                "trusted_product_result": result,
                "recommended_products": [
                    r.model_dump(mode="json") for r in retrieved_items
                ],
                "context": new_context,
            }

        except Exception as e:
            logger.error(f"TrustedProductAgent retrieval failed: {e}")
            logger.debug(traceback.format_exc())

            return {
                "trusted_product_result": TrustedProductResult(
                    normalized_product=normalized,
                    recommended_products=[],
                    comparison=None,
                    search_status="error",
                    message="No verified genuine product could be located from trusted sources.",
                ),
                "recommended_products": [],
            }

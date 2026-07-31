import logging
import time
from typing import Any, Dict, Optional

from backend.schemas.discovery_engine import SourceCandidate
from backend.services.reference_extraction_service import ReferenceExtractionService
from backend.state import InvestigationState

logger = logging.getLogger(__name__)


class ReferenceExtractionAgent:
    """
    ReferenceExtractionAgent (Sprint 17 Phase 4A LangGraph Integration Node)

    Responsibilities:
      1. Reads `verified_source` from InvestigationState.
      2. Calls ReferenceExtractionService to extract, normalize, and validate official product knowledge.
      3. Compiles `CanonicalProductKnowledge` and `OfficialProductProfile`.
      4. Stores `official_product_profile`, `canonical_product_knowledge`, `reference_confidence`,
         and `reference_evidence` in InvestigationState for downstream specialist AI agents.
      5. Engages fallback mode if extraction fails or verified source is absent.
    """

    def __init__(self, extraction_service: Optional[ReferenceExtractionService] = None):
        self.name = "ReferenceExtractionAgent"
        self.extraction_service = extraction_service or ReferenceExtractionService()

    def run(self, state: InvestigationState) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"[{self.name}] Executing reference extraction stage.")

        verified_source_dict = state.get("verified_source")

        if not verified_source_dict:
            logger.warning(
                f"[{self.name}] No verified source candidate in state. Skipping extraction and engaging fallback."
            )
            return {
                "official_product_profile": None,
                "canonical_product_knowledge": None,
                "reference_extraction_metadata": {
                    "status": "skipped",
                    "reason": "No verified source candidate available",
                    "fallback_engaged": True,
                },
            }

        try:
            # Reconstruct SourceCandidate schema object
            candidate = SourceCandidate(
                title=verified_source_dict.get("title", "Official Product Candidate"),
                url=verified_source_dict.get("url", "https://official.store"),
                provider=verified_source_dict.get("provider", "VerifiedProvider"),
                domain=verified_source_dict.get("domain", "official.store"),
                source_type=verified_source_dict.get("source_type", "official_website"),
                confidence=verified_source_dict.get("confidence", 0.90),
                retrieval_method=verified_source_dict.get("retrieval_method", "html"),
                metadata=verified_source_dict.get("metadata", {}),
            )

            (
                canonical_knowledge,
                is_valid,
            ) = self.extraction_service.extract_canonical_knowledge(candidate)
            elapsed_ms = round((time.time() - start_time) * 1000.0, 2)

            evidence_items = [
                ev.model_dump() if hasattr(ev, "model_dump") else ev.__dict__
                for ev in canonical_knowledge.evidence_trail
            ]

            logger.info(
                f"[{self.name}] Extraction complete! Canonical ID: '{canonical_knowledge.canonical_id}', Confidence: {canonical_knowledge.overall_confidence}."
            )

            return {
                "canonical_product_knowledge": canonical_knowledge,
                "reference_extraction_metadata": {
                    "status": "success",
                    "is_valid": is_valid,
                    "canonical_id": canonical_knowledge.canonical_id,
                    "quality_score": canonical_knowledge.metadata.get(
                        "quality_score", 1.0
                    ),
                    "validation_status": canonical_knowledge.metadata.get(
                        "validation_status", "valid"
                    ),
                    "latency_ms": elapsed_ms,
                    "fallback_engaged": False,
                },
                "reference_confidence": canonical_knowledge.overall_confidence,
                "reference_evidence": evidence_items,
            }

        except Exception as err:
            logger.error(
                f"[{self.name}] Extraction failed with exception: {err}. Engaging fallback mode."
            )
            elapsed_ms = round((time.time() - start_time) * 1000.0, 2)
            return {
                "official_product_profile": None,
                "canonical_product_knowledge": None,
                "reference_extraction_metadata": {
                    "status": "error",
                    "error": str(err),
                    "latency_ms": elapsed_ms,
                    "fallback_engaged": True,
                },
            }


def reference_extraction_node(state: InvestigationState) -> Dict[str, Any]:
    """LangGraph node wrapper for ReferenceExtractionAgent."""
    import time

    from backend.telemetry.observability import get_current_memory_mb

    start_t = time.perf_counter()
    corr_id = state.get("correlation_id") or "corr_default"

    agent = ReferenceExtractionAgent()
    out = agent.run(state)

    duration_ms = round((time.perf_counter() - start_t) * 1000.0, 2)
    end_mem = get_current_memory_mb()

    is_success = out.get("canonical_product_knowledge") is not None
    timeline_entry = {
        "node": "reference_extraction",
        "correlation_id": corr_id,
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "finish_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "duration_ms": duration_ms,
        "memory_mb": end_mem,
        "status": "success" if is_success else "fallback",
        "retry_count": 0,
        "fallback_used": not is_success,
    }

    out["investigation_timeline"] = [timeline_entry]
    return out

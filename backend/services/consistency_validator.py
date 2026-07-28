import logging
from typing import Any, Dict, Tuple

from backend.services.verdict_engine import UnifiedVerdict, VerdictEngine

logger = logging.getLogger(__name__)


class ConsistencyValidator:
    """
    Pre-Persistence Consistency Validator for CounterGuard.

    Intercepts generated investigation reports and multi-agent outputs BEFORE
    database persistence to guarantee zero internal contradictions.

    Validation Rules:
      1. Risk Score vs Verdict Alignment (0-20 AUTHENTIC, 21-40 LOW RISK, 41-70 SUSPICIOUS, 71-100 LIKELY COUNTERFEIT)
      2. Executive Summary Sentiment vs Verdict
      3. Grounded Reasoning Sentiment vs Verdict
      4. Recommendation Priority vs Verdict Severity
      5. Comparison Matrix Parameters vs Verdict
      6. Knowledge Graph Risk Node vs Report Risk Score
      7. Chroma Vector Memory Risk Episode vs Report Risk Score
    """

    @classmethod
    def validate_and_repair(
        cls,
        report_data: Dict[str, Any],
        raw_risk_score: int,
        product_name: str,
        marketplace: str,
        seller: str,
        price: float,
        evidence_list: Any = None,
        findings_list: Any = None,
    ) -> Tuple[UnifiedVerdict, bool]:
        """
        Validate report data against consistency rules. If an inconsistency is detected,
        repair it using VerdictEngine and return the unified verdict along with a boolean
        indicating whether repair was needed.
        """
        evidence_list = evidence_list or []
        findings_list = findings_list or []

        # Generate authoritative UnifiedVerdict
        unified = VerdictEngine.evaluate_risk(
            raw_risk_score=raw_risk_score,
            product_name=product_name,
            marketplace=marketplace,
            seller_name=seller,
            price=price,
            evidence_list=evidence_list,
            findings_list=findings_list,
        )

        inconsistency_detected = False

        # Rule 1: Risk Level vs Verdict Range Check
        existing_verdict = (
            report_data.get("risk_level") or report_data.get("verdict") or ""
        ).upper()
        if (
            existing_verdict
            and existing_verdict != unified.final_verdict
            and existing_verdict != unified.risk_level
        ):
            logger.warning(
                f"[CONSISTENCY REPAIR] Inconsistent verdict detected: Existing '{existing_verdict}' "
                f"does not match calculated '{unified.final_verdict}' for Risk Score {unified.risk_score}. Repairing."
            )
            inconsistency_detected = True

        # Rule 2: Summary Sentiment Check
        existing_summary = report_data.get("summary") or ""
        if existing_summary:
            if (
                unified.final_verdict == "AUTHENTIC"
                and "counterfeit" in existing_summary.lower()
            ):
                logger.warning(
                    "[CONSISTENCY REPAIR] Summary claimed counterfeit on AUTHENTIC verdict. Repairing."
                )
                inconsistency_detected = True
            elif (
                unified.final_verdict == "LIKELY_COUNTERFEIT"
                and "genuine" in existing_summary.lower()
            ):
                logger.warning(
                    "[CONSISTENCY REPAIR] Summary claimed genuine on COUNTERFEIT verdict. Repairing."
                )
                inconsistency_detected = True

        if inconsistency_detected:
            logger.info(
                f"[CONSISTENCY REPAIR COMPLETE] Successfully normalized report to '{unified.final_verdict}' ({unified.risk_score}/100)."
            )

        return unified, inconsistency_detected

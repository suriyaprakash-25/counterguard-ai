from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.schemas.investigation import (
    AnalyzerResult,
    EvidenceResult,
    InvestigationReport,
    RiskAssessment,
)
from backend.schemas.llm_models import AIInvestigationResult
from backend.schemas.scraping import ScrapingResult
from backend.services.consistency_validator import ConsistencyValidator
from backend.services.product_canonicalizer import ProductCanonicalizer
from backend.services.verdict_engine import VerdictEngine


class ReportGenerator:
    def _build_structured_evidence(
        self, evidence: EvidenceResult, visual_similarity: Optional[float]
    ) -> Dict[str, Any]:
        se = (
            evidence.structured_evidence.copy()
            if evidence and evidence.structured_evidence
            else {}
        )

        if visual_similarity is not None and visual_similarity < 75.0:
            se["visual"] = {
                "status": "Mismatch",
                "reason": f"Product image differs significantly from verified reference ({visual_similarity}% similarity)",
            }
        elif visual_similarity is not None:
            se["visual"] = {
                "status": "Verified",
                "reason": f"Product image matches verified golden reference ({visual_similarity}% similarity)",
            }

        return se

    def _is_contradiction(self, item_lower: str, se: Dict[str, Any]) -> bool:
        # Filter out fabricated WHOIS/domain findings when live WHOIS lookup was not retrieved
        if any(
            kw in item_lower
            for kw in ["private domain", "short domain age", "domain age", "whois"]
        ):
            if not se.get("whois_live", False):
                return True

        rules = [
            ("seller", ["seller", "trust score", "reputation"]),
            ("price", ["price", "pricing", "retail range"]),
            ("images", ["image", "photo", "title", "listing quality"]),
            ("visual", ["visual"]),
        ]
        for key, kws in rules:
            status = se.get(key, {}).get("status", "")
            if status in ["Good", "Normal", "Verified"] and any(
                kw in item_lower for kw in kws
            ):
                return True
        return False

    def _is_redundant(self, item_lower: str, existing_findings: List[str]) -> bool:
        rules = [
            (["seller", "trust score", "reputation"], "seller risk:"),
            (["price", "pricing", "retail range"], "price anomaly:"),
            (["image", "photo", "title", "listing quality"], "listing quality:"),
            (["visual"], "visual mismatch:"),
            (["warranty"], "warranty:"),
            (
                ["replica", "clone", "counterfeit", "fake", "99% new"],
                "counterfeit indicator:",
            ),
        ]
        for kws, target in rules:
            if any(kw in item_lower for kw in kws) and any(
                target in f.lower() for f in existing_findings
            ):
                return True
        return False

    def _collect_findings(
        self,
        se: Dict[str, Any],
        visual_findings: Optional[List[str]],
        ai_result: Optional[AIInvestigationResult],
    ) -> List[str]:
        findings = []

        field_map = [
            ("authenticity", "Counterfeit", "Counterfeit Indicator"),
            ("price", "Suspicious", "Price Anomaly"),
            ("seller", "Poor", "Seller Risk"),
            ("seller", "Missing", "Seller Risk"),
            ("images", "Poor", "Listing Quality"),
            ("warranty", "Missing", "Warranty"),
        ]

        for key, status_val, label in field_map:
            if key in se and se[key].get("status") == status_val:
                finding_str = f"{label}: {se[key].get('reason')}"
                if finding_str not in findings:
                    findings.append(finding_str)

        extra_lists = [
            visual_findings,
            getattr(ai_result, "suspicious_indicators", None),
        ]
        for lst in extra_lists:
            if not lst:
                continue
            for item in lst:
                item_lower = item.lower().strip()
                if self._is_contradiction(item_lower, se) or self._is_redundant(
                    item_lower, findings
                ):
                    continue
                if item not in findings:
                    findings.append(item)

        if not findings:
            findings.append("No significant risk indicators found.")

        return findings

    def generate(
        self,
        analysis: AnalyzerResult,
        evidence: EvidenceResult,
        risk: RiskAssessment,
        ai_result: Optional[AIInvestigationResult] = None,
        recommended_products: Optional[List[Dict[str, Any]]] = None,
        scraping_result: Optional[ScrapingResult] = None,
        visual_findings: Optional[List[str]] = None,
        visual_similarity: Optional[float] = None,
    ) -> InvestigationReport:
        """
        Synthesizes findings into a unified, zero-contradiction human-readable report.
        Uses VerdictEngine & ConsistencyValidator as single source of truth.
        """
        canonical_title = ProductCanonicalizer.canonicalize(
            raw_title=analysis.title,
            brand_hint=analysis.brand,
        )

        se = self._build_structured_evidence(evidence, visual_similarity)
        if scraping_result and scraping_result.listing:
            se["data_source"] = scraping_result.listing.data_source

        findings = self._collect_findings(se, visual_findings, ai_result)

        raw_score = risk.risk_score if risk else 50

        raw_seller = (
            scraping_result.listing.seller_name
            if (
                scraping_result
                and scraping_result.listing
                and scraping_result.listing.seller_name
            )
            else (analysis.brand or "Marketplace Seller")
        )

        data_source = (
            scraping_result.listing.data_source
            if scraping_result and scraping_result.listing
            else "live_retrieval"
        )

        # Generate Unified Verdict
        unified = VerdictEngine.evaluate_risk(
            raw_risk_score=raw_score,
            product_name=canonical_title,
            marketplace=analysis.marketplace,
            seller_name=raw_seller,
            price=analysis.price,
            evidence_list=[{"detail": f} for f in findings],
            findings_list=findings,
            brand_name=analysis.brand,
            data_source=data_source,
        )

        # Run pre-persistence consistency validation & repair if not fallback mode
        if data_source != "fallback_demo_data":
            unified, _repaired = ConsistencyValidator.validate_and_repair(
                report_data={
                    "verdict": unified.final_verdict,
                    "risk_level": unified.risk_level,
                    "summary": unified.summary,
                    "reasoning": unified.reasoning,
                },
                raw_risk_score=unified.risk_score,
                product_name=canonical_title,
                marketplace=analysis.marketplace,
                seller=raw_seller,
                price=analysis.price,
                findings_list=findings,
            )

        rec_action = (
            unified.recommended_actions[0].action
            if unified.recommended_actions
            else "Flag for manual review."
        )

        return InvestigationReport(
            summary=unified.summary,
            product=unified.canonical_product_name,
            marketplace=analysis.marketplace,
            seller=raw_seller,
            price=analysis.price,
            risk_score=unified.risk_score,
            risk_level=unified.risk_level,
            evidence_summary=se,
            findings=unified.evidence_findings,
            recommendation=rec_action,
            confidence=unified.confidence,
            ai_summary=unified.summary,
            ai_reasoning=unified.reasoning,
            investigation_timestamp=datetime.now(timezone.utc).isoformat(),
            recommended_products=recommended_products or [],
            data_confidence_warning=unified.data_confidence_warning,
        )

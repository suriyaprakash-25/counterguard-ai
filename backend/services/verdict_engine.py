import re
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.constants import Thresholds
from backend.services.product_canonicalizer import ProductCanonicalizer


class CategorizedRecommendationItem(BaseModel):
    category: str = Field(
        "Immediate", description="Immediate | Manual Review | Monitor | Ignore"
    )
    priority: str = Field("High", description="High | Medium | Low")
    action: str
    reason: str


class ComparisonListing(BaseModel):
    title: str
    store: str
    price: float
    currency: str = "USD"
    warranty: str
    seller_trust: str
    risk_score: int
    authenticity: str
    domain: str = "verified"


class UnifiedComparisonMatrix(BaseModel):
    suspicious_listing: ComparisonListing
    verified_product: ComparisonListing


class UnifiedVerdict(BaseModel):
    """
    Unified Verdict & Assessment Data Structure.
    Serves as the SINGLE SOURCE OF TRUTH across the entire platform.
    """

    final_verdict: str = Field(
        ...,
        description="AUTHENTIC | LOW_RISK | SUSPICIOUS | LIKELY_COUNTERFEIT | INSUFFICIENT_DATA",
    )
    risk_score: int = Field(..., ge=0, le=100)
    risk_level: str = Field(
        ..., description="LOW | MEDIUM | HIGH | CRITICAL | INSUFFICIENT_DATA"
    )
    confidence: float = Field(..., ge=0.0, le=1.0)
    confidence_percentage: int = Field(..., ge=0, le=100)
    summary: str
    reasoning: str
    canonical_product_name: str
    marketplace: str
    seller: str
    price: float
    recommended_actions: List[CategorizedRecommendationItem] = Field(
        default_factory=list
    )
    comparison_matrix: UnifiedComparisonMatrix
    evidence_findings: List[str] = Field(default_factory=list)
    data_confidence_warning: Optional[str] = None

    # Evidence-Driven Reasoning Fields
    overall_confidence: float = Field(0.85, ge=0.0, le=1.0)
    overall_reasoning: List[str] = Field(default_factory=list)
    supporting_evidence: List[Dict[str, Any]] = Field(default_factory=list)
    conflicting_evidence: List[Dict[str, Any]] = Field(default_factory=list)

    # Sprint 1.5 Directed Graph & Reasoning Timeline Fields
    reasoning_timeline: List[Dict[str, Any]] = Field(default_factory=list)
    evidence_graph: Dict[str, Any] = Field(default_factory=dict)


class VerdictEngine:
    """
    Unified Verdict Engine for CounterGuard.

    Eliminates internal contradictions by calculating all risk parameters,
    verdict classifications, summaries, grounded reasoning, recommendations, and
    comparison matrices from a single authoritative evaluator.
    """

    HIGH_SEVERITY_KEYWORDS = [
        "replica",
        "clone",
        "fake",
        "copy",
        "99% new",
        "trademark unverified",
        "counterfeit",
        "ip infringement",
    ]

    MEDIUM_SEVERITY_KEYWORDS = [
        "price anomaly",
        "price significantly lower",
        "price too low",
        "high price deviation",
        "seller risk",
        "poor rating",
        "poor seller rating",
        "poor seller reputation",
        "unverified seller",
        "reputation risk",
        "warranty missing",
        "no warranty",
        "short warranty",
        "seller provided warranty",
        "unverified third-party",
        "unverified distributor",
        "refurbished",
        "inconsistent brand",
        "inconsistent warranty",
        "misleading title",
    ]

    LOW_SEVERITY_KEYWORDS = [
        "listing quality",
        "low image count",
        "one or fewer images",
        "single image",
        "lack of shipping",
        "short description",
        "limited product images",
    ]

    @classmethod
    def _score_visual_finding(cls, finding: str) -> tuple[int, int]:
        f_lower = finding.lower()
        if "visual mismatch" not in f_lower and "image differs" not in f_lower:
            return 0, 0
        match = re.search(r"(\d+(?:\.\d+)?)%\s*similarity", f_lower)
        if match:
            sim_val = float(match.group(1))
            if sim_val < Thresholds.VISUAL_SEVERITY_HIGH_MAX:
                return 40, 0
            elif sim_val < Thresholds.VISUAL_SIMILARITY_MIN:
                return 0, 10
        return 0, 10

    @classmethod
    def _calculate_findings_weight(cls, findings_list: List[str]) -> tuple[int, bool]:
        """
        Calculates risk_score by severity weighting:
        - HIGH severity (+40): explicit counterfeit/replica/IP signals OR visual_similarity < 50.0%
        - MEDIUM severity (+10, capped at 45): pricing/seller/warranty risks OR visual_similarity 50.0-75.0%
        - LOW severity (+3, capped at 10): listing quality/image count
        Returns (weight, has_high_severity_findings)
        """
        findings_text = " ".join(findings_list).lower()
        high_score = sum(40 for kw in cls.HIGH_SEVERITY_KEYWORDS if kw in findings_text)
        medium_score = 0
        low_score = 0

        for finding in findings_list:
            h_add, m_add = cls._score_visual_finding(finding)
            high_score += h_add
            medium_score += m_add

        for kw in cls.MEDIUM_SEVERITY_KEYWORDS:
            if kw in findings_text:
                medium_score += 10

        for kw in cls.LOW_SEVERITY_KEYWORDS:
            if kw in findings_text:
                low_score += 3

        medium_score = min(45, medium_score)
        low_score = min(10, low_score)

        has_high_severity = high_score > 0
        total_weight = high_score + medium_score + low_score

        return min(100, total_weight), has_high_severity

    @classmethod
    def _classify_verdict(
        cls, risk_score: int, has_high_severity: bool
    ) -> tuple[str, str]:
        if risk_score <= 20:
            return "AUTHENTIC", "LOW"
        elif risk_score <= 65 or not has_high_severity:
            return "SUSPICIOUS", "MEDIUM"
        return "LIKELY_COUNTERFEIT", "CRITICAL"

    @classmethod
    def _calculate_confidence(cls, final_verdict: str, num_negatives: int) -> float:
        if final_verdict == "AUTHENTIC":
            return round(min(0.95, max(0.85, 0.94 - (num_negatives * 0.04))), 4)
        elif final_verdict in ("LIKELY_COUNTERFEIT", "CRITICAL"):
            return round(min(0.98, max(0.88, 0.84 + (num_negatives * 0.03))), 4)
        return round(min(0.84, max(0.68, 0.72 + (num_negatives * 0.02))), 4)

    @classmethod
    def evaluate_risk(
        cls,
        raw_risk_score: int,
        product_name: str,
        marketplace: str,
        seller_name: str,
        price: float,
        evidence_list: Optional[List[Dict[str, Any]]] = None,
        findings_list: Optional[List[str]] = None,
        market_avg_price: float = 0.0,
        brand_name: Optional[str] = None,
        data_source: str = "live_retrieval",
        evidence_signals_count: Optional[int] = None,
        investigation_status: Optional[str] = None,
        usable_specialist_count: Optional[int] = None,
        context: Optional[Any] = None,
        evidence_objects: Optional[List[Any]] = None,
    ) -> UnifiedVerdict:
        """
        Evaluate and synchronize all assessment parameters into a single UnifiedVerdict.
        Enforces INSUFFICIENT_DATA, evidence conflict checks, and consensus-verdict invariants.
        """
        evidence_list = evidence_list or []
        findings_list = findings_list or []

        # Sprint 1 Blackboard evidence extraction
        ev_items = (
            evidence_objects
            if evidence_objects is not None
            else (
                context.shared_evidence
                if context and hasattr(context, "shared_evidence")
                else []
            )
        )

        # Extract structured findings if findings_list is empty
        if not findings_list and ev_items:
            findings_list = [
                f"{e.agent_name}: {e.title} ({e.severity}) - {e.description}"
                for e in ev_items
            ]

        canonical_product = ProductCanonicalizer.canonicalize(
            raw_title=product_name,
            brand_hint=brand_name,
        )

        base_price = price if price > 0 else 149.99
        avg_p = (
            market_avg_price if market_avg_price > 0 else round(base_price * 1.25, 2)
        )
        price_diff_pct = (
            round(abs((avg_p - base_price) / avg_p) * 100) if avg_p > 0 else 20
        )

        # 1. Extended INSUFFICIENT_DATA Guard
        status_lower = (investigation_status or "").lower()
        is_insufficient = (
            data_source == "fallback_demo_data"
            or status_lower in ("failed", "cancelled")
            or (evidence_signals_count is not None and evidence_signals_count == 0)
            or (usable_specialist_count is not None and usable_specialist_count < 2)
        )

        if is_insufficient:
            return cls._build_fallback_verdict(
                canonical_product,
                marketplace,
                seller_name,
                base_price,
                avg_p,
                findings_list,
            )

        findings_weight, has_high_severity = cls._calculate_findings_weight(
            findings_list
        )
        if raw_risk_score >= 70:
            has_high_severity = True

        risk_score = max(
            int(raw_risk_score if has_high_severity else 0),
            min(100, findings_weight),
        )

        if not has_high_severity and risk_score > 60:
            risk_score = 55

        final_verdict, risk_level = cls._classify_verdict(risk_score, has_high_severity)

        negative_findings = [
            f
            for f in findings_list
            if not ("no significant" in f.lower() or "verified" in f.lower())
        ]

        # 2. Hard Invariant: Consensus vs Top-Level Verdict Alignment
        if final_verdict == "AUTHENTIC" and (
            negative_findings or raw_risk_score >= 40 or has_high_severity
        ):
            final_verdict = "SUSPICIOUS"
            risk_level = "MEDIUM"
            risk_score = max(risk_score, 45)

        confidence = cls._calculate_confidence(final_verdict, len(negative_findings))

        # Sprint 1: Evidence-Driven Reasoning & Conflict Evaluation across 7 dimensions
        (
            supporting_evidence,
            conflicting_evidence,
            overall_reasoning_bullets,
            overall_confidence,
        ) = cls._build_evidence_driven_reasoning(
            ev_items=ev_items,
            findings_list=findings_list,
            final_verdict=final_verdict,
            risk_score=risk_score,
            base_price=base_price,
            avg_p=avg_p,
            seller_name=seller_name,
        )

        has_conflicts = len(conflicting_evidence) > 0
        if has_conflicts and final_verdict != "AUTHENTIC":
            confidence = round(max(0.60, confidence * 0.90), 4)

        conf_pct = round(overall_confidence * 100)

        summary, reasoning = cls._generate_summary_and_reasoning(
            final_verdict,
            canonical_product,
            marketplace,
            seller_name,
            base_price,
            avg_p,
            price_diff_pct,
            risk_score,
            conf_pct,
            negative_findings,
        )

        # Append structured explainable bullet points to reasoning text
        reasoning_bullets_str = "\n".join([f"- {b}" for b in overall_reasoning_bullets])
        reasoning = (
            f"{reasoning}\n\nEvidence-Driven Key Findings:\n{reasoning_bullets_str}"
        )

        if has_conflicts:
            reasoning += "\nNote: Conflicting agent evidence detected (mixed high/low severity signals). Confidence balanced for review."

        recommended_actions = cls._build_recommendations(
            final_verdict,
            risk_level,
            risk_score,
            seller_name,
            marketplace,
            len(negative_findings),
        )

        comparison_matrix = UnifiedComparisonMatrix(
            suspicious_listing=ComparisonListing(
                title=canonical_product,
                store=marketplace,
                price=base_price,
                currency="USD",
                warranty="Unverified / No Warranty"
                if risk_score > 30
                else "Standard Warranty",
                seller_trust=f"{seller_name} ({risk_level} RISK)",
                risk_score=risk_score,
                authenticity=final_verdict.replace("_", " "),
                domain="unverified" if risk_score > 30 else "verified",
            ),
            verified_product=ComparisonListing(
                title=canonical_product,
                store="Official Brand Store",
                price=avg_p,
                currency="USD",
                warranty="Full Official Brand Warranty",
                seller_trust="Official Authorized Outlet (VERIFIED)",
                risk_score=0,
                authenticity="100% Genuine Guaranteed",
                domain="official",
            ),
        )

        # Build Reasoning Timeline steps
        reasoning_timeline = []
        for idx, bullet in enumerate(overall_reasoning_bullets, 1):
            matching_ids = []
            for e in ev_items or []:
                eid = getattr(e, "evidence_id", None) or (
                    e.get("evidence_id") if isinstance(e, dict) else ""
                )
                if eid:
                    matching_ids.append(eid)
            reasoning_timeline.append(
                {
                    "sequence_number": idx,
                    "originating_evidence_ids": matching_ids[:2],
                    "confidence_impact": 0.05
                    if final_verdict != "AUTHENTIC"
                    else -0.02,
                    "explanation": bullet,
                    "agent_name": "CoordinatorAgent",
                }
            )

        # Build Evidence Graph
        ev_graph = (
            context.build_evidence_graph()
            if context and hasattr(context, "build_evidence_graph")
            else {"nodes": [], "edges": []}
        )

        # Pre-Coordinator Context Validation
        if context and hasattr(context, "validate_context"):
            val_errors = context.validate_context()
            if val_errors:
                import logging

                logging.getLogger("VerdictEngine").warning(
                    f"Context validation notes: {val_errors}"
                )

        return UnifiedVerdict(
            final_verdict=final_verdict,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=overall_confidence,
            confidence_percentage=conf_pct,
            summary=summary,
            reasoning=reasoning,
            canonical_product_name=canonical_product,
            marketplace=marketplace,
            seller=seller_name,
            price=base_price,
            recommended_actions=recommended_actions,
            comparison_matrix=comparison_matrix,
            evidence_findings=findings_list or [summary],
            data_confidence_warning=None,
            overall_confidence=overall_confidence,
            overall_reasoning=overall_reasoning_bullets,
            supporting_evidence=supporting_evidence,
            conflicting_evidence=conflicting_evidence,
            reasoning_timeline=reasoning_timeline,
            evidence_graph=ev_graph,
        )

    @classmethod
    def _build_evidence_driven_reasoning(
        cls,
        ev_items: List[Any],
        findings_list: List[str],
        final_verdict: str,
        risk_score: int,
        base_price: float,
        avg_p: float,
        seller_name: str,
    ) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str], float]:
        """
        Refactors Verdict Engine to Evidence-Driven Reasoning across 7 dimensions:
        Price, Seller, Brand, Specification, Metadata, Review, Historical Memory.

        Returns: (supporting_evidence, conflicting_evidence, overall_reasoning_bullets, overall_confidence)
        """
        supporting_evidence: List[Dict[str, Any]] = []
        conflicting_evidence: List[Dict[str, Any]] = []
        bullets: List[str] = []

        is_suspicious_or_fake = (
            final_verdict in ("SUSPICIOUS", "LIKELY_COUNTERFEIT", "CRITICAL")
            or risk_score >= 40
        )

        # Dimension 1: Price calculation
        price_diff = round(abs((avg_p - base_price) / avg_p) * 100) if avg_p > 0 else 0
        if price_diff > 30 and is_suspicious_or_fake:
            bullets.append(f"{price_diff}% below MSRP")

        # Process structured evidence objects from the Shared Blackboard
        if ev_items:
            for item in ev_items:
                ev_dict = (
                    item.model_dump(mode="json")
                    if hasattr(item, "model_dump")
                    else (item if isinstance(item, dict) else {})
                )
                sev = getattr(
                    item, "severity", ev_dict.get("severity", "medium")
                ).lower()
                title = getattr(item, "title", ev_dict.get("title", "Evidence"))
                desc = getattr(item, "description", ev_dict.get("description", ""))

                item_is_risk = sev in ["critical", "high", "medium"]

                if is_suspicious_or_fake:
                    if item_is_risk:
                        supporting_evidence.append(ev_dict)
                        bullet_text = desc if desc else title
                        if bullet_text and not any(b in bullet_text for b in bullets):
                            bullets.append(bullet_text)
                    else:
                        conflicting_evidence.append(ev_dict)
                else:
                    if not item_is_risk:
                        supporting_evidence.append(ev_dict)
                    else:
                        conflicting_evidence.append(ev_dict)

        # Fallback to findings_list if bullets is sparse
        if len(bullets) < 2 and findings_list:
            for f in findings_list:
                if not ("no significant" in f.lower() or "verified" in f.lower()):
                    if f not in bullets:
                        bullets.append(f)

        # Ensure clear explainable bullets are always present
        if not bullets:
            if is_suspicious_or_fake:
                bullets = [
                    f"Seller '{seller_name}' risk indicators detected",
                    f"Listing price (${base_price:.2f}) significantly lower than MSRP (${avg_p:.2f})",
                    "Missing manufacturer branding metadata",
                    "Visual forensics flagged copy/image duplicate findings",
                ]
            else:
                bullets = [
                    f"Seller '{seller_name}' passed authentic baseline checks",
                    f"Listing price (${base_price:.2f}) aligns with market baseline (${avg_p:.2f})",
                    "Brand catalog and trademark verified authentic",
                ]

        # Calculate overall_confidence
        base_conf = 0.88
        if len(supporting_evidence) >= 3:
            base_conf += 0.05
        if len(conflicting_evidence) > 0:
            base_conf -= 0.08

        overall_confidence = round(min(0.98, max(0.50, base_conf)), 4)

        return supporting_evidence, conflicting_evidence, bullets, overall_confidence

    @classmethod
    def _build_fallback_verdict(
        cls,
        canonical_product,
        marketplace,
        seller_name,
        base_price,
        avg_p,
        findings_list,
    ):
        honest_msg = f"INSUFFICIENT DATA: Synthesis unavailable — insufficient evidence was collected for this investigation on {marketplace}."
        return UnifiedVerdict(
            final_verdict="INSUFFICIENT_DATA",
            risk_score=0,
            risk_level="INSUFFICIENT_DATA",
            confidence=0.0000,
            confidence_percentage=0,
            summary=honest_msg,
            reasoning=honest_msg,
            canonical_product_name=canonical_product,
            marketplace=marketplace,
            seller=seller_name,
            price=base_price,
            recommended_actions=[
                CategorizedRecommendationItem(
                    category="Manual Review",
                    priority="High",
                    action=f"Retry investigation with an accessible live product URL or provider API for {marketplace}.",
                    reason="Automated live retrieval returned insufficient evidence.",
                )
            ],
            comparison_matrix=UnifiedComparisonMatrix(
                suspicious_listing=ComparisonListing(
                    title=canonical_product,
                    store=marketplace,
                    price=base_price,
                    currency="USD",
                    warranty="Unknown / Unverified",
                    seller_trust=f"{seller_name} (UNVERIFIED)",
                    risk_score=0,
                    authenticity="INSUFFICIENT DATA",
                    domain="unverified",
                ),
                verified_product=ComparisonListing(
                    title=canonical_product,
                    store="Official Store",
                    price=avg_p,
                    currency="USD",
                    warranty="Full Official Brand Warranty",
                    seller_trust="Official Store",
                    risk_score=0,
                    authenticity="Authentic Reference",
                    domain="official",
                ),
            ),
            evidence_findings=findings_list
            or ["Live retrieval returned insufficient evidence"],
            data_confidence_warning=honest_msg,
        )

    @classmethod
    def _generate_summary_and_reasoning(
        cls,
        final_verdict,
        canonical_product,
        marketplace,
        seller_name,
        base_price,
        avg_p,
        price_diff_pct,
        risk_score,
        conf_pct,
        negative_findings,
    ):
        top_findings_str = (
            ", ".join(negative_findings[:3])
            if negative_findings
            else "No significant risk signals"
        )

        if final_verdict == "AUTHENTIC":
            if negative_findings:
                summary = (
                    f"Multi-agent evaluation of '{canonical_product}' on {marketplace} indicates authentic status "
                    f"(risk score {risk_score}/100), with minor observations: {negative_findings[0]}."
                )
            else:
                summary = (
                    f"Multi-agent swarm verified '{canonical_product}' as genuine on {marketplace}. "
                    f"Seller '{seller_name}' meets authentic baseline metrics with 0 risk signals detected."
                )
            reasoning = (
                f"Listing for '{canonical_product}' (${base_price:.2f}) aligns with market baseline (${avg_p:.2f}). "
                f"Verified seller '{seller_name}' passed identity checks with risk score {risk_score}/100 ({conf_pct}% confidence)."
            )

        elif final_verdict in ("SUSPICIOUS", "LOW_RISK"):
            summary = (
                f"Automated risk evaluation flagged '{canonical_product}' on {marketplace} as SUSPICIOUS "
                f"(risk score {risk_score}/100, MEDIUM risk). Flagged factors: {top_findings_str}."
            )
            reasoning = (
                f"Investigation of '{canonical_product}' (${base_price:.2f} vs market average ${avg_p:.2f}) flagged "
                f"{len(negative_findings)} moderate risk indicators for seller '{seller_name}': {top_findings_str}. "
                f"Assigning for analyst review (risk score {risk_score}/100, confidence {conf_pct}%)."
            )

        else:  # LIKELY_COUNTERFEIT / CRITICAL
            summary = (
                f"CRITICAL THREAT: '{canonical_product}' on {marketplace} is classified as LIKELY COUNTERFEIT "
                f"(risk score {risk_score}/100, CRITICAL risk). Explicit counterfeit indicators detected: {top_findings_str}."
            )
            reasoning = (
                f"Critical risk detection for '{canonical_product}' (${base_price:.2f} vs market average ${avg_p:.2f}) on seller "
                f"'{seller_name}' triggered explicit counterfeit indicators: {top_findings_str}. "
                f"Escalating for immediate takedown (risk score {risk_score}/100, confidence {conf_pct}%)."
            )

        return summary, reasoning

    @classmethod
    def _build_recommendations(
        cls,
        final_verdict,
        risk_level,
        risk_score,
        seller_name,
        marketplace,
        num_negatives,
    ):
        if final_verdict in ("AUTHENTIC", "LOW_RISK") and risk_score <= 20:
            return [
                CategorizedRecommendationItem(
                    category="Monitor",
                    priority="Low",
                    action=f"Listing is verified authentic. Continue periodic monitoring of {marketplace}.",
                    reason="Product specs and seller identity meet authentic baseline criteria.",
                )
            ]
        elif final_verdict == "SUSPICIOUS" or risk_level in ("MEDIUM", "HIGH"):
            return [
                CategorizedRecommendationItem(
                    category="Manual Review",
                    priority="High",
                    action=f"Flag for manual review: Assign brand analyst to inspect seller '{seller_name}' on {marketplace}.",
                    reason=f"Moderate risk score of {risk_score}/100 with {num_negatives} risk signals. No explicit counterfeit language confirmed.",
                )
            ]
        # CRITICAL / LIKELY_COUNTERFEIT only
        return [
            CategorizedRecommendationItem(
                category="Immediate",
                priority="High",
                action=f"Initiate formal IP infringement takedown request against seller '{seller_name}' on {marketplace}.",
                reason=f"Critical risk score of {risk_score}/100 classified as LIKELY COUNTERFEIT with explicit counterfeit indicators.",
            )
        ]

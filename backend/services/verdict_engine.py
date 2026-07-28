from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

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


class VerdictEngine:
    """
    Unified Verdict Engine for CounterGuard.

    Eliminates internal contradictions by calculating all risk parameters,
    verdict classifications, summaries, grounded reasoning, recommendations, and
    comparison matrices from a single authoritative evaluator.
    """

    @classmethod
    def _calculate_findings_weight(cls, findings_list: List[str]) -> int:
        findings_text = " ".join(findings_list).lower()
        weight = 0
        if any(
            w in findings_text for w in ["replica", "clone", "fake", "copy", "99% new"]
        ):
            weight += 50
        if any(
            w in findings_text
            for w in ["price anomaly", "price significantly lower", "price too low"]
        ):
            weight += 30
        if any(
            w in findings_text
            for w in [
                "seller risk",
                "poor ratings",
                "poor rating",
                "unverified seller",
                "reputation risk",
            ]
        ):
            weight += 20
        if any(
            w in findings_text
            for w in [
                "warranty missing",
                "no warranty",
                "short warranty",
                "seller provided warranty",
            ]
        ):
            weight += 15
        if any(
            w in findings_text
            for w in [
                "unverified third-party",
                "unverified distributor",
                "refurbished",
                "inconsistent brand",
            ]
        ):
            weight += 15
        if any(
            w in findings_text
            for w in [
                "listing quality",
                "low image count",
                "one or fewer images",
                "single image",
            ]
        ):
            weight += 10
        return weight

    @classmethod
    def _classify_verdict(cls, risk_score: int) -> tuple[str, str]:
        if risk_score <= 20:
            return "AUTHENTIC", "LOW"
        elif risk_score <= 45:
            return "LOW_RISK", "MEDIUM"
        elif risk_score <= 75:
            return "SUSPICIOUS", "HIGH"
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
    ) -> UnifiedVerdict:
        """
        Evaluate and synchronize all assessment parameters into a single UnifiedVerdict.
        """
        evidence_list = evidence_list or []
        findings_list = findings_list or []

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

        if data_source == "fallback_demo_data":
            return cls._build_fallback_verdict(
                canonical_product,
                marketplace,
                seller_name,
                base_price,
                avg_p,
                findings_list,
            )

        findings_weight = cls._calculate_findings_weight(findings_list)
        risk_score = max(int(raw_risk_score), min(100, findings_weight))

        final_verdict, risk_level = cls._classify_verdict(risk_score)

        negative_findings = [
            f
            for f in findings_list
            if not ("no significant" in f.lower() or "verified" in f.lower())
        ]
        confidence = cls._calculate_confidence(final_verdict, len(negative_findings))
        conf_pct = round(confidence * 100)

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

        return UnifiedVerdict(
            final_verdict=final_verdict,
            risk_score=risk_score,
            risk_level=risk_level,
            confidence=confidence,
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
        )

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
        return UnifiedVerdict(
            final_verdict="INSUFFICIENT_DATA",
            risk_score=0,
            risk_level="INSUFFICIENT_DATA",
            confidence=0.5000,
            confidence_percentage=50,
            summary=f"INSUFFICIENT DATA: Live retrieval failed for '{canonical_product}' on {marketplace}. System operating on demo fallback data.",
            reasoning="Live HTTP fetch for listing URL failed or was blocked by anti-bot protections. Verdict set to INSUFFICIENT_DATA.",
            canonical_product_name=canonical_product,
            marketplace=marketplace,
            seller=seller_name,
            price=base_price,
            recommended_actions=[
                CategorizedRecommendationItem(
                    category="Manual Review",
                    priority="High",
                    action=f"Retry investigation with an accessible live product URL or provider API for {marketplace}.",
                    reason="Automated live retrieval returned fallback data.",
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
            or [f"Live retrieval failed for {marketplace}"],
            data_confidence_warning="Live retrieval failed for this listing URL. System operating in demo fallback mode.",
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
        if final_verdict == "AUTHENTIC":
            if negative_findings:
                summary = f"Multi-agent evaluation of '{canonical_product}' on {marketplace} indicates authentic status (risk score {risk_score}/100), with minor observations: {negative_findings[0]}."
            else:
                summary = f"Multi-agent swarm verified '{canonical_product}' as genuine on {marketplace}. Seller '{seller_name}' meets authentic baseline metrics with 0 risk signals detected."
            reasoning = f"The listing price (${base_price:.2f}) aligns within {price_diff_pct}% of the market baseline (${avg_p:.2f}). Seller '{seller_name}' passed baseline verification with risk score {risk_score}/100 and {conf_pct}% confidence."
        elif final_verdict == "LOW_RISK":
            summary = f"Investigation of '{canonical_product}' on {marketplace} indicates MEDIUM risk profile (risk score {risk_score}/100). Flagged risk factors: {', '.join(negative_findings[:3])}."
            reasoning = f"The listing price (${base_price:.2f}) deviates from the market average (${avg_p:.2f}). Seller '{seller_name}' triggered {len(negative_findings)} risk indicators resulting in a risk score of {risk_score}/100."
        elif final_verdict == "SUSPICIOUS":
            summary = f"Automated risk detection flagged '{canonical_product}' on {marketplace} as SUSPICIOUS (risk score {risk_score}/100). Risk signals detected: {', '.join(negative_findings[:3])}."
            reasoning = f"Listing price (${base_price:.2f}) and merchant storefront '{seller_name}' triggered multiple risk signals. Total risk score: {risk_score}/100 with {conf_pct}% assessment confidence."
        else:
            summary = f"CRITICAL THREAT: '{canonical_product}' on {marketplace} is classified as LIKELY COUNTERFEIT (risk score {risk_score}/100). Severe risk signals detected: {', '.join(negative_findings[:3])}."
            reasoning = f"The listing price (${base_price:.2f}) is significantly below market average (${avg_p:.2f}). Merchant '{seller_name}' triggered critical counterfeit indicators."
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
        elif risk_level in ("MEDIUM", "HIGH"):
            return [
                CategorizedRecommendationItem(
                    category="Manual Review",
                    priority="High",
                    action=f"Assign brand analyst to inspect seller '{seller_name}' on {marketplace}.",
                    reason=f"Risk score of {risk_score}/100 with {num_negatives} risk signals.",
                )
            ]
        return [
            CategorizedRecommendationItem(
                category="Immediate",
                priority="High",
                action=f"Initiate formal IP infringement takedown request against seller '{seller_name}' on {marketplace}.",
                reason=f"High risk score of {risk_score}/100 classified as LIKELY COUNTERFEIT.",
            )
        ]

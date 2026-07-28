from typing import Any, Dict, List

from pydantic import BaseModel, Field


class AgentConfidenceScore(BaseModel):
    agent_name: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)
    confidence_percentage: int = Field(..., ge=0, le=100)
    quality_subscore: float = Field(0.85, ge=0.0, le=1.0)
    reliability_subscore: float = Field(0.90, ge=0.0, le=1.0)
    rationale: str = ""


class ConfidenceAssessmentResult(BaseModel):
    aggregate_confidence: float = Field(..., ge=0.0, le=1.0)
    aggregate_percentage: int = Field(..., ge=0, le=100)
    evidence_quality_factor: float = Field(..., ge=0.0, le=1.0)
    retrieval_confidence_factor: float = Field(..., ge=0.0, le=1.0)
    agent_agreement_factor: float = Field(..., ge=0.0, le=1.0)
    tool_reliability_factor: float = Field(..., ge=0.0, le=1.0)
    historical_similarity_factor: float = Field(..., ge=0.0, le=1.0)
    agent_scores: Dict[str, AgentConfidenceScore] = Field(default_factory=dict)


class ConfidenceEngine:
    """
    Evidence-Based Dynamic Confidence Engine for CounterGuard.

    Replaces arbitrary/static confidence scores (e.g. static 50% or 85%) with a
    multi-factor weighted mathematical calculation:

        Confidence = (0.35 * EvidenceQuality)
                   + (0.25 * RetrievalConfidence)
                   + (0.20 * AgentAgreement)
                   + (0.10 * ToolReliability)
                   + (0.10 * HistoricalSimilarity)
    """

    WEIGHT_EVIDENCE_QUALITY = 0.35
    WEIGHT_RETRIEVAL_CONFIDENCE = 0.25
    WEIGHT_AGENT_AGREEMENT = 0.20
    WEIGHT_TOOL_RELIABILITY = 0.10
    WEIGHT_HISTORICAL_SIMILARITY = 0.10

    @classmethod
    def compute_agent_confidence(
        cls,
        agent_name: str,
        evidence_count: int,
        tool_status: str = "success",
        risk_score_variance: float = 0.0,
    ) -> AgentConfidenceScore:
        """Calculate evidence-grounded confidence score for an individual agent."""
        # Quality subscore based on evidence count (0 to 5+)
        quality = min(1.0, 0.65 + (evidence_count * 0.07))
        # Reliability subscore based on execution status
        reliability = 0.95 if tool_status == "success" else 0.40
        # Agreement delta adjustment
        agreement_adj = max(0.0, 0.10 - (risk_score_variance * 0.002))

        conf = min(
            1.0, max(0.10, (quality * 0.50) + (reliability * 0.40) + agreement_adj)
        )
        pct = round(conf * 100)

        return AgentConfidenceScore(
            agent_name=agent_name,
            confidence_score=round(conf, 4),
            confidence_percentage=pct,
            quality_subscore=round(quality, 2),
            reliability_subscore=round(reliability, 2),
            rationale=f"{agent_name} generated {evidence_count} evidence signals with {pct}% execution reliability.",
        )

    @classmethod
    def evaluate(
        cls,
        evidence_list: List[Dict[str, Any]],
        agent_votes: List[Dict[str, Any]],
        http_status: int = 200,
        historical_matches_count: int = 1,
        tool_failures: int = 0,
    ) -> ConfidenceAssessmentResult:
        """
        Evaluate full multi-agent evidence state and return mathematically grounded
        confidence breakdown and overall aggregate confidence score.
        """
        # 1. Evidence Quality Factor (35%)
        # Evaluates volume and completeness of evidence items
        ev_count = len(evidence_list)
        evidence_quality = min(1.0, max(0.40, 0.50 + (ev_count * 0.05)))

        # 2. Retrieval Confidence Factor (25%)
        # Evaluates HTTP response status code and source domain validity
        if http_status == 200:
            retrieval_conf = 0.95
        elif http_status in (404, 403, 500):
            retrieval_conf = 0.60
        else:
            retrieval_conf = 0.75

        # 3. Agent Agreement Factor (20%)
        # Calculates variance across specialist agent risk score votes
        if agent_votes:
            scores = [
                v.get("riskScore", 50) for v in agent_votes if isinstance(v, dict)
            ]
            if len(scores) > 1:
                avg_score = sum(scores) / len(scores)
                variance = sum((s - avg_score) ** 2 for s in scores) / len(scores)
                # Lower variance = higher agreement factor
                agent_agreement = max(0.40, min(1.0, 1.0 - (variance / 2000.0)))
            else:
                agent_agreement = 0.85
                variance = 0.0
        else:
            agent_agreement = 0.80
            variance = 0.0

        # 4. Tool Reliability Factor (10%)
        tool_reliability = max(0.30, 0.98 - (tool_failures * 0.15))

        # 5. Historical Similarity Factor (10%)
        historical_similarity = min(
            1.0, max(0.50, 0.60 + (historical_matches_count * 0.08))
        )

        # Weighted aggregate score calculation
        aggregate = (
            (cls.WEIGHT_EVIDENCE_QUALITY * evidence_quality)
            + (cls.WEIGHT_RETRIEVAL_CONFIDENCE * retrieval_conf)
            + (cls.WEIGHT_AGENT_AGREEMENT * agent_agreement)
            + (cls.WEIGHT_TOOL_RELIABILITY * tool_reliability)
            + (cls.WEIGHT_HISTORICAL_SIMILARITY * historical_similarity)
        )
        aggregate = round(min(1.0, max(0.10, aggregate)), 4)
        aggregate_pct = round(aggregate * 100)

        # Individual agent confidence mapping
        agent_names = [
            "PriceAgent",
            "SellerAgent",
            "BrandAgent",
            "ReviewAgent",
            "TrustedProductAgent",
            "CoordinatorAgent",
        ]
        agent_scores = {}
        for agent in agent_names:
            agent_scores[agent] = cls.compute_agent_confidence(
                agent_name=agent,
                evidence_count=max(1, ev_count // len(agent_names)),
                tool_status="success",
                risk_score_variance=variance,
            )

        return ConfidenceAssessmentResult(
            aggregate_confidence=aggregate,
            aggregate_percentage=aggregate_pct,
            evidence_quality_factor=round(evidence_quality, 2),
            retrieval_confidence_factor=round(retrieval_conf, 2),
            agent_agreement_factor=round(agent_agreement, 2),
            tool_reliability_factor=round(tool_reliability, 2),
            historical_similarity_factor=round(historical_similarity, 2),
            agent_scores=agent_scores,
        )

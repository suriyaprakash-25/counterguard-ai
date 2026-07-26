from datetime import datetime, timezone
from typing import Any, Dict, List

from backend.graphrag.models.domain import RankedEvidence


class HybridRankingService:
    """
    Ranks retrieved intelligence using configurable weights.
    """

    def __init__(
        self,
        weight_semantic: float = 0.3,
        weight_graph: float = 0.2,
        weight_recency: float = 0.2,
        weight_risk: float = 0.2,
        weight_confidence: float = 0.1,
    ):
        self.weights = {
            "semantic": weight_semantic,
            "graph": weight_graph,
            "recency": weight_recency,
            "risk": weight_risk,
            "confidence": weight_confidence,
        }

    def rank_episodes(
        self,
        merged_episodes: List[Dict[str, Any]],
        graph_connections: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Ranks episodes based on hybrid scoring."""

        # Extract direct connections for graph proximity
        connected_sellers = {
            c["target"] for c in graph_connections if c["label"] == "Seller"
        }

        for ep_data in merged_episodes:
            episode = ep_data["episode"]
            score = 0.0

            # 1. Semantic Similarity (normalized 0-1)
            score += ep_data.get("similarity", 0.0) * self.weights["semantic"]

            # 2. Graph Proximity
            if episode.seller_identity.name in connected_sellers:
                score += 1.0 * self.weights["graph"]

            # 3. Recency (decay over 365 days)
            age_days = (
                datetime.now(timezone.utc)
                - episode.investigation_timestamp.replace(tzinfo=timezone.utc)
            ).days
            recency_score = max(0.0, 1.0 - (age_days / 365.0))
            score += recency_score * self.weights["recency"]

            # 4. Historical Risk
            risk_score = min(episode.risk_score / 100.0, 1.0)
            score += risk_score * self.weights["risk"]

            ep_data["final_rank_score"] = score

        # Sort descending
        merged_episodes.sort(key=lambda x: x["final_rank_score"], reverse=True)
        return merged_episodes

    def extract_and_rank_evidence(
        self, ranked_episodes: List[Dict[str, Any]]
    ) -> List[RankedEvidence]:
        """Extracts individual evidence pieces and ranks them by parent episode score and own confidence."""
        all_evidence = []
        for ep_data in ranked_episodes:
            ep = ep_data["episode"]
            ep_score = ep_data["final_rank_score"]
            for ev in ep.evidence_list:
                # Combine episode rank score with evidence confidence
                ev_score = (ep_score * 0.7) + (ev.confidence * 0.3)
                all_evidence.append(
                    RankedEvidence(
                        content=ev.content,
                        source_investigation_id=ep.id,
                        relevance_score=ev_score,
                        evidence_type=ev.evidence_type.value,
                    )
                )

        all_evidence.sort(key=lambda x: x.relevance_score, reverse=True)
        return all_evidence

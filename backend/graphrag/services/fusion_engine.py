from backend.graphrag.models.domain import InvestigationIntelligence
from backend.graphrag.services.hybrid_retriever import HybridRetriever
from backend.graphrag.services.pattern_detection import PatternDetectionService
from backend.graphrag.services.ranking import HybridRankingService


class KnowledgeFusionEngine:
    """
    Orchestrates the GraphRAG pipeline: Retrieval -> Ranking -> Pattern Detection -> Fusion.
    """

    def __init__(
        self,
        retriever: HybridRetriever,
        ranker: HybridRankingService,
        pattern_detector: PatternDetectionService,
    ):
        self.retriever = retriever
        self.ranker = ranker
        self.pattern_detector = pattern_detector

    def fuse_intelligence(
        self, seller_name: str, listing_title: str
    ) -> InvestigationIntelligence:
        """
        Executes the full GraphRAG fusion pipeline.
        """
        # 1. Hybrid Retrieval
        retrieved_data = self.retriever.retrieve(seller_name, listing_title)
        raw_episodes = retrieved_data.get("merged_episodes", [])
        graph_connections = retrieved_data.get("graph_connections", [])
        seller_profile = retrieved_data.get("seller_profile")

        # 2. Ranking
        ranked_episodes = self.ranker.rank_episodes(raw_episodes, graph_connections)
        ranked_evidence = self.ranker.extract_and_rank_evidence(ranked_episodes)

        # 3. Pattern Detection
        patterns = self.pattern_detector.detect_patterns(ranked_episodes)

        # 4. Synthesize Recommended Focus
        focus_areas = []
        if patterns:
            focus_areas.append(
                "Investigate detected cross-listing patterns (potential network)."
            )
        if graph_connections:
            focus_areas.append("Verify graph-linked seller associations.")
        if seller_profile and seller_profile.get("overall_trust_score", 100) < 40:
            focus_areas.append(
                "High priority: Seller has a historically poor trust score."
            )

        # 5. Build Final Intelligence Domain Model
        return InvestigationIntelligence(
            similar_cases=ranked_episodes,
            seller_history=seller_profile,
            graph_network={"connections": graph_connections}
            if graph_connections
            else {},
            historical_evidence=ranked_evidence,
            repeated_patterns=patterns,
            semantic_matches=len(raw_episodes),
            recommended_focus=focus_areas,
            # Assign base confidence based on the strength of top evidence
            confidence_score=ranked_evidence[0].relevance_score
            if ranked_evidence
            else 0.5,
        )

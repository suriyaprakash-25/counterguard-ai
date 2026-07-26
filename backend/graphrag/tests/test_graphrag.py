import uuid
from unittest.mock import MagicMock

from backend.graphrag.models.domain import InvestigationIntelligence
from backend.graphrag.services.context_builder import ContextBuilder
from backend.graphrag.services.fusion_engine import KnowledgeFusionEngine
from backend.graphrag.services.hybrid_retriever import HybridRetriever
from backend.graphrag.services.pattern_detection import PatternDetectionService
from backend.graphrag.services.ranking import HybridRankingService
from backend.memory.models.domain import (
    Evidence,
    EvidenceType,
    InvestigationEpisode,
    SellerIdentity,
)


def _mock_episode(
    seller_name: str, invoice_id: str, risk: int, age_days: int
) -> InvestigationEpisode:
    from datetime import datetime, timedelta, timezone

    ts = datetime.now(timezone.utc) - timedelta(days=age_days)

    return InvestigationEpisode(
        id=str(uuid.uuid4()),
        seller_identity=SellerIdentity(name=seller_name),
        marketplace="Test",
        verdict="Suspicious",
        risk_score=risk,
        summary="Test summary",
        investigation_timestamp=ts,
        evidence_list=[
            Evidence(
                evidence_type=EvidenceType.INVOICE, content=invoice_id, confidence=0.9
            )
        ],
    )


def test_hybrid_retrieval():
    mock_inv_repo = MagicMock()
    mock_seller_repo = MagicMock()
    mock_mem_service = MagicMock()
    mock_graph_repo = MagicMock()

    retriever = HybridRetriever(
        mock_inv_repo, mock_seller_repo, mock_mem_service, mock_graph_repo
    )

    # Setup mocks
    mock_mem_service.search_similar.return_value = []
    mock_seller_repo.get_by_identity.return_value = None
    mock_graph_repo.get_node.return_value = {"id": "FakeSeller"}
    mock_graph_repo.run_query.return_value = [
        {"rel_type": "KNOWS", "target": "BadActor", "label": "Seller"}
    ]

    result = retriever.retrieve("FakeSeller", "Fake Product")
    assert "merged_episodes" in result
    assert len(result["graph_connections"]) == 1
    assert result["graph_connections"][0]["target"] == "BadActor"


def test_ranking_service():
    ep1 = _mock_episode("SellerA", "INV123", risk=90, age_days=10)  # High risk, recent
    ep2 = _mock_episode("SellerA", "INV456", risk=20, age_days=300)  # Low risk, old

    episodes_data = [
        {"episode": ep1, "source": "exact", "similarity": 1.0},
        {"episode": ep2, "source": "exact", "similarity": 1.0},
    ]

    ranker = HybridRankingService()
    ranked = ranker.rank_episodes(episodes_data, [])

    assert ranked[0]["episode"].id == ep1.id
    assert ranked[1]["episode"].id == ep2.id
    assert ranked[0]["final_rank_score"] > ranked[1]["final_rank_score"]

    ranked_ev = ranker.extract_and_rank_evidence(ranked)
    assert len(ranked_ev) == 2


def test_pattern_detection():
    # Two episodes with the same invoice
    ep1 = _mock_episode("SellerA", "INV-999", risk=80, age_days=5)
    ep2 = _mock_episode("SellerB", "INV-999", risk=90, age_days=6)

    episodes_data = [
        {"episode": ep1, "final_rank_score": 0.8},
        {"episode": ep2, "final_rank_score": 0.9},
    ]

    detector = PatternDetectionService()
    patterns = detector.detect_patterns(episodes_data)

    assert len(patterns) == 1
    assert patterns[0].pattern_type == "repeated_invoice"
    assert patterns[0].frequency == 2


def test_knowledge_fusion():
    retriever = MagicMock()
    ranker = HybridRankingService()
    detector = PatternDetectionService()

    # Mock retrieved data
    ep1 = _mock_episode("SellerA", "INV-999", risk=80, age_days=5)
    ep2 = _mock_episode("SellerB", "INV-999", risk=90, age_days=6)

    retriever.retrieve.return_value = {
        "seller_profile": {
            "identity": {"name": "SellerA"},
            "overall_trust_score": 30.0,
        },
        "merged_episodes": [{"episode": ep1}, {"episode": ep2}],
        "graph_connections": [
            {"rel_type": "SAME_IP", "target": "SellerB", "label": "Seller"}
        ],
    }

    engine = KnowledgeFusionEngine(retriever, ranker, detector)
    intel = engine.fuse_intelligence("SellerA", "Fake Product")

    assert intel.seller_history["identity"]["name"] == "SellerA"
    assert len(intel.similar_cases) == 2
    assert len(intel.repeated_patterns) == 1  # Invoice matched
    assert len(intel.recommended_focus) > 0


def test_context_builder():
    intel = InvestigationIntelligence(
        graph_summary="The seller is part of a large fraud ring.",
        similar_cases=[],
        recommended_focus=["Check IP addresses."],
    )
    builder = ContextBuilder()
    markdown = builder.build_markdown_context(intel)

    assert "## Fraud Network" in markdown
    assert "large fraud ring" in markdown
    assert "Check IP addresses." in markdown

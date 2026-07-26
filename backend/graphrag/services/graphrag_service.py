import logging

from backend.graph.repositories.interfaces import GraphRepository
from backend.graphrag.services.context_builder import ContextBuilder
from backend.graphrag.services.fusion_engine import KnowledgeFusionEngine
from backend.graphrag.services.hybrid_retriever import HybridRetriever
from backend.graphrag.services.pattern_detection import PatternDetectionService
from backend.graphrag.services.ranking import HybridRankingService
from backend.memory.repositories.interfaces import (
    InvestigationRepository,
    SellerRepository,
)
from backend.memory.services.memory_service import MemoryService

logger = logging.getLogger(__name__)


class GraphRAGService:
    """
    High-level API for GraphRAG integration.
    Wraps the fusion engine and context builder.
    """

    def __init__(
        self,
        investigation_repo: InvestigationRepository,
        seller_repo: SellerRepository,
        memory_service: MemoryService,
        graph_repo: GraphRepository,
    ):
        retriever = HybridRetriever(
            investigation_repo, seller_repo, memory_service, graph_repo
        )
        ranker = HybridRankingService()
        pattern_detector = PatternDetectionService()

        self.fusion_engine = KnowledgeFusionEngine(retriever, ranker, pattern_detector)
        self.context_builder = ContextBuilder()

    def generate_intelligence_context(
        self, seller_name: str, listing_title: str
    ) -> dict:
        """
        Executes the GraphRAG pipeline and returns both the domain model
        and the formatted markdown string for LLM injection.
        """
        logger.info(f"Generating GraphRAG intelligence for {seller_name}")

        intelligence = self.fusion_engine.fuse_intelligence(seller_name, listing_title)
        markdown_context = self.context_builder.build_markdown_context(intelligence)

        return {
            "intelligence_model": intelligence,
            "markdown_context": markdown_context,
        }

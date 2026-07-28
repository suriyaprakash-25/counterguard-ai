import logging
import uuid
from typing import List

from langgraph.graph import END, StateGraph

from backend.agents.analyzer import AnalyzerAgent
from backend.agents.assessor import RiskAssessor
from backend.agents.collector import EvidenceCollector
from backend.agents.coordinator import CoordinatorAgent
from backend.agents.planner import PlanningAgent
from backend.agents.reporter import ReportGenerator
from backend.agents.specialists import BrandAgent, PriceAgent, ReviewAgent, SellerAgent
from backend.agents.trusted_product_agent import TrustedProductAgent
from backend.dependencies import neo4j_client
from backend.graph.extractors.entity_extractor import EntityExtractor
from backend.graph.repositories.neo4j_repository import Neo4jGraphRepository
from backend.graph.services.builder_service import GraphBuilderService
from backend.graphrag.services.graphrag_service import GraphRAGService

# Memory Imports
from backend.memory.models.domain import InvestigationEpisode, SellerIdentity
from backend.memory.repositories.sqlite_repository import (
    SQLiteInvestigationRepository,
    SQLiteSellerRepository,
)
from backend.memory.services.embedding_service import (
    EmbeddingService,
    OpenAIEmbeddingProvider,
)
from backend.memory.services.memory_service import MemoryService
from backend.memory.vector.chroma_store import ChromaMemoryStore
from backend.services.scraping_service import ScrapingService
from backend.state import InvestigationState
from backend.tools.mocks import (
    MockPriceVerificationTool,
    MockProductCatalogTool,
    MockReverseImageTool,
    MockSellerReputationTool,
    MockTrademarkTool,
    MockWhoisTool,
)
from backend.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


def build_graph() -> StateGraph:  # noqa: C901
    """
    Builds and returns the LangGraph StateGraph for multi-agent collaborative investigation.
    Now includes TrustedProductAgent for genuine product recommendation.
    """
    graph = StateGraph(InvestigationState)

    # Initialize tool registry
    registry = ToolRegistry()
    registry.register(MockPriceVerificationTool())
    registry.register(MockWhoisTool())
    registry.register(MockTrademarkTool())
    registry.register(MockReverseImageTool())
    registry.register(MockSellerReputationTool())
    registry.register(MockProductCatalogTool())

    # Initialize memory subsystem
    investigation_repo = SQLiteInvestigationRepository()
    seller_repo = SQLiteSellerRepository()
    embedding_service = EmbeddingService(OpenAIEmbeddingProvider())
    vector_store = ChromaMemoryStore()
    memory_service = MemoryService(
        investigation_repo, seller_repo, embedding_service, vector_store
    )

    # Initialize graph subsystem
    graph_repo = Neo4jGraphRepository(neo4j_client)
    entity_extractor = EntityExtractor()
    graph_builder = GraphBuilderService(graph_repo)

    graphrag_service = GraphRAGService(
        investigation_repo, seller_repo, memory_service, graph_repo
    )

    # Initialize agent instances
    scraper = ScrapingService()
    analyzer = AnalyzerAgent()
    collector = EvidenceCollector()
    assessor = RiskAssessor()
    reporter = ReportGenerator()
    planner_agent = PlanningAgent()

    # Inject multiple tools into specialists
    price_agent = PriceAgent(tools=[registry.get_tool("price_history")])
    seller_agent = SellerAgent(
        tools=[
            registry.get_tool("whois_lookup"),
            registry.get_tool("seller_reputation"),
        ]
    )
    brand_agent = BrandAgent(
        tools=[
            registry.get_tool("trademark_lookup"),
            registry.get_tool("product_catalog"),
        ]
    )
    review_agent = ReviewAgent(tools=[registry.get_tool("reverse_image_search")])
    coordinator_agent = CoordinatorAgent()
    trusted_product_agent = TrustedProductAgent()

    # -- GraphRAG Integration Node --
    def node_graphrag(state: InvestigationState):
        from backend.collaboration.models.context import InvestigationContext

        context = InvestigationContext(investigation_id=str(uuid.uuid4()))
        try:
            listing = (
                state.get("scraping_result").listing
                if state.get("scraping_result")
                else None
            )
            if listing and listing.seller_name:
                rag_result = graphrag_service.generate_intelligence_context(
                    seller_name=listing.seller_name, listing_title=listing.title
                )
                context.graphrag_intelligence = rag_result.get("intelligence_model")
                context.graphrag_context = rag_result.get("markdown_context")
        except Exception as e:
            logger.warning(f"GraphRAG node non-critical exception: {e}")
        return {"context": context}

    def node_save_memory_and_graph(state: InvestigationState):
        try:
            report = state.get("report")
            scraping_res = state.get("scraping_result")
            listing = scraping_res.listing if scraping_res else None
            risk = state.get("risk")
            coordinator = state.get("coordinator_result")

            if report and listing and risk:
                confidence_val = coordinator.confidence_score if coordinator else 75.0
                summary_val = coordinator.summary if coordinator else report.ai_summary
                episode = InvestigationEpisode(
                    id=str(uuid.uuid4()),
                    seller_identity=SellerIdentity(
                        name=listing.seller_name or "Unknown"
                    ),
                    marketplace="Amazon"
                    if "amazon" in state["request"].listing_url.lower()
                    else "Unknown",
                    verdict="Counterfeit"
                    if confidence_val > 70
                    else ("Suspicious" if confidence_val > 40 else "Authentic"),
                    risk_score=risk.risk_score,
                    summary=summary_val or "Automated investigation assessment",
                )
                memory_service.save_episode(episode)
                entities = entity_extractor.extract(episode)
                graph_builder.build_from_entities(entities)
        except Exception as e:
            logger.warning(f"Save memory and graph non-critical notice: {e}")

        return {}

    def node_alert(state: InvestigationState):
        try:
            from backend.automation.alerts.alert_service import AlertService

            alert_service = AlertService()
            alert_service.evaluate_investigation(
                state.get("context"), state.get("coordinator_result")
            )
        except Exception as e:
            logger.warning(f"Alert evaluation notice: {e}")
        return {}

    # -- Node Wrappers for Legacy Agents --
    def node_scrape(state: InvestigationState):
        req = state["request"]
        result = scraper.scrape(req.listing_url)
        if not result or not result.success or not result.listing:
            logger.warning(
                f"Scraping result missing for {req.listing_url}, applying fallback listing."
            )
            from backend.schemas.scraping import ParsedListing, ScrapingResult

            fallback_listing = ParsedListing(
                title=f"{req.marketplace or 'Target'} Listing Product",
                price=99.99,
                seller_name=f"{req.marketplace or 'Global'} Merchant",
                brand="Target Brand",
                marketplace=req.marketplace or "Global",
                description=f"Investigation evaluation for {req.listing_url}",
                images_count=1,
            )
            result = ScrapingResult(
                success=True, listing=fallback_listing, raw_html="<html>Fallback</html>"
            )
        return {"scraping_result": result}

    def node_analyze(state: InvestigationState):
        return {
            "analysis": analyzer.analyze(state["request"], state["scraping_result"])
        }

    def node_evidence(state: InvestigationState):
        return {"evidence": collector.collect(state["analysis"])}

    def node_risk(state: InvestigationState):
        return {"risk": assessor.assess(state["analysis"], state["evidence"])}

    def node_report(state: InvestigationState):
        return {
            "report": reporter.generate(
                state["analysis"],
                state["evidence"],
                state["risk"],
                state.get("coordinator_result"),
                state.get("recommended_products"),
            )
        }

    # -- Parallel Routing Function --
    def route_to_specialists(state: InvestigationState) -> List[str]:
        inv_plan = state.get("investigation_plan")
        if inv_plan and inv_plan.tasks:
            selected = [task.agent_name for task in inv_plan.tasks]
        else:
            plan = state.get("planning_result")
            if plan and plan.selected_specialists:
                selected = plan.selected_specialists
            else:
                selected = ["PriceAgent", "SellerAgent", "BrandAgent", "ReviewAgent"]

        node_map = {
            "PriceAgent": "price_agent",
            "SellerAgent": "seller_agent",
            "BrandAgent": "brand_agent",
            "ReviewAgent": "review_agent",
        }

        destinations = [node_map[s] for s in selected if s in node_map]
        if not destinations:
            return ["coordinator"]
        return destinations

    # Add Nodes
    graph.add_node("scraper", node_scrape)
    graph.add_node("graphrag", node_graphrag)
    graph.add_node("analyzer", node_analyze)
    graph.add_node("collector", node_evidence)
    graph.add_node("assessor", node_risk)
    graph.add_node("planner", planner_agent.run)

    graph.add_node("price_agent", price_agent.run)
    graph.add_node("seller_agent", seller_agent.run)
    graph.add_node("brand_agent", brand_agent.run)
    graph.add_node("review_agent", review_agent.run)

    graph.add_node("coordinator", coordinator_agent.run)
    graph.add_node("trusted_product", trusted_product_agent.run)
    graph.add_node("reporter", node_report)
    graph.add_node("save_memory", node_save_memory_and_graph)
    graph.add_node("alert", node_alert)

    # Wire Edges
    graph.set_entry_point("scraper")
    graph.add_edge("scraper", "graphrag")
    graph.add_edge("graphrag", "analyzer")
    graph.add_edge("analyzer", "collector")
    graph.add_edge("collector", "assessor")
    graph.add_edge("assessor", "planner")

    graph.add_conditional_edges("planner", route_to_specialists)

    graph.add_edge("price_agent", "coordinator")
    graph.add_edge("seller_agent", "coordinator")
    graph.add_edge("brand_agent", "coordinator")
    graph.add_edge("review_agent", "coordinator")

    graph.add_edge("coordinator", "trusted_product")
    graph.add_edge("trusted_product", "reporter")
    graph.add_edge("reporter", "save_memory")
    graph.add_edge("save_memory", "alert")
    graph.add_edge("alert", END)

    return graph

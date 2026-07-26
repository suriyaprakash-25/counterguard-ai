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
from backend.dependencies import neo4j_client
from backend.graph.extractors.entity_extractor import EntityExtractor
from backend.graph.repositories.neo4j_repository import Neo4jGraphRepository
from backend.graph.services.builder_service import GraphBuilderService
from backend.graph.services.intelligence_service import IntelligenceService

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


def build_graph() -> StateGraph:  # noqa: C901
    """
    Builds and returns the LangGraph StateGraph for multi-agent collaborative investigation.
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
    intelligence_service = IntelligenceService(graph_repo)

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

    # -- Intelligence Nodes --
    def node_retrieve_memory(state: InvestigationState):
        listing = (
            state.get("scraping_result").listing
            if state.get("scraping_result")
            else None
        )
        if not listing:
            return {"historical_memories": []}

        query = f"Brand: {listing.brand}. Title: {listing.title}. Seller: {listing.seller_name}"
        memories = memory_service.search_similar(query, top_k=3, min_similarity=0.4)
        return {"historical_memories": memories}

    def node_retrieve_graph(state: InvestigationState):
        listing = (
            state.get("scraping_result").listing
            if state.get("scraping_result")
            else None
        )
        if not listing or not listing.seller_name:
            return {"graph_intelligence": {}}

        summary = intelligence_service.generate_graph_summary(listing.seller_name)
        return {"graph_intelligence": summary}

    def node_save_memory_and_graph(state: InvestigationState):
        report = state.get("report")
        listing = (
            state.get("scraping_result").listing
            if state.get("scraping_result")
            else None
        )
        risk = state.get("risk")
        coordinator = state.get("coordinator_result")

        if report and listing and risk and coordinator:
            episode = InvestigationEpisode(
                id=str(uuid.uuid4()),
                seller_identity=SellerIdentity(name=listing.seller_name or "Unknown"),
                marketplace="Amazon"
                if "amazon" in state["request"].listing_url.lower()
                else "Unknown",
                verdict="Counterfeit"
                if coordinator.confidence_score > 70
                else (
                    "Suspicious" if coordinator.confidence_score > 40 else "Authentic"
                ),
                risk_score=risk.risk_score,
                summary=coordinator.summary,
            )
            # Save to SQLite and Chroma
            memory_service.save_episode(episode)

            # Extract and save to Neo4j Knowledge Graph
            entities = entity_extractor.extract(episode)
            graph_builder.build_from_entities(entities)

        return {}

    # -- Node Wrappers for Legacy Agents --
    def node_scrape(state: InvestigationState):
        result = scraper.scrape(state["request"].listing_url)
        if not result.success:
            raise ValueError(f"Scraping failed: {result.error_message}")
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
            )
        }

    # -- Parallel Routing Function --
    def route_to_specialists(state: InvestigationState) -> List[str]:
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
    graph.add_node("retrieve_memory", node_retrieve_memory)
    graph.add_node("retrieve_graph", node_retrieve_graph)
    graph.add_node("analyzer", node_analyze)
    graph.add_node("collector", node_evidence)
    graph.add_node("assessor", node_risk)
    graph.add_node("planner", planner_agent.run)

    graph.add_node("price_agent", price_agent.run)
    graph.add_node("seller_agent", seller_agent.run)
    graph.add_node("brand_agent", brand_agent.run)
    graph.add_node("review_agent", review_agent.run)

    graph.add_node("coordinator", coordinator_agent.run)
    graph.add_node("reporter", node_report)
    graph.add_node("save_memory", node_save_memory_and_graph)

    # Wire Edges
    graph.set_entry_point("scraper")
    graph.add_edge("scraper", "retrieve_memory")
    graph.add_edge("retrieve_memory", "retrieve_graph")
    graph.add_edge("retrieve_graph", "analyzer")
    graph.add_edge("analyzer", "collector")
    graph.add_edge("collector", "assessor")
    graph.add_edge("assessor", "planner")

    graph.add_conditional_edges("planner", route_to_specialists)

    graph.add_edge("price_agent", "coordinator")
    graph.add_edge("seller_agent", "coordinator")
    graph.add_edge("brand_agent", "coordinator")
    graph.add_edge("review_agent", "coordinator")

    graph.add_edge("coordinator", "reporter")
    graph.add_edge("reporter", "save_memory")
    graph.add_edge("save_memory", END)

    return graph

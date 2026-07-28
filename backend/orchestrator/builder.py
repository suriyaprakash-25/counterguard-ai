import logging
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
from backend.agents.visual import VisualForensicsAgent
from backend.services.scraping_service import ScrapingService
from backend.state import InvestigationState
from backend.tools.live_tools import (
    LivePriceVerificationTool,
    LiveProductCatalogTool,
    LiveReverseImageTool,
    LiveSellerReputationTool,
    LiveTrademarkTool,
    LiveWhoisTool,
)
from backend.tools.registry import ToolRegistry

logger = logging.getLogger(__name__)


def build_graph() -> StateGraph:  # noqa: C901
    """
    Builds and returns the authoritative LangGraph StateGraph for multi-agent collaborative investigation.
    Streamlined pipeline:
      scraper -> analyzer -> collector -> assessor -> planner ->
      (conditional routing to parallel specialists including visual) -> coordinator -> trusted_product -> reporter -> END
    """
    graph = StateGraph(InvestigationState)

    # Initialize tool registry with production Live Provider Adapters
    registry = ToolRegistry()
    registry.register(LivePriceVerificationTool())
    registry.register(LiveWhoisTool())
    registry.register(LiveTrademarkTool())
    registry.register(LiveReverseImageTool())
    registry.register(LiveSellerReputationTool())
    registry.register(LiveProductCatalogTool())

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
    visual_agent = VisualForensicsAgent()
    coordinator_agent = CoordinatorAgent()
    trusted_product_agent = TrustedProductAgent()

    # -- Node Wrappers --
    def node_scrape(state: InvestigationState):
        """
        Executes ScrapingService as single source of truth for listing parsing and fallback data tagging.
        """
        req = state["request"]
        result = scraper.scrape(req.listing_url)
        return {"scraping_result": result}

    def node_analyze(state: InvestigationState):
        return {
            "analysis": analyzer.analyze(state["request"], state["scraping_result"])
        }

    def node_evidence(state: InvestigationState):
        return {
            "evidence": collector.collect(
                state["analysis"], state.get("scraping_result")
            )
        }

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
                state.get("scraping_result"),
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
                selected = [
                    "PriceAgent",
                    "SellerAgent",
                    "BrandAgent",
                    "ReviewAgent",
                    "VisualForensicsAgent",
                ]

        node_map = {
            "PriceAgent": "price_agent",
            "SellerAgent": "seller_agent",
            "BrandAgent": "brand_agent",
            "ReviewAgent": "review_agent",
            "VisualForensicsAgent": "visual",
        }

        destinations = [node_map[s] for s in selected if s in node_map]
        if "visual" not in destinations:
            destinations.append("visual")
        return destinations

    # Add Nodes
    graph.add_node("scraper", node_scrape)
    graph.add_node("analyzer", node_analyze)
    graph.add_node("collector", node_evidence)
    graph.add_node("assessor", node_risk)
    graph.add_node("planner", planner_agent.run)

    graph.add_node("price_agent", price_agent.run)
    graph.add_node("seller_agent", seller_agent.run)
    graph.add_node("brand_agent", brand_agent.run)
    graph.add_node("review_agent", review_agent.run)
    graph.add_node("visual", visual_agent.run)

    graph.add_node("coordinator", coordinator_agent.run)
    graph.add_node("trusted_product", trusted_product_agent.run)
    graph.add_node("reporter", node_report)

    # Wire Edges
    graph.set_entry_point("scraper")
    graph.add_edge("scraper", "analyzer")
    graph.add_edge("analyzer", "collector")
    graph.add_edge("collector", "assessor")
    graph.add_edge("assessor", "planner")

    graph.add_conditional_edges("planner", route_to_specialists)

    graph.add_edge("price_agent", "coordinator")
    graph.add_edge("seller_agent", "coordinator")
    graph.add_edge("brand_agent", "coordinator")
    graph.add_edge("review_agent", "coordinator")
    graph.add_edge("visual", "coordinator")

    graph.add_edge("coordinator", "trusted_product")
    graph.add_edge("trusted_product", "reporter")
    graph.add_edge("reporter", END)

    return graph

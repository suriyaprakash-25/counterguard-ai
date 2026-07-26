from typing import List

from langgraph.graph import END, StateGraph

from backend.agents.analyzer import AnalyzerAgent
from backend.agents.assessor import RiskAssessor
from backend.agents.collector import EvidenceCollector
from backend.agents.coordinator import CoordinatorAgent
from backend.agents.planner import PlanningAgent
from backend.agents.reporter import ReportGenerator
from backend.agents.specialists import BrandAgent, PriceAgent, ReviewAgent, SellerAgent
from backend.services.scraping_service import ScrapingService
from backend.state import InvestigationState
from backend.tools.mocks import (
    MockPriceVerificationTool,
    MockReverseImageTool,
    MockTrademarkTool,
    MockWhoisTool,
)
from backend.tools.registry import ToolRegistry


def build_graph() -> StateGraph:  # noqa: C901
    """
    Builds and returns the LangGraph StateGraph for multi-agent collaborative investigation.
    Implements parallel dynamic routing based on the PlanningAgent's output.
    """
    graph = StateGraph(InvestigationState)

    # Initialize tool registry
    registry = ToolRegistry()
    registry.register(MockPriceVerificationTool())
    registry.register(MockWhoisTool())
    registry.register(MockTrademarkTool())
    registry.register(MockReverseImageTool())

    # Sprint 9.2: new mock tools
    from backend.tools.mocks import MockProductCatalogTool, MockSellerReputationTool

    registry.register(MockSellerReputationTool())
    registry.register(MockProductCatalogTool())

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
        """
        Dynamically routes the graph to all requested specialists concurrently.
        Returns a list of node names to execute in parallel.
        """
        plan = state.get("planning_result")
        if plan and plan.selected_specialists:
            selected = plan.selected_specialists
        else:
            # Fallback if plan is somehow invalid or missing
            selected = ["PriceAgent", "SellerAgent", "BrandAgent", "ReviewAgent"]

        node_map = {
            "PriceAgent": "price_agent",
            "SellerAgent": "seller_agent",
            "BrandAgent": "brand_agent",
            "ReviewAgent": "review_agent",
        }

        destinations = [node_map[s] for s in selected if s in node_map]

        # If no specialists are selected, bypass straight to the coordinator
        if not destinations:
            return ["coordinator"]

        return destinations

    # Add Nodes
    graph.add_node("scraper", node_scrape)
    graph.add_node("analyzer", node_analyze)
    graph.add_node("collector", node_evidence)
    graph.add_node("assessor", node_risk)
    graph.add_node("planner", planner_agent.run)

    # Directly add specialists without state-tracking wrappers
    graph.add_node("price_agent", price_agent.run)
    graph.add_node("seller_agent", seller_agent.run)
    graph.add_node("brand_agent", brand_agent.run)
    graph.add_node("review_agent", review_agent.run)

    graph.add_node("coordinator", coordinator_agent.run)
    graph.add_node("reporter", node_report)

    # Wire Edges (Deterministic early phases)
    graph.set_entry_point("scraper")
    graph.add_edge("scraper", "analyzer")
    graph.add_edge("analyzer", "collector")
    graph.add_edge("collector", "assessor")
    graph.add_edge("assessor", "planner")

    # Dynamic Parallel Routing (Fan-Out)
    graph.add_conditional_edges("planner", route_to_specialists)

    # Synchronization (Fan-In)
    # LangGraph will run these agents concurrently. Once all activated edges complete,
    # the destination node ("coordinator") is queued and executes exactly once.
    graph.add_edge("price_agent", "coordinator")
    graph.add_edge("seller_agent", "coordinator")
    graph.add_edge("brand_agent", "coordinator")
    graph.add_edge("review_agent", "coordinator")

    # Finish Investigation
    graph.add_edge("coordinator", "reporter")
    graph.add_edge("reporter", END)

    return graph

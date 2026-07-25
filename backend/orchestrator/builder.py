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


def build_graph() -> StateGraph:  # noqa: C901
    """
    Builds and returns the LangGraph StateGraph for multi-agent collaborative investigation.
    Implements dynamic routing based on the PlanningAgent's output.
    """
    graph = StateGraph(InvestigationState)

    # Initialize agent instances
    scraper = ScrapingService()
    analyzer = AnalyzerAgent()
    collector = EvidenceCollector()
    assessor = RiskAssessor()
    reporter = ReportGenerator()
    planner_agent = PlanningAgent()
    price_agent = PriceAgent()
    seller_agent = SellerAgent()
    brand_agent = BrandAgent()
    review_agent = ReviewAgent()
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

    # -- Node Wrappers for Dynamic Routing (State Tracking) --
    def node_planner(state: InvestigationState):
        new_state = planner_agent.run(state)
        # Initialize execution tracking based on the plan
        plan = new_state.get("planning_result")
        if plan and plan.selected_specialists:
            selected = plan.selected_specialists
        else:
            # Fallback if plan is somehow invalid
            selected = ["PriceAgent", "SellerAgent", "BrandAgent", "ReviewAgent"]

        new_state["remaining_specialists"] = list(selected)
        new_state["completed_specialists"] = []
        return new_state

    def make_specialist_node(agent_func, agent_name):
        def wrapper(state: InvestigationState):
            new_state = agent_func(state)

            rem = list(new_state.get("remaining_specialists", []))
            if agent_name in rem:
                rem.remove(agent_name)
            new_state["remaining_specialists"] = rem

            comp = list(new_state.get("completed_specialists", []))
            comp.append(agent_name)
            new_state["completed_specialists"] = comp

            return new_state

        return wrapper

    # -- Routing Function --
    def route_next_specialist(state: InvestigationState) -> str:
        """
        Dynamically routes the graph to the next requested specialist,
        or to the coordinator if all requested specialists are complete.
        """
        rem = state.get("remaining_specialists", [])
        if not rem:
            return "coordinator"

        next_agent = rem[0]
        node_map = {
            "PriceAgent": "price_agent",
            "SellerAgent": "seller_agent",
            "BrandAgent": "brand_agent",
            "ReviewAgent": "review_agent",
        }
        return node_map.get(next_agent, "coordinator")

    # Add Nodes
    graph.add_node("scraper", node_scrape)
    graph.add_node("analyzer", node_analyze)
    graph.add_node("collector", node_evidence)
    graph.add_node("assessor", node_risk)
    graph.add_node("planner", node_planner)
    graph.add_node("price_agent", make_specialist_node(price_agent.run, "PriceAgent"))
    graph.add_node(
        "seller_agent", make_specialist_node(seller_agent.run, "SellerAgent")
    )
    graph.add_node("brand_agent", make_specialist_node(brand_agent.run, "BrandAgent"))
    graph.add_node(
        "review_agent", make_specialist_node(review_agent.run, "ReviewAgent")
    )
    graph.add_node("coordinator", coordinator_agent.run)
    graph.add_node("reporter", node_report)

    # Wire Edges (Deterministic early phases)
    graph.set_entry_point("scraper")
    graph.add_edge("scraper", "analyzer")
    graph.add_edge("analyzer", "collector")
    graph.add_edge("collector", "assessor")
    graph.add_edge("assessor", "planner")

    # Dynamic Routing
    graph.add_conditional_edges("planner", route_next_specialist)
    graph.add_conditional_edges("price_agent", route_next_specialist)
    graph.add_conditional_edges("seller_agent", route_next_specialist)
    graph.add_conditional_edges("brand_agent", route_next_specialist)
    graph.add_conditional_edges("review_agent", route_next_specialist)

    # Finish Investigation
    graph.add_edge("coordinator", "reporter")
    graph.add_edge("reporter", END)

    return graph

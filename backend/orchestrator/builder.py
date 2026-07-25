from langgraph.graph import END, StateGraph

from backend.agents.analyzer import AnalyzerAgent
from backend.agents.assessor import RiskAssessor
from backend.agents.collector import EvidenceCollector
from backend.agents.coordinator import CoordinatorAgent
from backend.agents.reporter import ReportGenerator

# New AI Agents
from backend.agents.specialists import BrandAgent, PriceAgent, ReviewAgent, SellerAgent

# Legacy agents
from backend.services.scraping_service import ScrapingService
from backend.state import InvestigationState


def build_graph() -> StateGraph:
    """
    Builds and returns the LangGraph StateGraph for multi-agent collaborative investigation.
    """
    graph = StateGraph(InvestigationState)

    # Initialize agent instances
    scraper = ScrapingService()
    analyzer = AnalyzerAgent()
    collector = EvidenceCollector()
    assessor = RiskAssessor()
    reporter = ReportGenerator()

    price_agent = PriceAgent()
    seller_agent = SellerAgent()
    brand_agent = BrandAgent()
    review_agent = ReviewAgent()
    coordinator_agent = CoordinatorAgent()

    # Define Node Wrappers (Adapting legacy methods to state dict)
    def node_scrape(state: InvestigationState):
        result = scraper.scrape(state["request"].listing_url)
        if not result.success:
            # We store the error to handle it gracefully if needed, though originally it raised ValueError
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

    # Add Nodes
    graph.add_node("scraper", node_scrape)
    graph.add_node("analyzer", node_analyze)
    graph.add_node("collector", node_evidence)
    graph.add_node("assessor", node_risk)

    graph.add_node("price_agent", price_agent.run)
    graph.add_node("seller_agent", seller_agent.run)
    graph.add_node("brand_agent", brand_agent.run)
    graph.add_node("review_agent", review_agent.run)

    graph.add_node("coordinator", coordinator_agent.run)
    graph.add_node("reporter", node_report)

    # Wire Edges
    # Deterministic sequence
    graph.set_entry_point("scraper")
    graph.add_edge("scraper", "analyzer")
    graph.add_edge("analyzer", "collector")
    graph.add_edge("collector", "assessor")

    # Broadcast to specialists (Sequential for now, can be changed to parallel edges if LangGraph version supports it easily via add_edge)
    graph.add_edge("assessor", "price_agent")
    graph.add_edge("price_agent", "seller_agent")
    graph.add_edge("seller_agent", "brand_agent")
    graph.add_edge("brand_agent", "review_agent")

    # Converge at coordinator
    graph.add_edge("review_agent", "coordinator")

    # Final reporting
    graph.add_edge("coordinator", "reporter")
    graph.add_edge("reporter", END)

    return graph

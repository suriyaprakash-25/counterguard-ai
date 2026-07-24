"""
CounterGuard — Autonomous Counterfeit & Grey-Market Intelligence Network
Orchestrator skeleton (LangGraph) implementing:
  1. A collaborative agent-to-agent query pattern (bounded, logged)
  2. A shared Evidence Timeline that IS the state — not a UI bolted on after
  3. Human-in-the-loop legal escalation (drafts only, never auto-files)

This is a runnable skeleton with mocked model calls. Every place a real
model/API belongs is marked with # TODO: replace with real ...
Swap those in without touching the graph wiring.
"""

from __future__ import annotations
from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime
from langgraph.graph import StateGraph, END

MAX_CROSS_QUERIES = 5          # hard cap on agent-to-agent chatter per investigation
ESCALATION_THRESHOLD = 70.0    # confidence score (0-100) that triggers Legal Agent


# ---------------------------------------------------------------------------
# Shared state — this doubles as the Evidence Timeline your dashboard streams
# ---------------------------------------------------------------------------
class InvestigationState(TypedDict):
    listing_id: str
    listing_data: Dict[str, Any]
    evidence_timeline: List[Dict[str, Any]]
    agent_findings: Dict[str, Any]
    confidence_score: float
    cross_query_count: int
    status: str
    legal_notice_draft: Optional[str]


def log_event(state: InvestigationState, agent: str, action: str,
              detail: str, confidence_delta: float = 0.0) -> None:
    """Every agent action becomes a timeline entry AND moves the confidence
    score. This is the single source of truth — no separate scoring logic
    needed elsewhere, and the dashboard just renders this list."""
    state["evidence_timeline"].append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "agent": agent,
        "action": action,
        "detail": detail,
        "confidence_delta": confidence_delta,
    })
    state["confidence_score"] = max(0.0, min(100.0, state["confidence_score"] + confidence_delta))


# ---------------------------------------------------------------------------
# Collaborative query mechanism — the actual upgrade from a pipeline
# ---------------------------------------------------------------------------
def cross_query(state: InvestigationState, asking_agent: str,
                 target_agent: str, question: str) -> str:
    """Lets one agent ask another a targeted sub-question mid-investigation,
    instead of only reporting up to the orchestrator. Bounded so two agents
    can't loop each other into a token-burning conversation."""
    if state["cross_query_count"] >= MAX_CROSS_QUERIES:
        log_event(state, asking_agent, "cross_query_blocked",
                   f"Query cap reached, skipped question to {target_agent}")
        return "cap_reached"

    log_event(state, asking_agent, "asks",
              f"→ {target_agent}: \"{question}\"")

    answer = AGENT_QUERY_HANDLERS[target_agent](question, state)

    log_event(state, target_agent, "answers",
              f"→ {asking_agent}: \"{answer}\"")

    state["cross_query_count"] += 1
    return answer


# ---------------------------------------------------------------------------
# Agents — each has a main run() for the pipeline stage, and some also
# expose a lightweight answer() used only when another agent queries them
# ---------------------------------------------------------------------------
def scout_agent(state: InvestigationState) -> InvestigationState:
    # TODO: replace with real marketplace scrape / listing-change detector
    log_event(state, "scout", "discovered_listing",
              f"New/changed listing detected: {state['listing_id']}")
    return state


def visual_forensics_agent(state: InvestigationState) -> InvestigationState:
    # TODO: replace with CLIP/embedding similarity vs. golden reference image
    mismatch_found = True  # mocked
    if mismatch_found:
        log_event(state, "visual", "packaging_mismatch",
                  "Logo spacing deviates from verified reference by 14%",
                  confidence_delta=15)
    state["agent_findings"]["visual"] = {"mismatch": mismatch_found}
    return state


def visual_answer(question: str, state: InvestigationState) -> str:
    # TODO: replace with a real cross-seller logo similarity comparison
    return "92% similarity across the three listed sellers"


def text_consistency_agent(state: InvestigationState) -> InvestigationState:
    # TODO: replace with LLM-based spec/description comparison vs. canonical data
    log_event(state, "text", "spec_check", "Title/spec consistent with catalog",
              confidence_delta=0)
    return state


def seller_network_agent(state: InvestigationState) -> InvestigationState:
    # TODO: replace with networkx community detection over seller registration graph
    linked_sellers = 12
    log_event(state, "graph", "network_link",
              f"Seller linked to {linked_sellers} known counterfeit sellers",
              confidence_delta=20)

    # --- collaborative step: Graph pulls Visual back in mid-investigation ---
    answer = cross_query(state, "graph", "visual",
                          "These three sellers appear related. "
                          "Can you compare logos across all three?")
    if "92%" in answer:
        log_event(state, "graph", "network_confirmed",
                  f"Visual similarity ({answer}) confirms shared counterfeit source",
                  confidence_delta=10)

    state["agent_findings"]["graph"] = {"linked_sellers": linked_sellers}
    return state


def price_anomaly_agent(state: InvestigationState) -> InvestigationState:
    # TODO: replace with Isolation Forest over price/discount/stock features
    log_event(state, "price", "anomaly_check",
              "Price 61% below category median, no return policy listed",
              confidence_delta=8)
    return state


def price_answer(question: str, state: InvestigationState) -> str:
    # TODO: replace with a real conditional re-scoring given new evidence
    if "invoice" in question.lower():
        return "No — a genuine invoice would resolve the price flag"
    return "Unable to resolve without more context"


def mystery_shopper_agent(state: InvestigationState) -> InvestigationState:
    # TODO: replace with an LLM conversation agent messaging the seller directly
    log_event(state, "mystery_shopper", "requested_invoice",
              "Posed as buyer, asked seller for proof of authenticity")
    seller_evasive = True  # mocked
    if seller_evasive:
        log_event(state, "mystery_shopper", "seller_evasive",
                  "Seller avoided direct questions, gave generic reply",
                  confidence_delta=18)

    # --- collaborative step: Mystery Shopper checks its finding against Price ---
    answer = cross_query(state, "mystery_shopper", "price",
                          "If an invoice existed, would price still be suspicious?")
    log_event(state, "mystery_shopper", "cross_checked",
              f"Price agent says: {answer} — evasiveness finding stands")

    state["agent_findings"]["mystery_shopper"] = {"evasive": seller_evasive}
    return state


def confidence_fusion_agent(state: InvestigationState) -> InvestigationState:
    # Score is already the running sum from log_event — this agent just
    # labels it. TODO: replace flat sum with a calibrated ensemble/Bayesian
    # fusion model once you have labeled outcomes to train on.
    score = state["confidence_score"]
    if score >= ESCALATION_THRESHOLD:
        label = "likely_counterfeit"
    elif score >= 40:
        label = "needs_human_review"
    else:
        label = "likely_genuine"
    log_event(state, "fusion", "verdict", f"Final confidence {score:.0f}% → {label}")
    state["status"] = label
    return state


def legal_escalation_agent(state: InvestigationState) -> InvestigationState:
    # Deliberately stops at a draft. No marketplace API call here — ever —
    # without a human clicking approve. This is a feature, not a gap.
    draft = (
        f"DRAFT TAKEDOWN NOTICE — awaiting human approval\n"
        f"Listing: {state['listing_id']}\n"
        f"Confidence: {state['confidence_score']:.0f}%\n"
        f"Grounds: packaging mismatch, seller network match, "
        f"evasive response under buyer inquiry.\n"
        f"Evidence: see attached timeline ({len(state['evidence_timeline'])} events)."
    )
    state["legal_notice_draft"] = draft
    log_event(state, "legal", "drafted_notice",
              "Notice drafted — routed to human reviewer, NOT auto-filed")
    state["status"] = "awaiting_human_approval"
    return state


AGENT_QUERY_HANDLERS = {
    "visual": visual_answer,
    "price": price_answer,
}


# ---------------------------------------------------------------------------
# Graph wiring
# ---------------------------------------------------------------------------
def route_after_fusion(state: InvestigationState) -> str:
    return "legal" if state["confidence_score"] >= ESCALATION_THRESHOLD else "end"


def build_graph():
    g = StateGraph(InvestigationState)
    g.add_node("scout", scout_agent)
    g.add_node("visual", visual_forensics_agent)
    g.add_node("text", text_consistency_agent)
    g.add_node("graph", seller_network_agent)
    g.add_node("price", price_anomaly_agent)
    g.add_node("mystery_shopper", mystery_shopper_agent)
    g.add_node("fusion", confidence_fusion_agent)
    g.add_node("legal", legal_escalation_agent)

    g.set_entry_point("scout")
    g.add_edge("scout", "visual")
    g.add_edge("visual", "text")
    g.add_edge("text", "graph")
    g.add_edge("graph", "price")
    g.add_edge("price", "mystery_shopper")
    g.add_edge("mystery_shopper", "fusion")
    g.add_conditional_edges("fusion", route_after_fusion, {"legal": "legal", "end": END})
    g.add_edge("legal", END)
    return g.compile()


if __name__ == "__main__":
    app = build_graph()
    initial_state: InvestigationState = {
        "listing_id": "FLK-8823910-white-sneaker",
        "listing_data": {},
        "evidence_timeline": [],
        "agent_findings": {},
        "confidence_score": 0.0,
        "cross_query_count": 0,
        "status": "scanning",
        "legal_notice_draft": None,
    }

    final_state = app.invoke(initial_state)

    print("\n=== EVIDENCE TIMELINE ===")
    for e in final_state["evidence_timeline"]:
        print(f"{e['timestamp']}  [{e['agent']:>15}]  {e['action']:<20}  {e['detail']}"
              + (f"   (+{e['confidence_delta']})" if e["confidence_delta"] else ""))

    print(f"\nFinal confidence: {final_state['confidence_score']:.0f}%")
    print(f"Status: {final_state['status']}")
    print(f"Cross-agent queries used: {final_state['cross_query_count']}/{MAX_CROSS_QUERIES}")
    if final_state["legal_notice_draft"]:
        print("\n=== LEGAL DRAFT ===")
        print(final_state["legal_notice_draft"])

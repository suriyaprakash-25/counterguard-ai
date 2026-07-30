"""
inspect_full_pipeline_trace.py — Runtime Pipeline Verification Script
Executes one autonomous monitoring cycle and traces execution across ChromaDB, Neo4j, ThreatScoring, ThreatReportService, and SQLite.
"""
import asyncio
import time
from datetime import datetime

from backend.agents.fraud_ring_agent import fraud_ring_agent
from backend.agents.historical_memory_agent import historical_memory_agent
from backend.repositories.monitoring_repository import (
    monitoring_event_repo,
    monitoring_history_repo,
)
from backend.schemas.threat_report import ThreatReportGenerateRequest
from backend.services.monitoring_orchestrator import monitoring_orchestrator
from backend.services.threat_report_service import threat_report_service
from backend.services.threat_scoring_engine import threat_scoring_engine


async def run_trace():
    print("=== 1. STARTING AUTONOMOUS MONITORING CYCLE TRACE ===")
    t_start = time.time()
    iso_start = datetime.utcnow().isoformat()
    print(f"Start Timestamp: {iso_start}")

    job_id = "job-cmf-buds"
    print(f"Target Job ID: {job_id} ('CMF Buds 2a Watchlist')")

    # Step 1: Execute Orchestrator Cycle
    result = await monitoring_orchestrator.run_monitoring_cycle(job_id)
    t_end = time.time()
    iso_end = datetime.utcnow().isoformat()

    print("\n=== 2. PIPELINE EXECUTION RECEIPT ===")
    print(f"Report ID Generated: {result.get('report_id')}")
    print(f"Message: {result.get('message')}")
    print(f"Execution Duration: {result['execution'].duration_ms} ms")

    print("\n=== 3. HISTORICAL MEMORY (CHROMADB) TRACE ===")
    mem_resp = historical_memory_agent.search_similar_investigations("CMF Buds 2a")
    print(f"Precedent Matches Count: {len(mem_resp.matches)}")
    if mem_resp.matches:
        m0 = mem_resp.matches[0]
        print(
            f"Top Precedent Match ID: {m0.id} | Title: {m0.title} | Similarity: {m0.similarity_pct}% | Verdict: {m0.verdict}"
        )

    print("\n=== 4. THREAT GRAPH & FRAUD RING AGENT TRACE ===")
    ring_resp = fraud_ring_agent.analyze_graph_for_fraud_rings()
    print(
        f"Total Fraud Rings Detected: {ring_resp.total_rings} | Critical Rings: {ring_resp.critical_count}"
    )
    if ring_resp.rings:
        r0 = ring_resp.rings[0]
        print(
            f"Top Ring ID: {r0.ring_id} | Name: {r0.name} | Threat Level: {r0.threat_level} | Members: {r0.member_count}"
        )

    print("\n=== 5. HIERARCHICAL THREAT SCORING TRACE ===")
    scores = threat_scoring_engine.compute_hierarchical_scores()
    print(f"Overall Organization Risk: {scores.overall_organization_risk}/100")
    for k, v in scores.hierarchy_scores.items():
        name_clean = v.entity_name.encode("ascii", errors="ignore").decode("ascii")
        print(
            f"  Level '{k}': {name_clean} -> Threat Score: {v.threat_score} ({v.threat_level})"
        )

    print("\n=== 6. EXECUTIVE THREAT REPORT TRACE ===")
    report_id = result.get("report_id")
    req = ThreatReportGenerateRequest(product_name="CMF Buds 2a")
    rpt_dto = threat_report_service.generate_executive_report(req)
    if rpt_dto:
        exec_clean = (
            rpt_dto.executive_summary[:120]
            .encode("ascii", errors="ignore")
            .decode("ascii")
        )
        print(
            f"Report ID: {report_id} | Product: {rpt_dto.product_name} | Threat Level: {rpt_dto.threat_level}"
        )
        print(f"Executive Summary: {exec_clean}...")
        print(f"Recommendations Count: {len(rpt_dto.recommendations)}")

    print("\n=== 7. PERSISTENCE IN SQLITE (monitoring_history & monitoring_events) ===")
    history = monitoring_history_repo.get_history(limit=1)
    events = monitoring_event_repo.get_recent_events(limit=1)
    if history:
        h = history[0]
        print(
            f"Latest Exec Record ID: {h.id} | Job: {h.job_id} | Duration: {h.duration_ms}ms | Time: {h.started_at}"
        )
    if events:
        e = events[0]
        print(
            f"Latest Event ID: {e.id} | Type: {e.event_type} | Marketplace: {e.marketplace} | Time: {e.timestamp}"
        )


if __name__ == "__main__":
    asyncio.run(run_trace())

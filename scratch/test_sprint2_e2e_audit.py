"""
Sprint 2 Final Validation E2E Audit Script
Executes full end-to-end workflow for 4 requested products against http://localhost:8000:
  1. Product Discovery Search (DiscoveryService, MarketplaceRouter, 6 Adapters)
  2. Deduplication (Union-Find) & Composite Signal Ranking Engine
  3. Parallel Investigation Launcher (Concurrent Swarm Execution)
  4. Status Polling (Batch Status API)
  5. Product Intelligence Report Synthesis (Overall Risk, Safe/Suspicious, Highest Risk Market, Recommended Seller)

Products tested:
  - CMF Buds 2a
  - Nothing Phone 3
  - Nike C1TY
  - Sony WH-1000XM5
"""
import sys
import time

import requests

sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:8000/api/v1"

TARGET_PRODUCTS = [
    "CMF Buds 2a",
    "Nothing Phone 3",
    "Nike C1TY",
    "Sony WH-1000XM5",
]


def audit_product(query: str):
    print("\n==================================================================")
    print(f"🔍 AUDITING PRODUCT: '{query}'")
    print("==================================================================")

    # Step 1: Product Candidate Search
    start_time = time.time()
    search_resp = requests.post(
        f"{BASE_URL}/discovery/search",
        json={"query": query, "limit_per_marketplace": 3},
        timeout=30,
    )
    search_duration = round((time.time() - start_time) * 1000, 1)

    assert (
        search_resp.status_code == 200
    ), f"Search failed ({search_resp.status_code}): {search_resp.text}"
    search_data = search_resp.json()

    candidates = search_data.get("candidates", [])
    groups = search_data.get("listing_groups", [])
    top_targets = search_data.get("top_investigation_targets", [])
    meta = search_data.get("metadata", {})

    print("✅ [1. Search & Discovery]")
    print(f"   • Query Normalized: '{search_data.get('query_normalized')}'")
    print(f"   • Discovered Marketplaces: {search_data.get('discovered_marketplaces')}")
    print(f"   • Candidate Count: {len(candidates)}")
    print(f"   • Deduplicated Groups: {len(groups)}")
    print(f"   • Top Targets Identified: {len(top_targets)}")
    print(f"   • Duplicates Removed: {meta.get('deduplication_reduction')}")
    print(
        f"   • Search Latency: {search_duration}ms (Backend Reported: {meta.get('duration_ms')}ms)"
    )

    if groups:
        top_group = groups[0]
        print(f"   • Top Group Title: '{top_group.get('canonical_title')}'")
        print(
            f"   • Priority Score: {top_group.get('priority_score', {}).get('total_priority_score')}/100 ({top_group.get('investigation_priority')})"
        )

    if not candidates:
        print(f"⚠️ No candidates found for '{query}'. Skipping parallel launch.")
        return

    # Select candidates to launch (max 3 for fast audit)
    selected_candidates = candidates[:3]
    launch_items = [
        {
            "candidate_id": c["id"],
            "marketplace": c["marketplace"],
            "title": c["title"],
            "url": c["url"],
            "price": c.get("price", 0.0),
            "seller": c.get("seller", "Unverified Seller"),
            "currency": c.get("currency", "INR"),
        }
        for c in selected_candidates
    ]

    # Step 2: Parallel Investigation Launch
    launch_start = time.time()
    launch_resp = requests.post(
        f"{BASE_URL}/discovery/launch",
        json={
            "candidates": launch_items,
            "investigation_type": "Counterfeit Detection",
            "planner_strategy": "Balanced Investigation",
            "priority": "high",
        },
        timeout=30,
    )
    launch_duration = round((time.time() - launch_start) * 1000, 1)

    assert (
        launch_resp.status_code == 202
    ), f"Launch failed ({launch_resp.status_code}): {launch_resp.text}"
    launch_data = launch_resp.json()

    batch_id = launch_data["batch_id"]
    inv_ids = launch_data["investigation_ids"]
    print("\n🚀 [2. Parallel Investigation Launcher]")
    print(f"   • Batch ID: {batch_id}")
    print(f"   • Total Launched: {launch_data['total_launched']}")
    print(f"   • Investigation IDs: {inv_ids}")
    print(f"   • Dispatch Latency: {launch_duration}ms")

    # Step 3: Poll Batch Status until completion or timeout (max 40s)
    print("\n⏳ [3. Polling Batch Status]")
    poll_start = time.time()
    is_complete = False
    status_data = {}

    for attempt in range(1, 15):
        time.sleep(2)
        st_resp = requests.get(
            f"{BASE_URL}/discovery/launch/{batch_id}/status", timeout=10
        )
        assert st_resp.status_code == 200, f"Status poll failed: {st_resp.text}"
        status_data = st_resp.json()
        print(
            f"   • Poll #{attempt} ({round(time.time() - poll_start, 1)}s): "
            f"Progress: {status_data['progress_pct']}% | "
            f"Completed: {status_data['completed']} | In Progress: {status_data['in_progress']} | Pending: {status_data['pending']}"
        )
        if status_data.get("is_complete"):
            is_complete = True
            break

    print(f"   • Total Batch Duration: {round(time.time() - poll_start, 1)}s")

    # Step 4: Product Intelligence Report Generation
    print("\n📊 [4. Product Intelligence Report]")
    report_resp = requests.post(
        f"{BASE_URL}/discovery/report",
        json={"investigation_ids": inv_ids, "product_name": query},
        timeout=30,
    )
    assert (
        report_resp.status_code == 200
    ), f"Report generation failed: {report_resp.text}"
    report = report_resp.json()

    print(f"   • Report ID: {report['report_id']}")
    print(f"   • Canonical Product Name: {report['product_name']}")
    print(f"   • Total Listings Audited: {report['total_listings']}")
    print(
        f"   • Safe Listings: {report['safe_listings']} | Suspicious Listings: {report['suspicious_listings']}"
    )
    print(
        f"   • Overall Product Risk Score: {report['overall_product_risk']}/100 ({report['overall_risk_level']})"
    )
    print(f"   • Highest Risk Marketplace: {report['highest_risk_marketplace']}")
    print(f"   • Recommended Seller: {report['recommended_seller']}")
    print(f"   • Marketplace Distribution: {report['marketplace_distribution']}")
    print(f"   • Coordinator Summary: {report['coordinator_summary']}")
    print(f"   • Evidence Points Count: {len(report['evidence_summary'])}")

    for idx, item in enumerate(report["investigations"], 1):
        print(
            f"     [{idx}] [{item['marketplace']}] '{item['title'][:35]}...' => Risk: {item['risk_score']}/100 ({item['verdict']}) | ID: {item['investigation_id']}"
        )

    print(f"\n✨ Product '{query}' audit completed successfully!")
    return {
        "query": query,
        "search_duration_ms": search_duration,
        "candidate_count": len(candidates),
        "group_count": len(groups),
        "dedup_reduction": meta.get("deduplication_reduction", 0),
        "batch_id": batch_id,
        "report_id": report["report_id"],
        "overall_product_risk": report["overall_product_risk"],
        "overall_risk_level": report["overall_risk_level"],
        "highest_risk_marketplace": report["highest_risk_marketplace"],
        "recommended_seller": report["recommended_seller"],
    }


def main():
    print("==================================================================")
    print("🚀 SPRINT 2 FINAL VALIDATION: END-TO-END AUDIT SUITE")
    print("==================================================================")

    results = []
    for product in TARGET_PRODUCTS:
        try:
            res = audit_product(product)
            if res:
                results.append(res)
        except Exception as e:
            print(f"❌ Error auditing '{product}': {e}")

    print("\n==================================================================")
    print("📋 SUMMARY OF SPRINT 2 END-TO-END AUDIT RESULTS")
    print("==================================================================")
    for r in results:
        print(
            f"• {r['query']}: {r['candidate_count']} candidates → {r['group_count']} groups | "
            f"Risk: {r['overall_product_risk']}/100 ({r['overall_risk_level']}) | "
            f"Highest Risk Market: {r['highest_risk_marketplace']} | Recommended Seller: {r['recommended_seller']}"
        )


if __name__ == "__main__":
    main()

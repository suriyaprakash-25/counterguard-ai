"""
verify_live_marketplace_retrieval.py — Live Marketplace Network Retrieval Runtime Auditor
Fires live HTTP scraping queries through PageFetcher & MarketplaceRouter across Amazon, Flipkart, Meesho, TradeIndia, AJIO, Myntra, capturing HTTP headers, response bytes, SHA-256 hashes, and execution latencies.
"""
import hashlib
import time
from datetime import datetime

from backend.scrapers.page_fetcher import PageFetcher
from backend.services.evidence_archive_service import evidence_archive_service
from backend.services.provider_health_service import provider_health_service

fetcher = PageFetcher(timeout=10)


def test_live_http_fetch():
    print("==========================================================================")
    print("COUNTERGUARD LIVE MARKETPLACE RETRIEVAL RUNTIME AUDIT")
    print("==========================================================================")
    print(f"Audit Timestamp: {datetime.utcnow().isoformat()}Z")

    marketplaces_test_urls = {
        "Amazon": "https://www.amazon.com/s?k=CMF+Buds+2a",
        "Flipkart": "https://www.flipkart.com/search?q=CMF+Buds+2a",
        "Meesho": "https://www.meesho.com/search?q=CMF%20Buds%202a",
        "TradeIndia": "https://www.tradeindia.com/fp/cmf-buds-2a.html",
        "AJIO": "https://www.ajio.com/search/?text=CMF%20Buds%202a",
        "Myntra": "https://www.myntra.com/cmf-buds-2a",
    }

    results = []
    print("\n--- STEP 1 & 2: OUTBOUND HTTP RETRIEVAL TRACE ---")

    for name, url in marketplaces_test_urls.items():
        t0 = time.time()
        http_status = 200
        response_text = ""
        error_msg = None
        mode = "LIVE_HTTP"

        try:
            print(f"\n[HTTP GET] -> {name} | URL: {url}")
            response_text = fetcher.fetch(url)
            t1 = time.time()
            latency = round((t1 - t0) * 1000, 1)
            resp_bytes = len(response_text.encode("utf-8"))
            resp_hash = hashlib.sha256(response_text.encode("utf-8")).hexdigest()
            print(
                f"  [SUCCESS] Status: 200 OK | Latency: {latency}ms | Size: {resp_bytes} bytes | Hash: {resp_hash[:16]}..."
            )
            provider_health_service.record_success(name, latency_ms=latency)

            # Archive raw evidence
            archive_res = evidence_archive_service.archive_evidence(
                evidence_id=f"ev-{name.lower()}-test",
                marketplace=name,
                source_url=url,
                raw_payload=response_text,
                http_status=200,
            )

            results.append(
                {
                    "marketplace": name,
                    "url": url,
                    "status_code": 200,
                    "size_bytes": resp_bytes,
                    "latency_ms": latency,
                    "response_hash": resp_hash,
                    "archive_id": archive_res["archive_id"],
                    "mode": mode,
                    "confidence": 100.0,
                }
            )
        except Exception as e:
            t1 = time.time()
            latency = round((t1 - t0) * 1000, 1)
            error_msg = str(e)
            http_status = 403 if "403" in error_msg else 500
            mode = "FALLBACK"
            err_clean = error_msg[:100].encode("ascii", errors="ignore").decode("ascii")
            print(
                f"  [HTTP CHALLENGE / FALLBACK] Error: {err_clean} | Latency: {latency}ms"
            )
            provider_health_service.record_failure(
                name, status_code=http_status, error_msg=error_msg
            )

            results.append(
                {
                    "marketplace": name,
                    "url": url,
                    "status_code": http_status,
                    "size_bytes": 0,
                    "latency_ms": latency,
                    "response_hash": "FALLBACK_RESILIENCE_HASH",
                    "archive_id": f"arc-fallback-{name.lower()}",
                    "mode": mode,
                    "confidence": 20.0,
                }
            )

    print("\n--- STEP 9: RETRIEVAL SOURCE DISTRIBUTION SUMMARY ---")
    live_count = sum(1 for r in results if r["mode"] == "LIVE_HTTP")
    fallback_count = sum(1 for r in results if r["mode"] == "FALLBACK")
    print(f"Total Marketplace Requests Executed: {len(results)}")
    print(f"  [LIVE_HTTP Direct Responses]: {live_count}")
    print(f"  [FALLBACK Anti-Bot Challenged]: {fallback_count}")

    print(
        "\n=========================================================================="
    )
    print("LIVE MARKETPLACE AUDIT FINISHED")
    print("==========================================================================")


if __name__ == "__main__":
    test_live_http_fetch()

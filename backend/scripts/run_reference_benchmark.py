# ruff: noqa: E402
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.services.reference_discovery_service import (
    ReferenceDiscoveryService,  # noqa: E402
)
from backend.services.reference_extraction_service import (
    ReferenceExtractionService,  # noqa: E402
)

# Suppress verbose debug logs during benchmark execution
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ReferenceBenchmark")

BENCHMARK_DATASET: List[Dict[str, str]] = [
    # --- NOTHING / CMF (20 PRODUCTS) ---
    {"brand": "Nothing", "product": "Phone (1)", "expected_domain": "nothing.tech"},
    {"brand": "Nothing", "product": "Phone (2)", "expected_domain": "nothing.tech"},
    {"brand": "Nothing", "product": "Phone (2a)", "expected_domain": "nothing.tech"},
    {
        "brand": "Nothing",
        "product": "Phone (2a) Plus",
        "expected_domain": "nothing.tech",
    },
    {"brand": "Nothing", "product": "CMF Phone 1", "expected_domain": "nothing.tech"},
    {"brand": "Nothing", "product": "Ear (1)", "expected_domain": "nothing.tech"},
    {"brand": "Nothing", "product": "Ear (2)", "expected_domain": "nothing.tech"},
    {"brand": "Nothing", "product": "Ear (a)", "expected_domain": "nothing.tech"},
    {"brand": "Nothing", "product": "Ear", "expected_domain": "nothing.tech"},
    {"brand": "Nothing", "product": "CMF Buds", "expected_domain": "nothing.tech"},
    {"brand": "Nothing", "product": "CMF Buds Pro", "expected_domain": "nothing.tech"},
    {
        "brand": "Nothing",
        "product": "CMF Buds Pro 2",
        "expected_domain": "nothing.tech",
    },
    {"brand": "Nothing", "product": "CMF Watch Pro", "expected_domain": "nothing.tech"},
    {
        "brand": "Nothing",
        "product": "CMF Watch Pro 2",
        "expected_domain": "nothing.tech",
    },
    {
        "brand": "Nothing",
        "product": "Power 65W GaN Charger",
        "expected_domain": "nothing.tech",
    },
    {"brand": "Nothing", "product": "Headphone (1)", "expected_domain": "nothing.tech"},
    {
        "brand": "Nothing",
        "product": "CMF Neckband Pro",
        "expected_domain": "nothing.tech",
    },
    {"brand": "Nothing", "product": "Ear (open)", "expected_domain": "nothing.tech"},
    {
        "brand": "Nothing",
        "product": "Nothing Type-C Cable",
        "expected_domain": "nothing.tech",
    },
    {
        "brand": "Nothing",
        "product": "Nothing Power 45W",
        "expected_domain": "nothing.tech",
    },
    # --- APPLE (20 PRODUCTS) ---
    {"brand": "Apple", "product": "iPhone 15 Pro", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "iPhone 15", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "iPhone 14", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "iPhone 13", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "iPad Pro 12.9", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "iPad Air", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "iPad mini", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "MacBook Pro 16", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "MacBook Air 15", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "Mac Studio", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "iMac 24", "expected_domain": "apple.com"},
    {
        "brand": "Apple",
        "product": "Apple Watch Ultra 2",
        "expected_domain": "apple.com",
    },
    {
        "brand": "Apple",
        "product": "Apple Watch Series 9",
        "expected_domain": "apple.com",
    },
    {"brand": "Apple", "product": "Apple Watch SE", "expected_domain": "apple.com"},
    {
        "brand": "Apple",
        "product": "AirPods Pro (2nd gen)",
        "expected_domain": "apple.com",
    },
    {"brand": "Apple", "product": "AirPods Max", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "AirPods (3rd gen)", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "HomePod", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "Apple TV 4K", "expected_domain": "apple.com"},
    {"brand": "Apple", "product": "AirTag", "expected_domain": "apple.com"},
    # --- SAMSUNG (20 PRODUCTS) ---
    {
        "brand": "Samsung",
        "product": "Galaxy S24 Ultra",
        "expected_domain": "samsung.com",
    },
    {"brand": "Samsung", "product": "Galaxy S24+", "expected_domain": "samsung.com"},
    {"brand": "Samsung", "product": "Galaxy S24", "expected_domain": "samsung.com"},
    {"brand": "Samsung", "product": "Galaxy Z Fold5", "expected_domain": "samsung.com"},
    {"brand": "Samsung", "product": "Galaxy Z Flip5", "expected_domain": "samsung.com"},
    {"brand": "Samsung", "product": "Galaxy S23 FE", "expected_domain": "samsung.com"},
    {
        "brand": "Samsung",
        "product": "Galaxy Tab S9 Ultra",
        "expected_domain": "samsung.com",
    },
    {"brand": "Samsung", "product": "Galaxy Tab S9", "expected_domain": "samsung.com"},
    {
        "brand": "Samsung",
        "product": "Galaxy Watch6 Classic",
        "expected_domain": "samsung.com",
    },
    {"brand": "Samsung", "product": "Galaxy Watch6", "expected_domain": "samsung.com"},
    {
        "brand": "Samsung",
        "product": "Galaxy Buds2 Pro",
        "expected_domain": "samsung.com",
    },
    {"brand": "Samsung", "product": "Galaxy Buds FE", "expected_domain": "samsung.com"},
    {
        "brand": "Samsung",
        "product": "Galaxy Book4 Pro",
        "expected_domain": "samsung.com",
    },
    {"brand": "Samsung", "product": "Galaxy A55 5G", "expected_domain": "samsung.com"},
    {"brand": "Samsung", "product": "Galaxy A35 5G", "expected_domain": "samsung.com"},
    {
        "brand": "Samsung",
        "product": "Odyssey OLED G9",
        "expected_domain": "samsung.com",
    },
    {
        "brand": "Samsung",
        "product": "Smart Monitor M8",
        "expected_domain": "samsung.com",
    },
    {
        "brand": "Samsung",
        "product": "Portable SSD T7",
        "expected_domain": "samsung.com",
    },
    {"brand": "Samsung", "product": "Galaxy Ring", "expected_domain": "samsung.com"},
    {"brand": "Samsung", "product": "ViewFinity S9", "expected_domain": "samsung.com"},
    # --- SONY (20 PRODUCTS) ---
    {"brand": "Sony", "product": "WH-1000XM5", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "WH-1000XM4", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "WF-1000XM5", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "LinkBuds S", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "PlayStation 5", "expected_domain": "sony.com"},
    {
        "brand": "Sony",
        "product": "DualSense Edge Controller",
        "expected_domain": "sony.com",
    },
    {"brand": "Sony", "product": "Alpha 7 IV", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "Alpha 7R V", "expected_domain": "sony.com"},
    {
        "brand": "Sony",
        "product": "FE 24-70mm F2.8 GM II",
        "expected_domain": "sony.com",
    },
    {"brand": "Sony", "product": "BRAVIA XR A80L", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "HT-A7000 Soundbar", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "SRS-XG300 Speaker", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "Xperia 1 V", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "Xperia 5 V", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "INZONE H9 Headset", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "Walkman NW-ZX707", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "Vlog Camera ZV-E10", "expected_domain": "sony.com"},
    {"brand": "Sony", "product": "Cyber-shot RX100 VII", "expected_domain": "sony.com"},
    {
        "brand": "Sony",
        "product": "FX3 Cinema Line Camera",
        "expected_domain": "sony.com",
    },
    {"brand": "Sony", "product": "ECM-M1 Shotgun Mic", "expected_domain": "sony.com"},
    # --- NIKE / ADIDAS (20 PRODUCTS) ---
    {"brand": "Nike", "product": "Air Force 1 '07", "expected_domain": "nike.com"},
    {
        "brand": "Nike",
        "product": "Air Jordan 1 Retro High OG",
        "expected_domain": "nike.com",
    },
    {"brand": "Nike", "product": "Nike Dunk Low", "expected_domain": "nike.com"},
    {"brand": "Nike", "product": "Air Max 90", "expected_domain": "nike.com"},
    {"brand": "Nike", "product": "Pegasus 40", "expected_domain": "nike.com"},
    {"brand": "Nike", "product": "Metcon 9", "expected_domain": "nike.com"},
    {"brand": "Nike", "product": "Vaporfly 3", "expected_domain": "nike.com"},
    {"brand": "Nike", "product": "Invincible 3", "expected_domain": "nike.com"},
    {"brand": "Nike", "product": "Blazer Mid '77", "expected_domain": "nike.com"},
    {"brand": "Nike", "product": "Tech Fleece Joggers", "expected_domain": "nike.com"},
    {"brand": "Adidas", "product": "Ultraboost Light", "expected_domain": "adidas.com"},
    {"brand": "Adidas", "product": "Samba OG", "expected_domain": "adidas.com"},
    {"brand": "Adidas", "product": "Gazelle", "expected_domain": "adidas.com"},
    {"brand": "Adidas", "product": "Stan Smith", "expected_domain": "adidas.com"},
    {"brand": "Adidas", "product": "Forum Low", "expected_domain": "adidas.com"},
    {"brand": "Adidas", "product": "Superstar", "expected_domain": "adidas.com"},
    {
        "brand": "Adidas",
        "product": "Adizero Adios Pro 3",
        "expected_domain": "adidas.com",
    },
    {"brand": "Adidas", "product": "NMD_R1", "expected_domain": "adidas.com"},
    {
        "brand": "Adidas",
        "product": "Tiro 23 League Pants",
        "expected_domain": "adidas.com",
    },
    {
        "brand": "Adidas",
        "product": "Terrex Free Hiker 2",
        "expected_domain": "adidas.com",
    },
]


@dataclass
class ProductMetricResult:
    brand: str
    product: str
    expected_domain: str
    discovery_success: bool
    correct_domain: bool
    discovered_url: Optional[str]
    extraction_completeness_pct: float
    normalization_accuracy_pct: float
    quality_score: float
    confidence: float
    execution_time_ms: float
    evidence_count: int
    validation_status: str
    missing_fields: List[str] = field(default_factory=list)
    failure_reason: Optional[str] = None


@dataclass
class BrandBenchmarkSummary:
    brand_category: str
    total_products: int
    discovery_success_count: int
    discovery_success_rate_pct: float
    domain_accuracy_pct: float
    avg_quality_score: float
    avg_confidence: float
    avg_extraction_completeness_pct: float
    avg_execution_time_ms: float
    avg_evidence_count: float
    valid_status_pct: float


def run_benchmark() -> (  # noqa: C901
    Tuple[List[ProductMetricResult], List[BrandBenchmarkSummary], Dict[str, Any]]
):
    discovery_service = ReferenceDiscoveryService()
    extraction_service = ReferenceExtractionService()

    product_results: List[ProductMetricResult] = []
    category_buckets: Dict[str, List[ProductMetricResult]] = {}

    start_total_time = time.time()
    logger.info(
        f"Starting Reference Benchmark Sprint on {len(BENCHMARK_DATASET)} products..."
    )

    for idx, item in enumerate(BENCHMARK_DATASET, 1):
        brand = item["brand"]
        product_name = item["product"]
        expected_dom = item["expected_domain"]

        item_start = time.time()
        discovery_res, _ = discovery_service.discover(
            product_name=product_name, brand=brand
        )

        discovery_success = (
            discovery_res.status == "success"
            and discovery_res.verified_source is not None
        )
        discovered_url = (
            discovery_res.verified_source.url if discovery_res.verified_source else None
        )
        correct_domain = bool(discovered_url and expected_dom in discovered_url.lower())

        quality_score = 0.0
        confidence = 0.0
        completeness_pct = 0.0
        norm_accuracy_pct = 0.0
        evidence_count = 0
        val_status = "failed"
        missing_fields = []
        failure_reason = None

        if discovery_success and discovery_res.verified_source:
            # Execute extraction
            dummy_candidate = discovery_res.verified_source
            knowledge, is_valid = extraction_service.extract_canonical_knowledge(
                dummy_candidate
            )

            quality_score = knowledge.metadata.get(
                "quality_score", knowledge.overall_confidence
            )
            confidence = knowledge.overall_confidence
            val_status = knowledge.metadata.get(
                "validation_status", "valid" if is_valid else "invalid"
            )
            missing_fields = knowledge.metadata.get("missing_fields", [])
            evidence_count = len(knowledge.evidence_trail)

            # Completeness: Ratio of present core attributes (title, brand, url, msrp, specs, images)
            present_count = 0
            if knowledge.product_name and knowledge.product_name != "Unknown Product":
                present_count += 1
            if knowledge.brand and knowledge.brand != "Generic Brand":
                present_count += 1
            if knowledge.official_url:
                present_count += 1
            if knowledge.msrp:
                present_count += 1
            if knowledge.canonical_specs:
                present_count += 1
            if knowledge.verified_images:
                present_count += 1
            completeness_pct = round((present_count / 6.0) * 100.0, 1)

            # Normalization accuracy: All specs keys snake_case, numeric MSRP valid
            snake_keys = [
                k for k in knowledge.canonical_specs.keys() if k.islower() or "_" in k
            ]
            norm_accuracy_pct = (
                round(
                    (len(snake_keys) / max(len(knowledge.canonical_specs), 1)) * 100.0,
                    1,
                )
                if knowledge.canonical_specs
                else 100.0
            )
        else:
            failure_reason = (
                discovery_res.reasoning
                or "Discovery failed to locate verified official candidate"
            )

        item_latency_ms = round((time.time() - item_start) * 1000.0, 2)

        res = ProductMetricResult(
            brand=brand,
            product=product_name,
            expected_domain=expected_dom,
            discovery_success=discovery_success,
            correct_domain=correct_domain,
            discovered_url=discovered_url,
            extraction_completeness_pct=completeness_pct,
            normalization_accuracy_pct=norm_accuracy_pct,
            quality_score=quality_score,
            confidence=confidence,
            execution_time_ms=item_latency_ms,
            evidence_count=evidence_count,
            validation_status=val_status,
            missing_fields=missing_fields,
            failure_reason=failure_reason,
        )
        product_results.append(res)

        cat_key = "Nike / Adidas" if brand in ("Nike", "Adidas") else brand
        if cat_key not in category_buckets:
            category_buckets[cat_key] = []
        category_buckets[cat_key].append(res)

        if idx % 10 == 0:
            logger.info(
                f"Processed {idx}/{len(BENCHMARK_DATASET)} benchmark products..."
            )

    total_duration_s = round(time.time() - start_total_time, 2)

    # Compute category summaries
    summaries: List[BrandBenchmarkSummary] = []
    for cat_name, results in category_buckets.items():
        total = len(results)
        disc_success = sum(1 for r in results if r.discovery_success)
        correct_dom = sum(1 for r in results if r.correct_domain)
        avg_qs = round(sum(r.quality_score for r in results) / total, 2)
        avg_conf = round(sum(r.confidence for r in results) / total, 2)
        avg_comp = round(sum(r.extraction_completeness_pct for r in results) / total, 1)
        avg_lat = round(sum(r.execution_time_ms for r in results) / total, 2)
        avg_ev = round(sum(r.evidence_count for r in results) / total, 1)
        valid_cnt = sum(1 for r in results if r.validation_status == "valid")

        summaries.append(
            BrandBenchmarkSummary(
                brand_category=cat_name,
                total_products=total,
                discovery_success_count=disc_success,
                discovery_success_rate_pct=round((disc_success / total) * 100.0, 1),
                domain_accuracy_pct=round((correct_dom / total) * 100.0, 1),
                avg_quality_score=avg_qs,
                avg_confidence=avg_conf,
                avg_extraction_completeness_pct=avg_comp,
                avg_execution_time_ms=avg_lat,
                avg_evidence_count=avg_ev,
                valid_status_pct=round((valid_cnt / total) * 100.0, 1),
            )
        )

    # Compute global aggregate
    total_prods = len(product_results)
    global_disc_success = sum(1 for r in product_results if r.discovery_success)
    global_correct_dom = sum(1 for r in product_results if r.correct_domain)
    global_qs = round(sum(r.quality_score for r in product_results) / total_prods, 2)
    global_conf = round(sum(r.confidence for r in product_results) / total_prods, 2)
    global_comp = round(
        sum(r.extraction_completeness_pct for r in product_results) / total_prods, 1
    )
    global_norm_acc = round(
        sum(r.normalization_accuracy_pct for r in product_results) / total_prods, 1
    )
    global_lat = round(
        sum(r.execution_time_ms for r in product_results) / total_prods, 2
    )
    global_ev = round(sum(r.evidence_count for r in product_results) / total_prods, 1)

    global_metrics = {
        "total_benchmark_products": total_prods,
        "global_discovery_success_rate_pct": round(
            (global_disc_success / total_prods) * 100.0, 1
        ),
        "global_domain_accuracy_pct": round(
            (global_correct_dom / total_prods) * 100.0, 1
        ),
        "global_avg_quality_score": global_qs,
        "global_avg_confidence": global_conf,
        "global_avg_extraction_completeness_pct": global_comp,
        "global_avg_normalization_accuracy_pct": global_norm_acc,
        "global_avg_execution_time_ms": global_lat,
        "global_avg_evidence_count": global_ev,
        "total_duration_seconds": total_duration_s,
    }

    return product_results, summaries, global_metrics


if __name__ == "__main__":
    results, summaries, global_metrics = run_benchmark()

    print("\n" + "=" * 80)
    print(" REFERENCE DISCOVERY & EXTRACTION BENCHMARK RESULTS")
    print("=" * 80 + "\n")

    for summary in summaries:
        print(
            f"--- Category: {summary.brand_category} ({summary.total_products} products) ---"
        )
        print(
            f"  * Discovery Success Rate:   {summary.discovery_success_rate_pct}% ({summary.discovery_success_count}/{summary.total_products})"
        )
        print(f"  * Official Domain Accuracy: {summary.domain_accuracy_pct}%")
        print(f"  * Avg Validation Score:     {summary.avg_quality_score} / 1.00")
        print(f"  * Avg Confidence:           {summary.avg_confidence}")
        print(
            f"  * Avg Completeness:         {summary.avg_extraction_completeness_pct}%"
        )
        print(f"  * Avg Latency:              {summary.avg_execution_time_ms} ms")
        print(f"  * Avg Evidence Items:       {summary.avg_evidence_count}")
        print(f"  * Valid Status Rate:        {summary.valid_status_pct}%\n")

    print("=" * 80)
    print(" GLOBAL BENCHMARK METRICS SUMMARY")
    print("=" * 80)
    print(json.dumps(global_metrics, indent=2))

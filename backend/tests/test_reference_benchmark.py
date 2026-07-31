from backend.scripts.run_reference_benchmark import run_benchmark


def test_100_product_benchmark_suite():
    """
    Dedicated Pre-LangGraph Benchmark Validation Sprint Test.
    Evaluates 100 products (20 Nothing, 20 Apple, 20 Samsung, 20 Sony, 20 Nike/Adidas).
    Verifies discovery success rate, domain accuracy, normalization accuracy, and latency metrics.
    """
    product_results, summaries, global_metrics = run_benchmark()

    # 1. Total products count check
    assert global_metrics["total_benchmark_products"] == 100

    # 2. Discovery Success Rate >= 95%
    assert global_metrics["global_discovery_success_rate_pct"] >= 95.0

    # 3. Domain Accuracy Rate == 100%
    assert global_metrics["global_domain_accuracy_pct"] == 100.0

    # 4. Normalization Accuracy == 100%
    assert global_metrics["global_avg_normalization_accuracy_pct"] == 100.0

    # 5. Average Latency < 50ms
    assert global_metrics["global_avg_execution_time_ms"] < 50.0

    # 6. Verify each category bucket contains 20 products
    for summary in summaries:
        assert summary.total_products == 20
        assert summary.discovery_success_rate_pct >= 95.0
        assert summary.domain_accuracy_pct == 100.0

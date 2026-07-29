import unittest

from backend.services.verdict_engine import VerdictEngine


class TestVerdictEngineInvariants(unittest.TestCase):
    def test_failed_investigation_returns_insufficient_data(self):
        verdict = VerdictEngine.evaluate_risk(
            raw_risk_score=50,
            product_name="Test Product",
            marketplace="Amazon",
            seller_name="Unknown Seller",
            price=19.99,
            findings_list=["Price Anomaly: Low price"],
            investigation_status="failed",
        )
        self.assertEqual(verdict.final_verdict, "INSUFFICIENT_DATA")
        self.assertEqual(verdict.risk_level, "INSUFFICIENT_DATA")
        self.assertIn("Synthesis unavailable", verdict.summary)
        self.assertIn("Synthesis unavailable", verdict.reasoning)

    def test_degraded_live_run_usable_specialists_below_threshold_triggers_insufficient_data(
        self
    ):
        """
        Simulates a COMPLETED run where status='completed', but usable_specialist_count < 2 or evidence_signals == 0.
        Must trigger INSUFFICIENT_DATA guard instead of fabricating an AUTHENTIC verdict.
        """
        verdict = VerdictEngine.evaluate_risk(
            raw_risk_score=0,
            product_name="Amazon Listing",
            marketplace="Amazon",
            seller_name="Degraded Merchant",
            price=150.00,
            findings_list=[],
            data_source="live_retrieval",
            investigation_status="completed",
            usable_specialist_count=1,
            evidence_signals_count=0,
        )
        self.assertEqual(verdict.final_verdict, "INSUFFICIENT_DATA")
        self.assertEqual(verdict.risk_level, "INSUFFICIENT_DATA")
        self.assertIn("INSUFFICIENT DATA", verdict.summary)

    def test_hard_consensus_invariant_overrides_authentic_verdict_on_negative_consensus(
        self
    ):
        """
        Simulates a COMPLETED run where raw computed findings weight is 0 (raw verdict AUTHENTIC),
        but specialist consensus / raw_risk_score = 50 (SUSPICIOUS).
        The hard invariant MUST override final_verdict to SUSPICIOUS / MEDIUM and CANNOT render AUTHENTIC.
        """
        verdict = VerdictEngine.evaluate_risk(
            raw_risk_score=50,
            product_name="Sony WH-1000XM5",
            marketplace="Amazon",
            seller_name="ElectroDeals Direct",
            price=189.99,
            findings_list=[],
            data_source="live_retrieval",
            investigation_status="completed",
            usable_specialist_count=4,
            evidence_signals_count=2,
        )
        self.assertNotEqual(verdict.final_verdict, "AUTHENTIC")
        self.assertEqual(verdict.final_verdict, "SUSPICIOUS")
        self.assertEqual(verdict.risk_level, "MEDIUM")
        self.assertGreaterEqual(verdict.risk_score, 45)

    def test_authentic_verdict_only_with_clean_signals(self):
        verdict = VerdictEngine.evaluate_risk(
            raw_risk_score=0,
            product_name="Sony WH-1000XM5",
            marketplace="Sony Direct Store",
            seller_name="Sony Direct Store",
            price=399.99,
            findings_list=["No significant risk indicators found."],
            data_source="live_retrieval",
            investigation_status="completed",
            usable_specialist_count=5,
            evidence_signals_count=5,
        )
        self.assertEqual(verdict.final_verdict, "AUTHENTIC")
        self.assertEqual(verdict.risk_level, "LOW")


if __name__ == "__main__":
    unittest.main()

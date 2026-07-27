import logging
from typing import Optional

from backend.automation.models.domain import Alert, AlertSeverity
from backend.collaboration.models.context import InvestigationContext
from backend.schemas.llm_models import AIInvestigationResult

logger = logging.getLogger(__name__)


class AlertService:
    """
    Evaluates completed investigations and generates system alerts for critical findings.
    """

    def evaluate_investigation(
        self, context: InvestigationContext, result: AIInvestigationResult
    ) -> Optional[Alert]:
        """
        Determines if an investigation warrants a proactive alert based on risk score,
        network indicators, or watchlist matches.
        """
        if not result:
            return None

        # Check for Critical/High Risk
        if result.confidence_score >= 0.85:
            severity = AlertSeverity.CRITICAL
            alert_type = "suspicious_listing"

            # Check if Graph Intelligence shows network risk
            if context.graphrag_intelligence and hasattr(
                context.graphrag_intelligence, "network_risk"
            ):
                if context.graphrag_intelligence.network_risk > 0.7:
                    alert_type = "fraud_ring_expansion"

            alert = Alert(
                severity=severity,
                alert_type=alert_type,
                reason=result.summary,
                supporting_evidence=[
                    {"indicator": ind} for ind in result.suspicious_indicators
                ],
                recommended_action="Immediately review listing and flag seller account.",
            )
            self._dispatch_alert(alert)
            return alert

        elif result.confidence_score >= 0.65:
            alert = Alert(
                severity=AlertSeverity.HIGH,
                alert_type="potential_counterfeit",
                reason=result.summary,
                recommended_action="Schedule for manual review.",
            )
            self._dispatch_alert(alert)
            return alert

        return None

    def _dispatch_alert(self, alert: Alert) -> None:
        """
        Sends the alert to the appropriate channel (e.g. Email, Slack, DB).
        """
        logger.warning(
            f"DISPATCHING ALERT: [{alert.severity.value.upper()}] {alert.alert_type} - {alert.reason}"
        )

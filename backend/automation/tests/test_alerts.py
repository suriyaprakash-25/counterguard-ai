import uuid

from backend.automation.alerts.alert_service import AlertService
from backend.automation.models.domain import AlertSeverity
from backend.collaboration.models.context import InvestigationContext
from backend.schemas.llm_models import AIInvestigationResult


def test_alert_service_critical():
    service = AlertService()
    context = InvestigationContext(investigation_id=str(uuid.uuid4()))

    result = AIInvestigationResult(
        summary="Clear counterfeit",
        detailed_reasoning="Failed multiple checks",
        suspicious_indicators=["price", "image"],
        confidence_score=0.9,
    )

    alert = service.evaluate_investigation(context, result)
    assert alert is not None
    assert alert.severity == AlertSeverity.CRITICAL


def test_alert_service_high():
    service = AlertService()
    context = InvestigationContext(investigation_id=str(uuid.uuid4()))

    result = AIInvestigationResult(
        summary="Possible counterfeit",
        detailed_reasoning="Some flags",
        suspicious_indicators=["price"],
        confidence_score=0.75,
    )

    alert = service.evaluate_investigation(context, result)
    assert alert is not None
    assert alert.severity == AlertSeverity.HIGH


def test_alert_service_no_alert():
    service = AlertService()
    context = InvestigationContext(investigation_id=str(uuid.uuid4()))

    result = AIInvestigationResult(
        summary="Authentic",
        detailed_reasoning="Looks good",
        suspicious_indicators=[],
        confidence_score=0.2,
    )

    alert = service.evaluate_investigation(context, result)
    assert alert is None

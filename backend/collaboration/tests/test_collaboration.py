from backend.collaboration.models.context import InvestigationContext
from backend.collaboration.models.protocol import AgentObservation
from backend.collaboration.services.consensus import ConsensusService
from backend.collaboration.services.delegation import DelegationService
from backend.collaboration.services.explainability import ExplainabilityService
from backend.collaboration.services.timeline import TimelineService
from backend.collaboration.services.validation import ValidationService
from backend.memory.models.domain import Evidence, EvidenceType, ValidationStatus


def test_validation_service_conflicting_invoices():
    context = InvestigationContext(investigation_id="test-1")

    # Add two conflicting invoices
    context.shared_evidence.append(
        Evidence(
            evidence_type=EvidenceType.INVOICE,
            content="Total: $100",
            source_agent="AgentA",
        )
    )
    context.shared_evidence.append(
        Evidence(
            evidence_type=EvidenceType.INVOICE,
            content="Total: $200",
            source_agent="AgentB",
        )
    )

    service = ValidationService()
    service.validate_evidence(context)

    # Both should be marked as conflicting
    assert context.shared_evidence[0].validation_status == ValidationStatus.CONFLICTING
    assert context.shared_evidence[1].validation_status == ValidationStatus.CONFLICTING


def test_consensus_service_conflict_detection():
    context = InvestigationContext(investigation_id="test-2")
    context.shared_observations = [
        AgentObservation(
            source_agent="A", content="Product is highly likely Authentic"
        ),
        AgentObservation(
            source_agent="B", content="Found counterfeit materials, very suspicious"
        ),
    ]

    service = ConsensusService()
    conflicts = service.resolve_conflicts(context)

    assert len(conflicts) == 1
    assert "Conflict Detected" in conflicts[0]


def test_delegation_service_routing():
    context = InvestigationContext(investigation_id="test-3")
    from backend.collaboration.models.protocol import AgentQuestion

    context.unresolved_questions.append(
        AgentQuestion(source_agent="Vision", content="What is the historical price?")
    )

    service = DelegationService()
    service.evaluate_and_delegate(context)

    assert len(context.tasks) == 1
    assert context.tasks[0].assigned_agent == "PriceAgent"


def test_explainability_service():
    context = InvestigationContext(investigation_id="test-4")
    context.shared_evidence.append(
        Evidence(
            evidence_type=EvidenceType.METADATA,
            content="Missing GST Number",
            source_agent="OCR Agent",
            validation_status=ValidationStatus.VERIFIED,
        )
    )

    service = ExplainabilityService()
    explanation = service.generate_explanation(context, 0.95)

    assert "Final Risk Confidence: 95.0%" in explanation
    assert "OCR Agent:" in explanation
    assert "Missing GST Number" in explanation


def test_timeline_service():
    service = TimelineService()
    service.record_event("AgentStarted", "PriceAgent", "Started analyzing prices")

    timeline = service.get_timeline()
    assert len(timeline) == 1
    assert timeline[0]["type"] == "AgentStarted"
    assert timeline[0]["actor"] == "PriceAgent"

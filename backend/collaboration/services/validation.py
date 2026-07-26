from backend.collaboration.models.context import InvestigationContext
from backend.memory.models.domain import Evidence, ValidationStatus


class ValidationService:
    """
    Cross-checks evidence on the Blackboard to determine its validity.
    Updates the validation_status of Evidence objects.
    """

    def validate_evidence(self, context: InvestigationContext) -> None:
        """
        Reviews all shared evidence and updates their validation status
        based on corroborating or conflicting evidence.
        """
        for evidence in context.shared_evidence:
            if evidence.validation_status != ValidationStatus.PENDING:
                continue

            # Basic validation logic based on type and context
            if evidence.evidence_type.value == "Invoice":
                self._validate_invoice(evidence, context)
            elif evidence.evidence_type.value == "SellerInfo":
                self._validate_seller_info(evidence, context)
            else:
                # Default to VERIFIED if confidence is high, else WEAK
                if evidence.confidence > 0.8:
                    evidence.validation_status = ValidationStatus.VERIFIED
                else:
                    evidence.validation_status = ValidationStatus.WEAK

    def _validate_invoice(
        self, evidence: Evidence, context: InvestigationContext
    ) -> None:
        """Example: Cross-check invoice OCR with other evidence."""
        # Check if another agent reported conflicting invoice data
        conflicts = [
            e
            for e in context.shared_evidence
            if e.evidence_type.value == "Invoice"
            and e.evidence_id != evidence.evidence_id
            and e.content != evidence.content
        ]

        if conflicts:
            evidence.validation_status = ValidationStatus.CONFLICTING
        else:
            evidence.validation_status = ValidationStatus.VERIFIED

    def _validate_seller_info(
        self, evidence: Evidence, context: InvestigationContext
    ) -> None:
        """Example: Cross-check seller info with graph intelligence."""
        phone = evidence.metadata.get("phone")

        # If Graph Intelligence flags this phone as suspicious
        if (
            phone
            and context.graphrag_intelligence
            and hasattr(context.graphrag_intelligence, "shared_entities")
        ):
            if phone in context.graphrag_intelligence.shared_entities:
                # Validated but highly suspicious
                evidence.validation_status = ValidationStatus.VERIFIED
                evidence.reasoning = "Phone verified as shared with known fraud ring via Graph Intelligence."
                return

        evidence.validation_status = ValidationStatus.VERIFIED

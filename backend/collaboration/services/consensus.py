from typing import List

from backend.collaboration.models.context import InvestigationContext


class ConsensusService:
    """
    Detects conflicts between agent findings and calculates consensus confidence.
    """

    def resolve_conflicts(self, context: InvestigationContext) -> List[str]:
        """
        Analyzes the Blackboard for conflicting agent observations and evidence.
        Returns a list of identified conflicts.
        """
        conflicts = []

        # Simple conflict detection: e.g., one agent says 'Authentic', another says 'Counterfeit'
        authentic_votes = 0
        counterfeit_votes = 0

        for obs in context.shared_observations:
            if (
                "authentic" in obs.content.lower()
                and "not authentic" not in obs.content.lower()
            ):
                authentic_votes += 1
            elif (
                "counterfeit" in obs.content.lower()
                or "suspicious" in obs.content.lower()
            ):
                counterfeit_votes += 1

        if authentic_votes > 0 and counterfeit_votes > 0:
            conflicts.append(
                f"Conflict Detected: {authentic_votes} agents lean Authentic, "
                f"while {counterfeit_votes} agents lean Counterfeit/Suspicious."
            )

        return conflicts

    def calculate_consensus_confidence(self, context: InvestigationContext) -> float:
        """
        Calculates an aggregate confidence score based on Blackboard evidence.
        """
        if not context.shared_evidence and not context.shared_observations:
            return 0.5

        total_confidence = 0.0
        count = 0

        for evidence in context.shared_evidence:
            if evidence.validation_status == "Verified":
                total_confidence += evidence.confidence * 1.2
            elif evidence.validation_status == "Conflicting":
                total_confidence += evidence.confidence * 0.5
            else:
                total_confidence += evidence.confidence
            count += 1

        if count == 0:
            return 0.5

        base_confidence = total_confidence / count

        # Adjust based on Graph Intelligence Risk
        risk_multiplier = 1.0
        if context.graphrag_intelligence and hasattr(
            context.graphrag_intelligence, "network_risk"
        ):
            risk_multiplier += context.graphrag_intelligence.network_risk * 0.2

        final_confidence = min(max(base_confidence * risk_multiplier, 0.0), 1.0)

        # Log to timeline
        context.confidence_timeline.append(
            {
                "timestamp": "now",  # In real usage, use actual time
                "confidence": final_confidence,
                "reason": "Consensus calculation",
            }
        )

        return final_confidence

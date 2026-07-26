from backend.collaboration.models.context import InvestigationContext


class ExplainabilityService:
    """
    Produces structured explanations detailing exactly which agents
    and evidence contributed to the final confidence score.
    """

    def generate_explanation(
        self, context: InvestigationContext, final_confidence: float
    ) -> str:
        """
        Synthesizes the Blackboard into a readable, attributable explanation.
        """
        explanation_lines = [
            f"Final Risk Confidence: {final_confidence * 100:.1f}%\n",
            "Supported By:\n",
        ]

        # Group evidence by source agent
        evidence_by_agent = {}
        for ev in context.shared_evidence:
            agent = ev.source_agent or "Unknown Agent"
            if agent not in evidence_by_agent:
                evidence_by_agent[agent] = []
            evidence_by_agent[agent].append(ev)

        for agent, evidence_list in evidence_by_agent.items():
            explanation_lines.append(f"{agent}:")
            for ev in evidence_list:
                status = (
                    f"[{ev.validation_status.value}]"
                    if ev.validation_status
                    else "[Unvalidated]"
                )
                explanation_lines.append(
                    f"  - {status} {ev.evidence_type.value}: {ev.content}"
                )

        # Add Graph Intelligence
        if context.graph_intelligence:
            explanation_lines.append("\nGraph Intelligence:")
            explanation_lines.append(
                f"  - Network Risk Multiplier: {context.graph_intelligence.get('network_risk_multiplier', 1.0)}"
            )
            shared = context.graph_intelligence.get("shared_identifiers", {})
            if shared:
                explanation_lines.append(f"  - Shared Identifiers Found: {len(shared)}")

        return "\n".join(explanation_lines)

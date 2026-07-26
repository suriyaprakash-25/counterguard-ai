from backend.graphrag.models.domain import InvestigationIntelligence


class ContextBuilder:
    """
    Converts InvestigationIntelligence into structured LLM-ready context strings.
    """

    def build_markdown_context(self, intelligence: InvestigationIntelligence) -> str:  # noqa: C901
        """
        Builds a comprehensive markdown report of the gathered intelligence.
        """
        sections = []

        # 1. Seller History
        sections.append("## Seller History")
        if intelligence.seller_history:
            sh = intelligence.seller_history
            name = sh.get("identity", {}).get("name", "Unknown")
            trust = sh.get("overall_trust_score", 50.0)
            sections.append(f"Seller Name: {name}")
            sections.append(f"Historical Trust Score: {trust}/100")
            sections.append(
                f"Previous Investigations: {len(sh.get('previous_episode_ids', []))}"
            )
        else:
            sections.append("No historical profile found for this seller.")

        # 2. Fraud Network
        sections.append("\n## Fraud Network (Graph Intelligence)")
        if intelligence.graph_summary:
            sections.append(intelligence.graph_summary)
        elif intelligence.graph_network:
            nodes = intelligence.graph_network
            sections.append(
                f"Detected {len(nodes)} direct connections in the knowledge graph."
            )
            for node in nodes:
                sections.append(
                    f"- Connected to [{node.get('label', 'Unknown')}] {node.get('target', 'Unknown')} via {node.get('rel_type', 'Unknown')}"
                )
        else:
            sections.append("No known fraudulent network connections.")

        # 3. Similar Investigations
        sections.append("\n## Similar Investigations")
        if intelligence.similar_cases:
            sections.append(
                f"Found {len(intelligence.similar_cases)} similar past cases."
            )
            for i, case in enumerate(intelligence.similar_cases[:3]):
                ep = case.get("episode")
                if hasattr(ep, "model_dump"):
                    ep = ep.model_dump()
                sections.append(f"**Case {i+1}:** {ep.get('summary', 'No summary')}")
                sections.append(
                    f"Verdict: {ep.get('verdict', 'Unknown')} (Risk Score: {ep.get('risk_score', 0)})"
                )
        else:
            sections.append("No semantically similar cases found.")

        # 4. Shared Evidence (Historical)
        sections.append("\n## Shared Evidence")
        if intelligence.historical_evidence:
            for ev in intelligence.historical_evidence[:5]:
                sections.append(
                    f"- [{ev.evidence_type}]: {ev.content} (Relevance: {ev.relevance_score:.2f})"
                )
        else:
            sections.append("No relevant historical evidence retrieved.")

        # 5. Historical Patterns
        sections.append("\n## Historical Patterns")
        if intelligence.repeated_patterns:
            for pat in intelligence.repeated_patterns:
                sections.append(
                    f"- **{pat.pattern_type.upper()}**: {pat.description} (Frequency: {pat.frequency})"
                )
        else:
            sections.append("No overlapping fraud patterns detected.")

        # 6. Recommended Investigation Focus
        sections.append("\n## Recommended Investigation Focus")
        if intelligence.recommended_focus:
            for focus in intelligence.recommended_focus:
                sections.append(f"- {focus}")
        else:
            sections.append("- Proceed with standard multi-agent investigation.")

        return "\n".join(sections)

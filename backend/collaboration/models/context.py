from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.collaboration.models.protocol import (
    AgentObservation,
    AgentQuestion,
    InvestigationTask,
)
from backend.memory.models.domain import (
    ConfidenceStep,
    Evidence,
    EvidenceCategory,
    ReasoningStep,
)


class AgentWorkspace(BaseModel):
    """
    Localized memory for an individual agent during a single run.
    This does NOT persist after the investigation.
    """

    agent_name: str
    temporary_reasoning: List[str] = Field(default_factory=list)
    intermediate_observations: List[str] = Field(default_factory=list)
    tool_outputs: Dict[str, Any] = Field(default_factory=dict)
    confidence: float = 0.5


class InvestigationContext(BaseModel):
    """
    The Investigation Blackboard.
    Single source of truth shared across all agents during an investigation.
    Agents read/write to this context as a Directed Evidence Graph.
    """

    investigation_id: str = Field(default_factory=lambda: "inv_default")

    # Sprint 1 Structured Context Fields
    product_info: Dict[str, Any] = Field(default_factory=dict)
    marketplace: str = "Global"
    seller_info: Dict[str, Any] = Field(default_factory=dict)
    extracted_metadata: Dict[str, Any] = Field(default_factory=dict)

    # Evidence & Observations
    shared_evidence: List[Evidence] = Field(default_factory=list)
    shared_observations: List[AgentObservation] = Field(default_factory=list)
    unresolved_questions: List[AgentQuestion] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    tasks: List[InvestigationTask] = Field(default_factory=list)

    # Risk & Confidence Analytics
    confidence_timeline: List[ConfidenceStep] = Field(default_factory=list)
    reasoning_timeline: List[ReasoningStep] = Field(default_factory=list)
    intermediate_risk: float = 0.0
    final_verdict: Dict[str, Any] = Field(default_factory=dict)

    # External Context Injected into Blackboard via GraphRAG
    graphrag_intelligence: Any = None
    graphrag_context: str = ""

    @property
    def evidence(self) -> List[Evidence]:
        return self.shared_evidence

    @property
    def observations(self) -> List[AgentObservation]:
        return self.shared_observations

    @property
    def confidence_history(self) -> List[ConfidenceStep]:
        return self.confidence_timeline

    def add_evidence(
        self, item: Evidence, derived_from_ids: Optional[List[str]] = None
    ) -> None:
        """
        Appends evidence to the blackboard as a node in the Directed Evidence Graph.
        Updates parent lineage (`consumed_by`, `supports`, `conflicts_with`).
        """
        if not item.timestamp:
            item.timestamp = datetime.utcnow().isoformat()

        # Set lineage
        if derived_from_ids:
            for parent_id in derived_from_ids:
                if parent_id not in item.derived_from:
                    item.derived_from.append(parent_id)

        existing_ids = {e.evidence_id: e for e in self.shared_evidence}
        if item.evidence_id not in existing_ids:
            # Wire parent consumed_by and supports/conflicts links
            for parent_id in item.derived_from:
                if parent_id in existing_ids:
                    parent_ev = existing_ids[parent_id]
                    if item.evidence_id not in parent_ev.consumed_by:
                        parent_ev.consumed_by.append(item.evidence_id)

                    if item.severity in ["critical", "high", "medium"]:
                        if item.evidence_id not in parent_ev.supports:
                            parent_ev.supports.append(item.evidence_id)
                    else:
                        if item.evidence_id not in parent_ev.conflicts_with:
                            parent_ev.conflicts_with.append(item.evidence_id)

            self.shared_evidence.append(item)

            # Record confidence evolution step
            prev_conf = (
                self.confidence_timeline[-1].current_confidence
                if self.confidence_timeline
                else 0.50
            )
            self.record_confidence_step(
                agent_name=item.agent_name,
                previous_confidence=prev_conf,
                current_confidence=item.confidence,
                reason=f"Emitted evidence [{item.category}]: {item.title}",
            )
            self.recalculate_intermediate_risk()

    def add_observation(self, obs: AgentObservation) -> None:
        if obs not in self.shared_observations:
            self.shared_observations.append(obs)

    def get_evidence_by_agent(self, agent_name: str) -> List[Evidence]:
        return [
            e
            for e in self.shared_evidence
            if e.agent_name.lower() == agent_name.lower()
            or e.source_agent.lower() == agent_name.lower()
        ]

    def get_evidence_by_category(self, category: str) -> List[Evidence]:
        return [
            e for e in self.shared_evidence if e.category.lower() == category.lower()
        ]

    def record_confidence_step(
        self,
        agent_name: str,
        current_confidence: float,
        previous_confidence: float = 0.50,
        reason: str = "",
    ) -> None:
        step = ConfidenceStep(
            previous_confidence=previous_confidence,
            current_confidence=current_confidence,
            reason=reason,
            agent=agent_name,
            timestamp=datetime.utcnow().isoformat(),
        )
        self.confidence_timeline.append(step)

    def recalculate_intermediate_risk(self) -> float:
        if not self.shared_evidence:
            self.intermediate_risk = 0.0
            return 0.0

        weights = {
            "critical": 35.0,
            "high": 25.0,
            "medium": 15.0,
            "low": 5.0,
            "info": 0.0,
        }
        total_risk = 0.0
        for e in self.shared_evidence:
            sev_weight = weights.get(e.severity.lower(), 10.0)
            total_risk += sev_weight * e.confidence

        self.intermediate_risk = round(min(100.0, total_risk), 1)
        return self.intermediate_risk

    def build_evidence_graph(self) -> Dict[str, Any]:
        """
        Serializes the Directed Evidence Graph into Cytoscape.js compatible JSON format.
        """
        nodes = []
        edges = []

        for ev in self.shared_evidence:
            nodes.append(
                {
                    "data": {
                        "id": ev.evidence_id,
                        "label": ev.title,
                        "category": ev.category,
                        "severity": ev.severity,
                        "confidence": ev.confidence,
                        "agent": ev.agent_name,
                        "description": ev.description,
                        "timestamp": ev.timestamp,
                    }
                }
            )

            # Edge 1: derived_from
            for parent_id in ev.derived_from:
                edges.append(
                    {
                        "data": {
                            "id": f"edge-{parent_id}-{ev.evidence_id}-derived",
                            "source": parent_id,
                            "target": ev.evidence_id,
                            "relationship": "derived_from",
                        }
                    }
                )

            # Edge 2: supports
            for sup_id in ev.supports:
                edges.append(
                    {
                        "data": {
                            "id": f"edge-{ev.evidence_id}-{sup_id}-supports",
                            "source": ev.evidence_id,
                            "target": sup_id,
                            "relationship": "supports",
                        }
                    }
                )

            # Edge 3: conflicts_with
            for conf_id in ev.conflicts_with:
                edges.append(
                    {
                        "data": {
                            "id": f"edge-{ev.evidence_id}-{conf_id}-conflicts",
                            "source": ev.evidence_id,
                            "target": conf_id,
                            "relationship": "conflicts_with",
                        }
                    }
                )

        return {"nodes": nodes, "edges": edges}

    def validate_context(self) -> List[str]:
        """
        Pre-Coordinator context validation rules:
        1. Prevent duplicate evidence IDs
        2. Prevent circular references (DAG cycle check)
        3. Enforce taxonomy category validation
        4. Enforce confidence bounds (0.0 <= c <= 1.0)
        5. Enforce agent attribution (no orphan evidence)
        """
        errors = []
        seen_ids = set()
        adj = {}

        for ev in self.shared_evidence:
            # 1. Duplicate check
            if ev.evidence_id in seen_ids:
                errors.append(f"Duplicate evidence ID detected: {ev.evidence_id}")
            seen_ids.add(ev.evidence_id)

            # 3. Category validation
            if ev.category not in EvidenceCategory.__members__:
                errors.append(
                    f"Invalid Evidence Category '{ev.category}' on {ev.evidence_id}"
                )

            # 4. Confidence bounds
            if not (0.0 <= ev.confidence <= 1.0):
                errors.append(
                    f"Invalid confidence score {ev.confidence} on {ev.evidence_id}"
                )

            # 5. Agent attribution
            if not ev.agent_name or ev.agent_name == "Unknown":
                errors.append(
                    f"Orphan evidence without agent attribution: {ev.evidence_id}"
                )

            adj[ev.evidence_id] = list(set(ev.derived_from))

        # 2. Circular reference prevention (DAG cycle detection via DFS)
        visited = {}  # 0=unvisited, 1=visiting, 2=visited

        def dfs(node_id: str) -> bool:
            visited[node_id] = 1
            for parent_id in adj.get(node_id, []):
                if parent_id in adj:
                    if visited.get(parent_id, 0) == 1:
                        return True
                    if visited.get(parent_id, 0) == 0:
                        if dfs(parent_id):
                            return True
            visited[node_id] = 2
            return False

        for node_id in adj:
            if visited.get(node_id, 0) == 0:
                if dfs(node_id):
                    errors.append(
                        f"Circular evidence reference cycle detected starting at {node_id}"
                    )
                    break

        return errors

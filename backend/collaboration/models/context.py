from typing import Any, Dict, List

from pydantic import BaseModel, Field

from backend.collaboration.models.protocol import (
    AgentObservation,
    AgentQuestion,
    InvestigationTask,
)
from backend.memory.models.domain import Evidence


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
    Agents only read/write to this context.
    """

    investigation_id: str

    # The Blackboard Data
    shared_evidence: List[Evidence] = Field(default_factory=list)
    shared_observations: List[AgentObservation] = Field(default_factory=list)
    unresolved_questions: List[AgentQuestion] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    tasks: List[InvestigationTask] = Field(default_factory=list)

    # External Context Injected into Blackboard
    memory_context: List[Dict[str, Any]] = Field(default_factory=list)
    graph_intelligence: Dict[str, Any] = Field(default_factory=dict)

    # Analytics
    confidence_timeline: List[Dict[str, Any]] = Field(default_factory=list)

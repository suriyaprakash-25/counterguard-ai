import uuid
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AgentMessageType(str, Enum):
    OBSERVATION = "Observation"
    DECISION = "Decision"
    QUESTION = "Question"
    RECOMMENDATION = "Recommendation"


class AgentMessage(BaseModel):
    """Base protocol for inter-agent communication."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_agent: str
    target_agent: Optional[str] = None
    message_type: AgentMessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentObservation(AgentMessage):
    message_type: AgentMessageType = AgentMessageType.OBSERVATION
    evidence_ref_ids: List[str] = Field(default_factory=list)


class AgentDecision(AgentMessage):
    message_type: AgentMessageType = AgentMessageType.DECISION
    confidence: float
    rationale: str


class AgentQuestion(AgentMessage):
    message_type: AgentMessageType = AgentMessageType.QUESTION
    is_resolved: bool = False
    resolution: Optional[str] = None


class AgentRecommendation(AgentMessage):
    message_type: AgentMessageType = AgentMessageType.RECOMMENDATION
    suggested_action: str


class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"


class TaskPriority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class InvestigationTask(BaseModel):
    """A unit of work delegated to an agent."""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    description: str
    assigned_agent: Optional[str] = None
    created_by: str
    status: TaskStatus = TaskStatus.PENDING
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = Field(default_factory=list)  # List of Task IDs
    created_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    result: Optional[str] = None
    artifacts: List[str] = Field(default_factory=list)

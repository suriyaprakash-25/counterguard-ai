import uuid
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, Field


class ValidationStatus(str, Enum):
    VERIFIED = "Verified"
    CONFLICTING = "Conflicting"
    WEAK = "Weak"
    UNSUPPORTED = "Unsupported"
    PENDING = "Pending"


class EvidenceType(str, Enum):
    OCR = "OCR"
    IMAGE = "Image"
    SCREENSHOT = "Screenshot"
    CHAT = "Chat"
    METADATA = "Metadata"
    INVOICE = "Invoice"
    PRODUCT = "Product"
    SELLER_INFO = "SellerInfo"


class EvidenceCategory(str, Enum):
    PRICE = "PRICE"
    SELLER = "SELLER"
    BRAND = "BRAND"
    SPECIFICATION = "SPECIFICATION"
    METADATA = "METADATA"
    REVIEWS = "REVIEWS"
    VISUAL = "VISUAL"
    MEMORY = "MEMORY"
    GRAPH = "GRAPH"
    NETWORK = "NETWORK"
    PROVENANCE = "PROVENANCE"
    MARKETPLACE = "MARKETPLACE"
    GENERAL = "GENERAL"


class Evidence(BaseModel):
    """Represents a discrete piece of evidence collected during an investigation."""

    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: EvidenceType = EvidenceType.METADATA
    content: str = ""
    metadata: dict = Field(default_factory=dict)

    # Sprint 1 Structured Evidence Fields
    agent_name: str = "Unknown"
    category: str = "GENERAL"
    title: str = "Evidence Observation"
    description: str = ""
    severity: str = "medium"  # "critical" | "high" | "medium" | "low" | "info"
    confidence: float = 0.5
    source: str = "System"
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

    # Sprint 1.5 Directed Evidence Graph Lineage
    derived_from: List[str] = Field(default_factory=list)
    consumed_by: List[str] = Field(default_factory=list)
    supports: List[str] = Field(default_factory=list)
    conflicts_with: List[str] = Field(default_factory=list)

    # Attribution & Legacy Compatibility
    source_agent: str = "Unknown"
    supporting_files: List[str] = Field(default_factory=list)
    reasoning: str = ""
    validation_status: ValidationStatus = ValidationStatus.PENDING

    def model_post_init(self, __context: Any) -> None:
        if self.agent_name == "Unknown" and self.source_agent != "Unknown":
            self.agent_name = self.source_agent
        elif self.source_agent == "Unknown" and self.agent_name != "Unknown":
            self.source_agent = self.agent_name

        if not self.description and self.content:
            self.description = self.content
        elif not self.content and self.description:
            self.content = self.description

        if not self.reasoning and self.description:
            self.reasoning = self.description

        # Normalize category
        cat_upper = (self.category or "GENERAL").upper()
        if cat_upper in EvidenceCategory.__members__:
            self.category = cat_upper
        else:
            self.category = "GENERAL"

    @property
    def id(self) -> str:
        return self.evidence_id


class ConfidenceStep(BaseModel):
    previous_confidence: float
    current_confidence: float
    reason: str
    agent: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class ReasoningStep(BaseModel):
    sequence_number: int
    originating_evidence_ids: List[str] = Field(default_factory=list)
    confidence_impact: float = 0.0
    explanation: str
    agent_name: str


class SellerIdentity(BaseModel):
    """Core identification data for a seller."""

    name: str
    domain: Optional[str] = None
    marketplace_id: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None


class SellerProfile(BaseModel):
    """Long-term profile of a seller across multiple investigations."""

    identity: SellerIdentity
    overall_trust_score: float = 50.0
    previous_episode_ids: List[str] = Field(default_factory=list)


class InvestigationEpisode(BaseModel):
    """A complete historical record of a single investigation."""

    id: str
    seller_identity: SellerIdentity
    marketplace: Optional[str]
    investigation_timestamp: datetime = Field(default_factory=datetime.utcnow)
    verdict: str
    risk_score: float
    summary: str
    evidence_list: List[Evidence] = Field(default_factory=list)


class MemorySearchResult(BaseModel):
    """Wrapper for a retrieved episode containing semantic similarity scores."""

    episode: InvestigationEpisode
    similarity_score: float

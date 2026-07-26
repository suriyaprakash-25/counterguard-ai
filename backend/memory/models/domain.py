import uuid
from datetime import datetime
from enum import Enum
from typing import List, Optional

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


class Evidence(BaseModel):
    """Represents a discrete piece of evidence collected during an investigation."""

    evidence_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    evidence_type: EvidenceType
    content: str
    metadata: dict = Field(default_factory=dict)

    # Evidence Attribution (Sprint 12)
    source_agent: str = "Unknown"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    confidence: float = 0.5
    supporting_files: List[str] = Field(default_factory=list)
    reasoning: str = ""
    validation_status: ValidationStatus = ValidationStatus.PENDING


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

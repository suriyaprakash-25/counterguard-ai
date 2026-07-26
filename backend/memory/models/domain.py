from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


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

    evidence_type: EvidenceType
    content: str
    metadata: dict = Field(default_factory=dict)


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

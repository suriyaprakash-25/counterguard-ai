import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class RelationshipType(str, Enum):
    """Standardized relationship edge types within the CounterGuard Knowledge Graph."""

    # Seller & Listing associations
    OFFERS_LISTING = "OFFERS_LISTING"  # Seller -> Listing
    SOLD_BY = "SOLD_BY"  # Listing -> Seller

    # Contact correlations (for syndication and network clustering)
    HAS_CONTACT_EMAIL = "HAS_CONTACT_EMAIL"  # Seller -> Email
    HAS_CONTACT_PHONE = "HAS_CONTACT_PHONE"  # Seller -> Phone
    SHARES_CONTACT_WITH = "SHARES_CONTACT_WITH"  # Seller -> Seller

    # Brand associations & IP enforcement
    ASSOCIATED_WITH_BRAND = (
        "ASSOCIATED_WITH_BRAND"  # Listing -> Brand or Seller -> Brand
    )
    AUTHORIZED_DISTRIBUTOR = "AUTHORIZED_DISTRIBUTOR"  # Seller -> Brand
    INFRINGES_BRAND = "INFRINGES_BRAND"  # Listing -> Brand or Seller -> Brand
    COUNTERFEIT_OF = "COUNTERFEIT_OF"  # Listing -> Brand

    # Media and digital asset correlation
    CONTAINS_IMAGE = "CONTAINS_IMAGE"  # Listing -> Image
    SHARES_IMAGE_WITH = "SHARES_IMAGE_WITH"  # Listing -> Listing (replica detection)

    # General / Custom link
    RELATED_TO = "RELATED_TO"  # Entity -> Entity
    CUSTOM = "CUSTOM"


class Relationship(BaseModel):
    """
    Represents a directed, weighted relationship edge between two entities in the Knowledge Graph.
    """

    id: str = ""
    source_id: str
    target_id: str
    relationship_type: str = RelationshipType.RELATED_TO.value
    weight: float = Field(default=1.0, ge=0.0, le=10.0)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __init__(self, **data: Any):
        # Allow passing enum directly as relationship_type
        if "relationship_type" in data and isinstance(
            data["relationship_type"], RelationshipType
        ):
            data["relationship_type"] = data["relationship_type"].value

        if not data.get("id") and "source_id" in data and "target_id" in data:
            rel = data.get("relationship_type", RelationshipType.RELATED_TO.value)
            data["id"] = f"{data['source_id']}--[{rel}]-->{data['target_id']}"

        super().__init__(**data)


def create_relationship(
    source_id: str,
    target_id: str,
    relationship_type: str,
    weight: float = 1.0,
    metadata: Optional[Dict[str, Any]] = None,
    relationship_id: Optional[str] = None,
) -> Relationship:
    """Helper factory method to construct a Relationship instance cleanly."""
    return Relationship(
        id=relationship_id or "",
        source_id=source_id,
        target_id=target_id,
        relationship_type=relationship_type,
        weight=weight,
        metadata=metadata or {},
    )

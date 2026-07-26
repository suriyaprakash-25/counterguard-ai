import logging
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Entity(BaseModel):
    """
    Base class representing a general node in the CounterGuard Knowledge Graph.
    All specialized investigation entities inherit from this foundation.
    """

    id: str
    entity_type: str = "ENTITY"
    label: str = ""
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def __init__(self, **data: Any):
        super().__init__(**data)
        if not self.label and self.id:
            self.label = str(self.id)


class Seller(Entity):
    """Represents a merchant or seller entity operating on an e-commerce marketplace."""

    entity_type: str = "SELLER"
    seller_id: str = ""
    name: str = ""
    trust_score: float = 50.0
    verified_merchant: bool = False
    marketplace: Optional[str] = None

    def __init__(self, **data: Any):
        if "seller_id" not in data and "id" in data:
            data["seller_id"] = data["id"]
        if "label" not in data and "name" in data:
            data["label"] = data["name"]
        super().__init__(**data)


class Brand(Entity):
    """Represents a monitored trademarked Brand entity or rights holder."""

    entity_type: str = "BRAND"
    brand_name: str = ""
    trademark_reg_number: Optional[str] = None
    official_website: Optional[str] = None
    authorized_jurisdictions: list[str] = Field(default_factory=list)

    def __init__(self, **data: Any):
        if "label" not in data and "brand_name" in data:
            data["label"] = data["brand_name"]
        super().__init__(**data)


class Listing(Entity):
    """Represents a specific target e-commerce product listing under investigation."""

    entity_type: str = "LISTING"
    listing_id: str = ""
    title: str = ""
    price: Optional[float] = None
    currency: str = "USD"
    marketplace: Optional[str] = None
    url: Optional[str] = None
    status: str = "ACTIVE"

    def __init__(self, **data: Any):
        if "listing_id" not in data and "id" in data:
            data["listing_id"] = data["id"]
        if "label" not in data and "title" in data:
            data["label"] = data["title"]
        super().__init__(**data)


class Phone(Entity):
    """Represents a telephone contact number discovered during OSINT or scraping."""

    entity_type: str = "PHONE"
    phone_number: str = ""
    country_code: Optional[str] = None
    carrier_info: Optional[str] = None
    is_verified: bool = False

    def __init__(self, **data: Any):
        if "label" not in data and "phone_number" in data:
            data["label"] = data["phone_number"]
        super().__init__(**data)


class Email(Entity):
    """Represents an email address associated with a seller, domain registrar, or shop."""

    entity_type: str = "EMAIL"
    email_address: str = ""
    domain: Optional[str] = None
    is_disposable: bool = False
    is_whois_privacy: bool = False

    def __init__(self, **data: Any):
        if "label" not in data and "email_address" in data:
            data["label"] = data["email_address"]
        if "email_address" in data and not data.get("domain"):
            parts = str(data["email_address"]).split("@")
            if len(parts) == 2:
                data["domain"] = parts[1].lower()
        super().__init__(**data)


class Image(Entity):
    """Represents a product catalog image, scraped photo, or studio visual asset."""

    entity_type: str = "IMAGE"
    image_url: str = ""
    perceptual_hash: Optional[str] = None
    is_replica_or_stolen: bool = False
    source_domain: Optional[str] = None

    def __init__(self, **data: Any):
        if "label" not in data and "image_url" in data:
            data["label"] = data["image_url"].split("/")[-1] or data["image_url"]
        super().__init__(**data)

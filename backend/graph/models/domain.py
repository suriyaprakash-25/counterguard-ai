from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class RelationshipType(str, Enum):
    USES_PHONE = "USES_PHONE"
    USES_EMAIL = "USES_EMAIL"
    USES_ADDRESS = "USES_ADDRESS"
    LISTED_ON = "LISTED_ON"
    SELLS_PRODUCT = "SELLS_PRODUCT"
    USES_IMAGE = "USES_IMAGE"
    USES_INVOICE = "USES_INVOICE"
    INVESTIGATED_IN = "INVESTIGATED_IN"
    CONNECTED_TO = "CONNECTED_TO"


class GraphNode(BaseModel):
    """Base class for all graph nodes."""

    id: str
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class SellerNode(GraphNode):
    label: str = "Seller"

    @classmethod
    def create(cls, seller_name: str, **kwargs) -> "SellerNode":
        return cls(
            id=f"seller_{seller_name.lower().replace(' ', '_')}",
            properties={"name": seller_name, **kwargs},
        )


class PhoneNode(GraphNode):
    label: str = "Phone"

    @classmethod
    def create(cls, phone_number: str) -> "PhoneNode":
        return cls(id=f"phone_{phone_number}", properties={"number": phone_number})


class EmailNode(GraphNode):
    label: str = "Email"

    @classmethod
    def create(cls, email: str) -> "EmailNode":
        return cls(id=f"email_{email.lower()}", properties={"address": email.lower()})


class AddressNode(GraphNode):
    label: str = "Address"

    @classmethod
    def create(cls, address: str) -> "AddressNode":
        import hashlib

        addr_hash = hashlib.md5(address.lower().encode()).hexdigest()
        return cls(id=f"addr_{addr_hash}", properties={"full_address": address})


class MarketplaceNode(GraphNode):
    label: str = "Marketplace"

    @classmethod
    def create(cls, name: str) -> "MarketplaceNode":
        return cls(id=f"mp_{name.lower()}", properties={"name": name})


class ProductNode(GraphNode):
    label: str = "Product"

    @classmethod
    def create(cls, title: str, brand: str = "") -> "ProductNode":
        import hashlib

        prod_hash = hashlib.md5(f"{brand}_{title}".lower().encode()).hexdigest()
        return cls(id=f"prod_{prod_hash}", properties={"title": title, "brand": brand})


class InvoiceNode(GraphNode):
    label: str = "Invoice"

    @classmethod
    def create(cls, invoice_id: str) -> "InvoiceNode":
        return cls(id=f"inv_{invoice_id}", properties={"invoice_id": invoice_id})


class ImageNode(GraphNode):
    label: str = "Image"

    @classmethod
    def create(cls, image_hash: str) -> "ImageNode":
        return cls(id=f"img_{image_hash}", properties={"hash": image_hash})


class InvestigationNode(GraphNode):
    label: str = "Investigation"

    @classmethod
    def create(
        cls, episode_id: str, verdict: str, risk_score: float
    ) -> "InvestigationNode":
        return cls(
            id=f"inv_ep_{episode_id}",
            properties={
                "episode_id": episode_id,
                "verdict": verdict,
                "risk_score": risk_score,
            },
        )

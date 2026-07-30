from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class OfficialProductProfile(BaseModel):
    """
    Extensible Pydantic model representing a verified, official product baseline profile.
    Used by ReferenceDiscoveryAgent and ReferenceDiscoveryService to provide structured
    ground-truth product metadata for comparison across all specialist agents.
    """

    brand: str = Field(
        ..., description="Official brand name (e.g., 'Nothing', 'Nike', 'Apple')"
    )
    product_name: str = Field(..., description="Official product title/name")
    normalized_name: str = Field(
        ..., description="Normalized product name for canonical comparison"
    )
    category: Optional[str] = Field(
        None, description="Product category (e.g., 'Audio', 'Footwear')"
    )
    model_number: Optional[str] = Field(
        None, description="Official manufacturer SKU or model number"
    )
    manufacturer: Optional[str] = Field(None, description="Legal manufacturer entity")
    official_url: Optional[str] = Field(
        None, description="Canonical official product store URL"
    )
    official_images: List[str] = Field(
        default_factory=list, description="Verified high-resolution brand image URLs"
    )
    specifications: Dict[str, Any] = Field(
        default_factory=dict, description="Technical specifications key-value map"
    )
    colors: List[str] = Field(
        default_factory=list, description="Official color variants"
    )
    msrp: Optional[float] = Field(
        None, description="Manufacturer's Suggested Retail Price (MSRP)"
    )
    currency: str = Field("INR", description="Price currency code")
    warranty: Optional[str] = Field(
        None, description="Official manufacturer warranty terms"
    )
    source: str = Field(
        "placeholder",
        description="Provenance source indicator (e.g., 'brand_catalog', 'web_search')",
    )
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Verification confidence score between 0.0 and 1.0",
    )
    last_verified: Optional[str] = Field(
        None, description="ISO timestamp of last verification check"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata storage for provider attributes",
    )

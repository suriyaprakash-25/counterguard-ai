from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class RetrievedProduct(BaseModel):
    product_name: str
    brand: str
    model: str
    store: str
    store_type: str = "Official Store"  # "Official Store" | "Authorized Retailer" | "Trusted Marketplace"
    official: bool = True
    price: float
    currency: str = "USD"
    availability: str = "In Stock"
    warranty: str = "Official Manufacturer Warranty"
    image_url: Optional[str] = None
    product_url: str
    retrieved_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    source_provider: str = "Direct Brand Search"
    domain: str = "official"
    metadata_completeness: float = 1.0
    search_confidence: int = 90
    score: int = 90
    verification_badge: str = "🟢 Official Store"
    verification_reason: str = "Official Manufacturer Flagship"
    why_recommended: str = "Exact model match from verified official store."


class ProductNormalized(BaseModel):
    brand: str
    model: str
    category: str
    variant: Optional[str] = None
    normalized_title: str


class TrustedProductResult(BaseModel):
    normalized_product: ProductNormalized
    recommended_products: List[RetrievedProduct] = Field(default_factory=list)
    comparison: Optional[Dict[str, Any]] = None
    search_status: str = "success"
    message: Optional[str] = None

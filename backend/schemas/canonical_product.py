from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.schemas.extraction_evidence import ExtractionEvidence


class CanonicalProductKnowledge(BaseModel):
    """
    Unified, source-agnostic knowledge representation consumed by all downstream specialist agents.
    Fuses information from Official Website profiles, FCC database, BIS certifications,
    GSMArena specs, and retail catalogs into a canonical ground-truth reference object.
    """

    brand: str = Field(..., description="Normalized canonical brand name")
    product_name: str = Field(..., description="Normalized canonical product name")
    canonical_id: str = Field(
        ..., description="Unique slug/key identifying this canonical product entity"
    )
    category: str = Field("General", description="Normalized category classification")
    model_number: Optional[str] = Field(None, description="Official SKU / Model Number")
    manufacturer: Optional[str] = Field(None, description="Legal manufacturing entity")
    official_url: Optional[str] = Field(
        None, description="Verified canonical official product URL"
    )
    msrp: Optional[float] = Field(None, description="Canonical benchmark MSRP value")
    currency: str = Field("INR", description="Price currency code")
    verified_images: List[str] = Field(
        default_factory=list, description="Golden reference image URLs"
    )
    canonical_specs: Dict[str, Any] = Field(
        default_factory=dict, description="Normalized technical specifications"
    )
    variants: List[str] = Field(
        default_factory=list, description="Official color/storage variant strings"
    )
    certifications: List[str] = Field(
        default_factory=list, description="Regulatory compliance badges (BIS, CE, FCC)"
    )
    warranty_terms: Optional[str] = Field(
        None, description="Canonical warranty terms string"
    )
    overall_confidence: float = Field(
        0.0, ge=0.0, le=1.0, description="Fused knowledge confidence score"
    )
    provenance_sources: List[str] = Field(
        default_factory=list,
        description="List of contributing sources (e.g. 'official_site', 'bis_db')",
    )
    evidence_trail: List[ExtractionEvidence] = Field(
        default_factory=list, description="Traceable evidence items from all sources"
    )
    last_updated: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO UTC timestamp of knowledge compilation",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extensible metadata container"
    )

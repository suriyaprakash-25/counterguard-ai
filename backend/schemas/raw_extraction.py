from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from backend.schemas.extraction_evidence import ExtractionEvidence


class RawExtractionResult(BaseModel):
    """
    Intermediate un-normalized extraction data container returned by an ExtractionProvider.
    Captures raw scraped strings, unstructured specs, images, and evidence trails prior to normalization.
    """

    url: str = Field(..., description="Target webpage URL that was extracted")
    provider: str = Field(..., description="Name of the ExtractionProvider used")
    raw_title: Optional[str] = Field(
        None, description="Unprocessed product title string"
    )
    raw_brand: Optional[str] = Field(None, description="Unprocessed brand string")
    raw_price_str: Optional[str] = Field(
        None, description="Raw price string (e.g. '$199.99', 'Rs. 4,999')"
    )
    raw_currency: Optional[str] = Field(
        None, description="Extracted currency symbol or ISO code"
    )
    raw_images: List[str] = Field(
        default_factory=list, description="Raw image URLs extracted from DOM"
    )
    raw_specs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Unstructured technical specification key-value pairs",
    )
    raw_description: Optional[str] = Field(
        None, description="Raw product description text"
    )
    raw_warranty: Optional[str] = Field(None, description="Raw warranty text snippet")
    evidence_trail: List[ExtractionEvidence] = Field(
        default_factory=list,
        description="Traceable evidence items proving field extraction provenance",
    )
    extraction_method: str = Field(
        "html",
        description="Extraction strategy: 'html', 'json_ld', 'structured_api', 'dom'",
    )
    extraction_time_ms: float = Field(
        0.0, description="Extraction duration in milliseconds"
    )
    confidence: float = Field(
        0.0, ge=0.0, le=1.0, description="Raw extraction quality confidence score"
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO UTC timestamp of extraction",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extensible metadata attributes"
    )

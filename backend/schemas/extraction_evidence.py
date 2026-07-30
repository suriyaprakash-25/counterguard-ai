from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class ExtractionEvidence(BaseModel):
    """
    Represents an evidence trail entry proving provenance and traceability for extracted fields.
    Records the source URL, provider strategy, CSS selector/XPath, and confidence score.
    """

    field: str = Field(
        ..., description="Field name (e.g. 'title', 'price', 'battery_capacity')"
    )
    value: Any = Field(..., description="Extracted field value")
    css_selector: Optional[str] = Field(
        None, description="CSS selector used for extraction if applicable"
    )
    xpath: Optional[str] = Field(
        None, description="XPath expression used for extraction if applicable"
    )
    source_url: str = Field(
        ..., description="Origin URL from which the field was extracted"
    )
    provider: str = Field(..., description="Name of the ExtractionProvider used")
    confidence: float = Field(
        0.0,
        ge=0.0,
        le=1.0,
        description="Extraction confidence score between 0.0 and 1.0",
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO UTC timestamp of extraction",
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extensible metadata attributes"
    )

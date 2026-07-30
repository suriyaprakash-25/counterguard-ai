from typing import List

from pydantic import BaseModel, Field


class BrandIntelligenceResult(BaseModel):
    """Output schema for BrandIntelligenceAgent."""

    official_brand: str = "Unknown"
    manufacturer: str = "Unknown"
    product_family: str = "General"
    catalog_match: bool = False
    suspicious_branding_flags: List[str] = Field(default_factory=list)
    risk_score: int = Field(50, ge=0, le=100)
    reasoning: str = ""


class SpecificationValidationResult(BaseModel):
    """Output schema for SpecificationValidationAgent."""

    missing_specs: List[str] = Field(default_factory=list)
    impossible_specs: List[str] = Field(default_factory=list)
    inconsistent_specs: List[str] = Field(default_factory=list)
    validated_specs: dict = Field(default_factory=dict)
    risk_score: int = Field(50, ge=0, le=100)
    reasoning: str = ""


class AuthorizedSellerResult(BaseModel):
    """Output schema for AuthorizedSellerAgent."""

    seller_type: str = Field(
        "unknown_seller",
        description="official_seller | marketplace_fulfilled | verified_seller | trusted_reseller | unknown_seller",
    )
    is_official: bool = False
    confidence_boost: float = 0.0
    risk_score: int = Field(50, ge=0, le=100)
    reasoning: str = ""


class MetadataIntelligenceResult(BaseModel):
    """Output schema for MetadataIntelligenceAgent."""

    keyword_stuffing_detected: bool = False
    spam_score: int = Field(0, ge=0, le=100)
    grammar_anomaly_score: int = Field(0, ge=0, le=100)
    duplicate_wording_detected: bool = False
    image_metadata_flags: List[str] = Field(default_factory=list)
    risk_score: int = Field(50, ge=0, le=100)
    reasoning: str = ""

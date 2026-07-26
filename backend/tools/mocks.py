from typing import Optional

from pydantic import BaseModel

from backend.tools.base import BaseTool


# ---------------------------------------------------------
# Mock Trademark Tool
# ---------------------------------------------------------
class TrademarkInput(BaseModel):
    brand_name: str


class TrademarkOutput(BaseModel):
    is_registered: bool
    owner: Optional[str]
    status: str


class MockTrademarkTool(BaseTool[TrademarkInput, TrademarkOutput]):
    @property
    def name(self) -> str:
        return "trademark_lookup"

    @property
    def description(self) -> str:
        return "Looks up the trademark registration status for a given brand name."

    @property
    def input_schema(self) -> type[TrademarkInput]:
        return TrademarkInput

    @property
    def output_schema(self) -> type[TrademarkOutput]:
        return TrademarkOutput

    def run(self, input_data: TrademarkInput) -> TrademarkOutput:
        # Mock logic
        brand = input_data.brand_name.lower()
        if brand in ["nike", "apple", "rolex", "gucci"]:
            return TrademarkOutput(
                is_registered=True, owner=brand.capitalize(), status="ACTIVE"
            )
        return TrademarkOutput(is_registered=False, owner=None, status="UNREGISTERED")


# ---------------------------------------------------------
# Mock WHOIS Tool
# ---------------------------------------------------------
class WhoisInput(BaseModel):
    domain: str


class WhoisOutput(BaseModel):
    domain_age_days: int
    registrar: str
    is_private: bool


class MockWhoisTool(BaseTool[WhoisInput, WhoisOutput]):
    @property
    def name(self) -> str:
        return "whois_lookup"

    @property
    def description(self) -> str:
        return "Looks up domain age and registration details."

    @property
    def input_schema(self) -> type[WhoisInput]:
        return WhoisInput

    @property
    def output_schema(self) -> type[WhoisOutput]:
        return WhoisOutput

    @property
    def cacheable(self) -> bool:
        return True

    def run(self, input_data: WhoisInput) -> WhoisOutput:
        # Mock logic
        domain = input_data.domain.lower()
        if "amazon" in domain or "ebay" in domain:
            return WhoisOutput(
                domain_age_days=5000, registrar="MarkMonitor", is_private=False
            )
        return WhoisOutput(
            domain_age_days=15, registrar="CheapDomains", is_private=True
        )


# ---------------------------------------------------------
# Mock Price Verification Tool
# ---------------------------------------------------------
class PriceInput(BaseModel):
    product_name: str


class PriceOutput(BaseModel):
    average_msrp: float
    lowest_historical_price: float


class MockPriceVerificationTool(BaseTool[PriceInput, PriceOutput]):
    @property
    def name(self) -> str:
        return "price_history"

    @property
    def description(self) -> str:
        return (
            "Fetches the historical MSRP for a product to detect unrealistic discounts."
        )

    @property
    def input_schema(self) -> type[PriceInput]:
        return PriceInput

    @property
    def output_schema(self) -> type[PriceOutput]:
        return PriceOutput

    def run(self, input_data: PriceInput) -> PriceOutput:
        # Mock logic
        return PriceOutput(average_msrp=250.0, lowest_historical_price=180.0)


# ---------------------------------------------------------
# Mock Reverse Image Tool
# ---------------------------------------------------------
class ImageInput(BaseModel):
    image_url: str


class ImageOutput(BaseModel):
    stock_photo_match_probability: float
    stolen_image: bool


class MockReverseImageTool(BaseTool[ImageInput, ImageOutput]):
    @property
    def name(self) -> str:
        return "reverse_image_search"

    @property
    def description(self) -> str:
        return "Checks if a product image is stolen or a generic stock photo."

    @property
    def input_schema(self) -> type[ImageInput]:
        return ImageInput

    @property
    def output_schema(self) -> type[ImageOutput]:
        return ImageOutput

    def run(self, input_data: ImageInput) -> ImageOutput:
        # Mock logic
        return ImageOutput(stock_photo_match_probability=0.85, stolen_image=True)


# ---------------------------------------------------------
# Mock Seller Reputation Tool
# ---------------------------------------------------------
class ReputationInput(BaseModel):
    seller_name: str


class ReputationOutput(BaseModel):
    trust_score: float
    total_reviews: int
    is_verified: bool


class MockSellerReputationTool(BaseTool[ReputationInput, ReputationOutput]):
    @property
    def name(self) -> str:
        return "seller_reputation"

    @property
    def description(self) -> str:
        return "Fetches external marketplace reputation data for the seller."

    @property
    def input_schema(self) -> type[ReputationInput]:
        return ReputationInput

    @property
    def output_schema(self) -> type[ReputationOutput]:
        return ReputationOutput

    def run(self, input_data: ReputationInput) -> ReputationOutput:
        # Mock logic
        return ReputationOutput(trust_score=88.5, total_reviews=1200, is_verified=True)


# ---------------------------------------------------------
# Mock Product Catalog Tool
# ---------------------------------------------------------
class CatalogInput(BaseModel):
    brand_name: str
    product_title: str


class CatalogOutput(BaseModel):
    in_catalog: bool
    expected_materials: str
    release_year: int


class MockProductCatalogTool(BaseTool[CatalogInput, CatalogOutput]):
    @property
    def name(self) -> str:
        return "product_catalog"

    @property
    def description(self) -> str:
        return "Checks the manufacturer catalog to verify product specifications."

    @property
    def input_schema(self) -> type[CatalogInput]:
        return CatalogInput

    @property
    def output_schema(self) -> type[CatalogOutput]:
        return CatalogOutput

    def run(self, input_data: CatalogInput) -> CatalogOutput:
        # Mock logic
        return CatalogOutput(
            in_catalog=True,
            expected_materials="Leather, Stainless Steel",
            release_year=2023,
        )

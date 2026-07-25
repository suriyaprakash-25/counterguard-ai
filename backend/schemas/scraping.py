from typing import Optional

from pydantic import BaseModel


class ParsedListing(BaseModel):
    title: Optional[str] = None
    price: Optional[float] = None
    seller_name: Optional[str] = None
    seller_rating: Optional[float] = None
    brand: Optional[str] = None
    images_count: int = 0
    description: Optional[str] = None
    availability: Optional[str] = None
    warranty_info: Optional[str] = None
    marketplace: Optional[str] = None
    currency: Optional[str] = None
    shipping: Optional[str] = None
    category: Optional[str] = None


class ScrapingResult(BaseModel):
    success: bool
    listing: Optional[ParsedListing] = None
    error_message: Optional[str] = None
    raw_html: Optional[str] = None

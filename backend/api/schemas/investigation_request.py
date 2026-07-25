from pydantic import BaseModel


class InvestigationRequest(BaseModel):
    listing_url: str
    marketplace: str

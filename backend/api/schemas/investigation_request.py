from pydantic import BaseModel
from typing import Optional

class InvestigationRequest(BaseModel):
    listing_url: str
    marketplace: str

from typing import List, Optional

from pydantic import BaseModel

from backend.graph.models.domain import (
    AddressNode,
    EmailNode,
    ImageNode,
    InvestigationNode,
    InvoiceNode,
    MarketplaceNode,
    PhoneNode,
    ProductNode,
    SellerNode,
)
from backend.memory.models.domain import InvestigationEpisode


class GraphEntities(BaseModel):
    investigation: InvestigationNode
    seller: SellerNode
    marketplace: MarketplaceNode
    product: Optional[ProductNode] = None
    phones: List[PhoneNode] = []
    emails: List[EmailNode] = []
    addresses: List[AddressNode] = []
    invoices: List[InvoiceNode] = []
    images: List[ImageNode] = []


class EntityExtractor:
    """Extracts normalized graph nodes from an InvestigationEpisode."""

    def extract(self, episode: InvestigationEpisode) -> GraphEntities:  # noqa: C901
        # Core Nodes
        investigation_node = InvestigationNode.create(
            episode_id=episode.id,
            verdict=episode.verdict,
            risk_score=episode.risk_score,
        )

        seller_node = SellerNode.create(seller_name=episode.seller_identity.name)
        marketplace_node = MarketplaceNode.create(name=episode.marketplace)

        # Optional Entities
        product_node = None
        phones = set()
        emails = set()
        addresses = set()
        invoices = set()
        images = set()

        if episode.seller_identity.phone:
            phones.add(episode.seller_identity.phone)
        if episode.seller_identity.email:
            emails.add(episode.seller_identity.email)
        if episode.seller_identity.address:
            addresses.add(episode.seller_identity.address)

        # Parse Evidence to extract more entities (Product, Invoice, Image)
        for evidence in episode.evidence_list:
            if evidence.evidence_type.value == "Product":
                product_node = ProductNode.create(
                    title=evidence.metadata.get("title", "Unknown"),
                    brand=evidence.metadata.get("brand", ""),
                )
            elif evidence.evidence_type.value == "Invoice":
                invoice_id = evidence.metadata.get("invoice_id")
                if invoice_id:
                    invoices.add(invoice_id)
            elif evidence.evidence_type.value == "Image":
                img_hash = evidence.metadata.get("image_hash")
                if img_hash:
                    images.add(img_hash)
            elif evidence.evidence_type.value == "SellerInfo":
                if "phone" in evidence.metadata:
                    phones.add(evidence.metadata["phone"])
                if "email" in evidence.metadata:
                    emails.add(evidence.metadata["email"])
                if "address" in evidence.metadata:
                    addresses.add(evidence.metadata["address"])

        return GraphEntities(
            investigation=investigation_node,
            seller=seller_node,
            marketplace=marketplace_node,
            product=product_node,
            phones=[PhoneNode.create(p) for p in phones],
            emails=[EmailNode.create(e) for e in emails],
            addresses=[AddressNode.create(a) for a in addresses],
            invoices=[InvoiceNode.create(i) for i in invoices],
            images=[ImageNode.create(i) for i in images],
        )

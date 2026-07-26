import logging

from backend.graph.extractors.entity_extractor import GraphEntities
from backend.graph.models.domain import RelationshipType
from backend.graph.repositories.interfaces import GraphRepository

logger = logging.getLogger(__name__)


class GraphBuilderService:
    """Orchestrates the construction of the knowledge graph from extracted entities."""

    def __init__(self, repository: GraphRepository):
        self.repository = repository

    def build_from_entities(self, entities: GraphEntities) -> None:  # noqa: C901
        """
        Takes extracted GraphEntities and pushes them into the graph database
        idempotently, creating all required relationships.
        """
        try:
            # 1. Create Nodes
            self.repository.create_node(entities.investigation)
            self.repository.create_node(entities.seller)
            self.repository.create_node(entities.marketplace)

            if entities.product:
                self.repository.create_node(entities.product)

            for phone in entities.phones:
                self.repository.create_node(phone)
            for email in entities.emails:
                self.repository.create_node(email)
            for addr in entities.addresses:
                self.repository.create_node(addr)
            for inv in entities.invoices:
                self.repository.create_node(inv)
            for img in entities.images:
                self.repository.create_node(img)

            # 2. Create Core Relationships

            # Investigation -> Seller
            self.repository.create_relationship(
                from_id=entities.investigation.id,
                from_label=entities.investigation.label,
                to_id=entities.seller.id,
                to_label=entities.seller.label,
                rel_type=RelationshipType.INVESTIGATED_IN,
            )

            # Seller -> Marketplace
            self.repository.create_relationship(
                from_id=entities.seller.id,
                from_label=entities.seller.label,
                to_id=entities.marketplace.id,
                to_label=entities.marketplace.label,
                rel_type=RelationshipType.LISTED_ON,
            )

            # Seller -> Product
            if entities.product:
                self.repository.create_relationship(
                    from_id=entities.seller.id,
                    from_label=entities.seller.label,
                    to_id=entities.product.id,
                    to_label=entities.product.label,
                    rel_type=RelationshipType.SELLS_PRODUCT,
                )

            # 3. Create Seller Contact Relationships
            for phone in entities.phones:
                self.repository.create_relationship(
                    from_id=entities.seller.id,
                    from_label=entities.seller.label,
                    to_id=phone.id,
                    to_label=phone.label,
                    rel_type=RelationshipType.USES_PHONE,
                )
            for email in entities.emails:
                self.repository.create_relationship(
                    from_id=entities.seller.id,
                    from_label=entities.seller.label,
                    to_id=email.id,
                    to_label=email.label,
                    rel_type=RelationshipType.USES_EMAIL,
                )
            for addr in entities.addresses:
                self.repository.create_relationship(
                    from_id=entities.seller.id,
                    from_label=entities.seller.label,
                    to_id=addr.id,
                    to_label=addr.label,
                    rel_type=RelationshipType.USES_ADDRESS,
                )

            # 4. Create Evidence Relationships (Images, Invoices)
            for img in entities.images:
                self.repository.create_relationship(
                    from_id=entities.seller.id,
                    from_label=entities.seller.label,
                    to_id=img.id,
                    to_label=img.label,
                    rel_type=RelationshipType.USES_IMAGE,
                )
            for inv in entities.invoices:
                self.repository.create_relationship(
                    from_id=entities.seller.id,
                    from_label=entities.seller.label,
                    to_id=inv.id,
                    to_label=inv.label,
                    rel_type=RelationshipType.USES_INVOICE,
                )

            logger.info(
                f"Successfully built graph for episode {entities.investigation.id}"
            )

        except Exception as e:
            logger.error(f"Failed to build graph from entities: {e}")
            raise

import pytest

from backend.knowledge import (
    Brand,
    Email,
    EntityNotFoundError,
    Image,
    InMemoryKnowledgeGraph,
    KnowledgeGraph,
    KnowledgeGraphInterface,
    Listing,
    Phone,
    Relationship,
    RelationshipInvalidError,
    RelationshipType,
    Seller,
    create_relationship,
)


def test_interface_cannot_be_instantiated():
    with pytest.raises(TypeError):
        KnowledgeGraphInterface()


# -------------------------------------------------------------------------
# Entity Creation & Model Verification
# -------------------------------------------------------------------------
def test_all_entity_types_creation():
    seller = Seller(id="sel_01", name="Global Electronics", trust_score=82.5)
    assert seller.entity_type == "SELLER"
    assert seller.label == "Global Electronics"
    assert seller.seller_id == "sel_01"

    brand = Brand(id="brd_nike", brand_name="Nike", trademark_reg_number="TM-999")
    assert brand.entity_type == "BRAND"
    assert brand.label == "Nike"
    assert brand.trademark_reg_number == "TM-999"

    listing = Listing(
        id="lst_101", title="Authentic Shoes", price=129.99, marketplace="Amazon"
    )
    assert listing.entity_type == "LISTING"
    assert listing.label == "Authentic Shoes"
    assert listing.price == 129.99

    phone = Phone(id="ph_001", phone_number="+1-555-0199", country_code="US")
    assert phone.entity_type == "PHONE"
    assert phone.label == "+1-555-0199"

    email = Email(id="em_001", email_address="support@shady-deals.com")
    assert email.entity_type == "EMAIL"
    assert email.label == "support@shady-deals.com"
    assert email.domain == "shady-deals.com"

    img = Image(
        id="img_1",
        image_url="https://shady-deals.com/photo.jpg",
        is_replica_or_stolen=True,
    )
    assert img.entity_type == "IMAGE"
    assert img.is_replica_or_stolen is True


# -------------------------------------------------------------------------
# Relationship Creation Tests
# -------------------------------------------------------------------------
def test_relationship_creation_and_defaults():
    rel = Relationship(
        source_id="sel_01",
        target_id="lst_101",
        relationship_type=RelationshipType.OFFERS_LISTING,
        weight=2.5,
    )
    assert rel.source_id == "sel_01"
    assert rel.target_id == "lst_101"
    assert rel.relationship_type == "OFFERS_LISTING"
    assert rel.weight == 2.5
    assert "OFFERS_LISTING" in rel.id

    factory_rel = create_relationship(
        "sel_01", "em_001", RelationshipType.HAS_CONTACT_EMAIL
    )
    assert factory_rel.relationship_type == "HAS_CONTACT_EMAIL"
    assert factory_rel.weight == 1.0


# -------------------------------------------------------------------------
# Knowledge Graph CRUD & Referential Integrity
# -------------------------------------------------------------------------
@pytest.fixture
def graph():
    return KnowledgeGraph()


def test_graph_node_and_edge_lifecycle(graph: InMemoryKnowledgeGraph):
    seller = Seller(id="s_1", name="Seller 1")
    listing = Listing(id="l_1", title="Listing 1")
    brand = Brand(id="b_1", brand_name="Brand 1")

    graph.add_entity(seller)
    graph.add_entity(listing)
    graph.add_entity(brand)

    assert len(graph.list_entities()) == 3
    assert len(graph.list_entities(entity_type="SELLER")) == 1
    assert len(graph.list_entities(entity_type="brand")) == 1
    assert graph.get_entity("s_1") == seller

    rel1 = create_relationship("s_1", "l_1", RelationshipType.OFFERS_LISTING)
    rel2 = create_relationship("l_1", "b_1", RelationshipType.INFRINGES_BRAND)
    graph.add_relationship(rel1)
    graph.add_relationship(rel2)

    assert len(graph.list_relationships()) == 2
    assert len(graph.list_relationships(relationship_type="INFRINGES_BRAND")) == 1

    # Verify edge invalidation error when targeting missing entity
    invalid_rel = create_relationship(
        "s_1", "missing_node", RelationshipType.RELATED_TO
    )
    with pytest.raises(RelationshipInvalidError):
        graph.add_relationship(invalid_rel)

    # Delete listing entity -> should automatically purge both connecting edges
    graph.delete_entity("l_1")
    assert graph.get_entity("l_1") is None
    assert len(graph.list_relationships()) == 0  # Both rel1 and rel2 touched l_1

    with pytest.raises(EntityNotFoundError):
        graph.delete_entity("already_deleted")


# -------------------------------------------------------------------------
# Neighborhood Queries & Directional Traversal
# -------------------------------------------------------------------------
def test_graph_neighborhood_queries(graph: InMemoryKnowledgeGraph):
    seller = Seller(id="sel_main", name="Main Merchant")
    phone1 = Phone(id="ph_1", phone_number="111-222-3333")
    email1 = Email(id="em_1", email_address="admin@merchant.com")
    listing1 = Listing(id="lst_1", title="Item A")
    listing2 = Listing(id="lst_2", title="Item B")

    for ent in [seller, phone1, email1, listing1, listing2]:
        graph.add_entity(ent)

    graph.add_relationship(
        create_relationship("sel_main", "ph_1", RelationshipType.HAS_CONTACT_PHONE)
    )
    graph.add_relationship(
        create_relationship("sel_main", "em_1", RelationshipType.HAS_CONTACT_EMAIL)
    )
    graph.add_relationship(
        create_relationship("sel_main", "lst_1", RelationshipType.OFFERS_LISTING)
    )
    graph.add_relationship(
        create_relationship("sel_main", "lst_2", RelationshipType.OFFERS_LISTING)
    )

    # All outgoing neighbors of seller
    neighbors = graph.get_neighbors("sel_main", direction="out")
    assert len(neighbors) == 4

    # Filtered by OFFERS_LISTING
    listing_neighbors = graph.get_neighbors(
        "sel_main", relationship_type="OFFERS_LISTING"
    )
    assert len(listing_neighbors) == 2
    assert all(isinstance(n, Listing) for n in listing_neighbors)

    # Incoming check from listing to seller
    incoming_to_listing = graph.get_neighbors("lst_1", direction="in")
    assert len(incoming_to_listing) == 1
    assert incoming_to_listing[0].id == "sel_main"


# -------------------------------------------------------------------------
# Multi-Hop Path Discovery & Subgraph Extraction
# -------------------------------------------------------------------------
def test_find_paths_and_subgraph(graph: InMemoryKnowledgeGraph):
    # Construct a syndication ring:
    # Seller A -> Shares Email X <- Seller B -> Offers Listing Y -> Infringes Brand Z
    s_a = Seller(id="seller_a", name="Shop A")
    em_x = Email(id="shared_email", email_address="network@scam.org")
    s_b = Seller(id="seller_b", name="Shop B")
    lst_y = Listing(id="listing_y", title="Replica Handbag")
    brd_z = Brand(id="brand_z", brand_name="LuxuryBrand")

    for ent in [s_a, em_x, s_b, lst_y, brd_z]:
        graph.add_entity(ent)

    graph.add_relationship(
        create_relationship(
            "seller_a", "shared_email", RelationshipType.HAS_CONTACT_EMAIL
        )
    )
    graph.add_relationship(
        create_relationship(
            "seller_b", "shared_email", RelationshipType.HAS_CONTACT_EMAIL
        )
    )
    graph.add_relationship(
        create_relationship("seller_b", "listing_y", RelationshipType.OFFERS_LISTING)
    )
    graph.add_relationship(
        create_relationship("listing_y", "brand_z", RelationshipType.INFRINGES_BRAND)
    )

    # Discover multi-hop path connecting Seller A to LuxuryBrand Z
    paths = graph.find_paths("seller_a", "brand_z", max_depth=4)
    assert len(paths) >= 1
    assert paths[0] == ["seller_a", "shared_email", "seller_b", "listing_y", "brand_z"]

    # Subgraph extraction depth 1 from shared_email should catch both Seller A and Seller B
    sub = graph.get_subgraph("shared_email", max_depth=1)
    assert sub["root_id"] == "shared_email"
    assert len(sub["nodes"]) == 3  # shared_email + seller_a + seller_b
    assert len(sub["edges"]) == 2

    graph.clear()
    assert len(graph.list_entities()) == 0

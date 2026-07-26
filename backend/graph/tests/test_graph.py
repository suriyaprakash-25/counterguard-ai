from unittest.mock import MagicMock

from backend.graph.extractors.entity_extractor import EntityExtractor
from backend.graph.services.builder_service import GraphBuilderService
from backend.graph.services.intelligence_service import IntelligenceService
from backend.memory.models.domain import InvestigationEpisode, SellerIdentity


def get_mock_episode() -> InvestigationEpisode:
    return InvestigationEpisode(
        id="ep-123",
        seller_identity=SellerIdentity(
            name="FraudSeller", phone="555-0101", email="fraud@seller.com"
        ),
        marketplace="Amazon",
        verdict="Counterfeit",
        risk_score=95.0,
        summary="Clear evidence of IP infringement.",
    )


def test_entity_extraction():
    episode = get_mock_episode()
    extractor = EntityExtractor()
    entities = extractor.extract(episode)

    assert entities.investigation.id == "inv_ep_ep-123"
    assert entities.seller.id == "seller_fraudseller"
    assert entities.marketplace.id == "mp_amazon"

    assert len(entities.phones) == 1
    assert entities.phones[0].id == "phone_555-0101"

    assert len(entities.emails) == 1
    assert entities.emails[0].id == "email_fraud@seller.com"


def test_graph_builder_service():
    repository = MagicMock()
    builder = GraphBuilderService(repository)
    extractor = EntityExtractor()
    entities = extractor.extract(get_mock_episode())

    builder.build_from_entities(entities)

    # Check if nodes were created
    assert repository.create_node.call_count >= 5

    # Check if relationships were created
    assert repository.create_relationship.call_count >= 4


def test_intelligence_service_shared_identifiers():
    repository = MagicMock()

    # Mocking Cypher query results
    repository.run_query.return_value = [
        {"type": "Phone", "id": "phone_555-0101", "shared_with": "OtherFraudSeller"}
    ]

    service = IntelligenceService(repository)
    shared = service.find_shared_identifiers("FraudSeller")

    assert "Phone" in shared
    assert "phone_555-0101" in shared["Phone"]
    assert "OtherFraudSeller" in shared["Sellers"]


def test_intelligence_service_network_risk():
    repository = MagicMock()

    # Mocking Cypher query returning a connected counterfeit investigation
    repository.run_query.return_value = [
        {"inv": {"id": "inv_ep_999", "verdict": "Counterfeit"}}
    ]

    service = IntelligenceService(repository)
    risk = service.calculate_seller_network_risk("FraudSeller")

    # Base 1.0 + 0.2 for the one counterfeit connected investigation
    assert risk == 1.2

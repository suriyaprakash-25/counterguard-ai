"""
test_threat_graph.py — Backend Pytest suite for Threat Knowledge Graph
Tests node creation, duplicate merging, relationship building, and REST API endpoints.
"""
from fastapi.testclient import TestClient

from backend.api.main import app
from backend.services.threat_graph_service import threat_graph_service

client = TestClient(app)


def test_threat_graph_service_seed():
    """Verify initial seeded threat graph nodes and relationships."""
    graph = threat_graph_service.get_full_graph()
    assert len(graph.nodes) >= 10
    assert len(graph.relationships) >= 5
    node_labels = {n.label for n in graph.nodes}
    assert "Product" in node_labels
    assert "Seller" in node_labels
    assert "Marketplace" in node_labels
    assert "Phone" in node_labels
    assert "Email" in node_labels
    assert "GST" in node_labels


def test_threat_graph_ingestion_and_merge():
    """Verify continuous investigation ingestion and node merging."""
    inv_payload = {
        "investigation_id": "inv-test-99",
        "title": "Counterfeit Earbuds Listing",
        "seller": "Radha Wholesale Enterprise",
        "marketplace": "Meesho",
        "risk_score": 92.0,
        "verdict": "CRITICAL",
        "seller_properties": {
            "phone": "+91 98765-43210",
            "email": "radha.wholesales@gmail.com",
        },
    }

    total_nodes = threat_graph_service.ingest_investigation(inv_payload)
    assert total_nodes >= 10

    # Retrieve seller subgraph
    seller_sub = threat_graph_service.get_seller_subgraph(
        "seller-radha-wholesale-enterprise"
    )
    assert len(seller_sub.nodes) >= 2


def test_threat_graph_api_endpoints():
    """Verify GET /api/v1/threat/graph and subgraphs."""
    resp = client.get("/api/v1/threat/graph")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "relationships" in data

    # Test seller subgraph endpoint
    resp_seller = client.get("/api/v1/threat/seller/seller-radha")
    assert resp_seller.status_code == 200
    assert "nodes" in resp_seller.json()

    # Test product subgraph endpoint
    resp_prod = client.get("/api/v1/threat/product/prod-cmf-buds")
    assert resp_prod.status_code == 200
    assert "nodes" in resp_prod.json()

from backend.collaboration.models.context import InvestigationContext
from backend.memory.models.domain import Evidence


def test_evidence_graph_lineage_and_parent_linking():
    ctx = InvestigationContext(investigation_id="inv_graph_test")

    # Node 1: Root Price Evidence
    ev1 = Evidence(
        evidence_id="ev-price-1",
        agent_name="PriceAgent",
        category="PRICE",
        title="MSRP Price Drop Anomaly",
        description="Price is 87% below market MSRP",
        severity="critical",
        confidence=0.95,
    )
    ctx.add_evidence(ev1)

    # Node 2: Derived Seller Evidence referencing Root Node 1
    ev2 = Evidence(
        evidence_id="ev-seller-2",
        agent_name="SellerAgent",
        category="SELLER",
        title="Seller Account Audit",
        description="Seller account age 8 days",
        severity="high",
        confidence=0.88,
        derived_from=["ev-price-1"],
    )
    ctx.add_evidence(ev2, derived_from_ids=["ev-price-1"])

    # Node 3: Derived Brand Evidence referencing Node 2
    ev3 = Evidence(
        evidence_id="ev-brand-3",
        agent_name="BrandIntelligenceAgent",
        category="BRAND",
        title="Brand Verification",
        description="Missing manufacturer branding metadata",
        severity="medium",
        confidence=0.82,
        derived_from=["ev-seller-2"],
    )
    ctx.add_evidence(ev3, derived_from_ids=["ev-seller-2"])

    # 1. Lineage Assertions
    assert "ev-price-1" in ev2.derived_from
    assert "ev-seller-2" in ev1.consumed_by
    assert "ev-seller-2" in ev3.derived_from
    assert "ev-brand-3" in ev2.consumed_by

    # 2. Cytoscape Graph Serialization
    graph_json = ctx.build_evidence_graph()
    assert len(graph_json["nodes"]) == 3
    assert len(graph_json["edges"]) >= 2

    edge_ids = [e["data"]["id"] for e in graph_json["edges"]]
    assert any("edge-ev-price-1-ev-seller-2-derived" in eid for eid in edge_ids)

    # 3. Validation Rules
    validation_errors = ctx.validate_context()
    assert len(validation_errors) == 0


def test_evidence_graph_circular_reference_prevention():
    ctx = InvestigationContext(investigation_id="inv_cycle_test")

    ev1 = Evidence(
        evidence_id="ev-1",
        agent_name="AgentA",
        category="PRICE",
        title="Evidence A",
        derived_from=["ev-2"],  # Cycle: 1 derived from 2
    )
    ev2 = Evidence(
        evidence_id="ev-2",
        agent_name="AgentB",
        category="SELLER",
        title="Evidence B",
        derived_from=["ev-1"],  # Cycle: 2 derived from 1
    )

    ctx.shared_evidence.extend([ev1, ev2])

    errors = ctx.validate_context()
    assert any("Circular evidence reference cycle detected" in err for err in errors)


def test_evidence_taxonomy_normalization():
    ev = Evidence(
        evidence_id="ev-tax-1",
        agent_name="MetadataAgent",
        category="metadata",  # Lowercase should normalize to METADATA
        title="Copywriting Forensics",
    )
    assert ev.category == "METADATA"

    ev_bad = Evidence(
        evidence_id="ev-tax-2",
        agent_name="UnknownAgent",
        category="INVALID_TAXONOMY",
        title="Invalid Category",
    )
    assert ev_bad.category == "GENERAL"

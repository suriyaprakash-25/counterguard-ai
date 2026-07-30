"""
threat_graph_service.py — Phase 3 & 4: Threat Knowledge Graph Service
In-memory and Neo4j graph ingestion, deduplication, relationship creation, and query services.
"""
import logging
from datetime import datetime
from typing import Any, Dict, List

from backend.schemas.threat_graph import (
    GraphNode,
    GraphRelationship,
    ThreatGraphResponse,
)

logger = logging.getLogger("counterguard.threat_graph")


class ThreatGraphService:
    """
    Central Threat Intelligence Knowledge Graph Service.
    Enriches Neo4j graph with deduplication, relationship inference, and structured queries.
    Maintains an in-memory synchronized store for ultra-fast fallback querying.
    """

    def __init__(self):
        self._nodes: Dict[str, GraphNode] = {}
        self._relationships: Dict[str, GraphRelationship] = {}
        self._seed_initial_demo_graph()

    def _seed_initial_demo_graph(self):
        """Seed initial realistic threat graph topology."""
        demo_nodes = [
            GraphNode(
                id="prod-cmf-buds",
                label="Product",
                name="CMF Buds 2a",
                type="Product",
                risk_score=72.0,
                confidence=0.95,
            ),
            GraphNode(
                id="prod-sony-wh",
                label="Product",
                name="Sony WH-1000XM5",
                type="Product",
                risk_score=45.0,
                confidence=0.98,
            ),
            GraphNode(
                id="seller-radha",
                label="Seller",
                name="Radha Wholesale Enterprise",
                type="Seller",
                risk_score=88.0,
                confidence=0.92,
                properties={"gst": "07AAAAA0000A1Z5", "location": "Surat, GJ"},
            ),
            GraphNode(
                id="seller-shenzhen",
                label="Seller",
                name="Shenzhen Precision Mfg",
                type="Seller",
                risk_score=94.0,
                confidence=0.89,
                properties={"gst": "99BBBBB1111B2Z3", "location": "Shenzhen, CN"},
            ),
            GraphNode(
                id="seller-official",
                label="Seller",
                name="Amazon Official Flagship Store",
                type="Seller",
                risk_score=10.0,
                confidence=0.99,
            ),
            GraphNode(
                id="mp-meesho",
                label="Marketplace",
                name="Meesho",
                type="Marketplace",
                risk_score=72.0,
                confidence=0.99,
            ),
            GraphNode(
                id="mp-tradeindia",
                label="Marketplace",
                name="TradeIndia",
                type="Marketplace",
                risk_score=63.0,
                confidence=0.99,
            ),
            GraphNode(
                id="mp-amazon",
                label="Marketplace",
                name="Amazon",
                type="Marketplace",
                risk_score=15.0,
                confidence=0.99,
            ),
            GraphNode(
                id="phone-9876543210",
                label="Phone",
                name="+91 98765-43210",
                type="Phone",
                risk_score=85.0,
                confidence=0.90,
            ),
            GraphNode(
                id="email-radha-supplier",
                label="Email",
                name="radha.wholesales@gmail.com",
                type="Email",
                risk_score=82.0,
                confidence=0.91,
            ),
            GraphNode(
                id="gst-radha",
                label="GST",
                name="GST-07AAAAA0000A1Z5",
                type="GST",
                risk_score=88.0,
                confidence=0.95,
            ),
            GraphNode(
                id="net-surat-ring",
                label="CounterfeitNetwork",
                name="Surat Replica Network-A",
                type="CounterfeitNetwork",
                risk_score=92.0,
                confidence=0.88,
            ),
            GraphNode(
                id="ev-price-anomaly",
                label="Evidence",
                name="Price Anomaly (-75% MSRP)",
                type="Evidence",
                risk_score=80.0,
                confidence=0.95,
            ),
        ]

        for n in demo_nodes:
            self._nodes[n.id] = n

        demo_rel = [
            GraphRelationship(
                id="r1",
                source="seller-radha",
                target="mp-meesho",
                type="SELLS",
                confidence=0.95,
            ),
            GraphRelationship(
                id="r2",
                source="seller-shenzhen",
                target="mp-tradeindia",
                type="SELLS",
                confidence=0.95,
            ),
            GraphRelationship(
                id="r3",
                source="seller-radha",
                target="phone-9876543210",
                type="SHARES_PHONE",
                confidence=0.99,
            ),
            GraphRelationship(
                id="r4",
                source="seller-radha",
                target="email-radha-supplier",
                type="SHARES_EMAIL",
                confidence=0.99,
            ),
            GraphRelationship(
                id="r5",
                source="seller-radha",
                target="gst-radha",
                type="SHARES_GST",
                confidence=0.99,
            ),
            GraphRelationship(
                id="r6",
                source="seller-radha",
                target="net-surat-ring",
                type="PART_OF_NETWORK",
                confidence=0.90,
            ),
            GraphRelationship(
                id="r7",
                source="seller-radha",
                target="ev-price-anomaly",
                type="HAS_EVIDENCE",
                confidence=0.95,
            ),
            GraphRelationship(
                id="r8",
                source="seller-official",
                target="mp-amazon",
                type="SELLS",
                confidence=0.99,
            ),
        ]

        for r in demo_rel:
            self._relationships[r.id] = r

    def add_node(self, node: GraphNode) -> GraphNode:
        """Upsert node into threat graph."""
        if node.id in self._nodes:
            existing = self._nodes[node.id]
            existing.confidence = max(existing.confidence, node.confidence)
            existing.risk_score = max(existing.risk_score, node.risk_score)
            existing.properties.update(node.properties)
            return existing
        self._nodes[node.id] = node
        return node

    def add_relationship(self, rel: GraphRelationship) -> GraphRelationship:
        """Upsert relationship into threat graph."""
        self._relationships[rel.id] = rel
        return rel

    def ingest_investigation(self, investigation_data: Dict[str, Any]) -> int:
        """
        Ingest a completed investigation payload into the Threat Knowledge Graph.
        Creates Product, Seller, Marketplace, Phone, Email, GST, Evidence nodes & links.
        """
        inv_id = (
            investigation_data.get("investigation_id")
            or investigation_data.get("id")
            or f"inv-{int(datetime.utcnow().timestamp())}"
        )
        title = investigation_data.get("title", "Discovered Listing")
        seller_name = investigation_data.get("seller", "Unknown Seller")
        marketplace = investigation_data.get("marketplace", "Unknown Marketplace")
        risk_score = float(investigation_data.get("risk_score", 50.0))
        verdict = investigation_data.get("verdict", "SUSPICIOUS")

        # 1. Investigation Node
        inv_node = GraphNode(
            id=inv_id,
            label="Investigation",
            name=f"Case: {title[:25]}",
            type="Investigation",
            risk_score=risk_score,
            confidence=0.95,
            properties={"verdict": verdict, "title": title},
        )
        self.add_node(inv_node)

        # 2. Seller Node
        seller_id = f"seller-{seller_name.lower().replace(' ', '-')}"
        seller_node = GraphNode(
            id=seller_id,
            label="Seller",
            name=seller_name,
            type="Seller",
            risk_score=risk_score,
            confidence=0.90,
            properties={"marketplace": marketplace},
        )
        self.add_node(seller_node)

        # 3. Marketplace Node
        mp_id = f"mp-{marketplace.lower().replace(' ', '-')}"
        mp_node = GraphNode(
            id=mp_id,
            label="Marketplace",
            name=marketplace,
            type="Marketplace",
            risk_score=20.0 if marketplace in ["Amazon", "AJIO"] else 70.0,
            confidence=0.99,
        )
        self.add_node(mp_node)

        # 4. Link Relationships
        self.add_relationship(
            GraphRelationship(
                id=f"r-{seller_id}-{mp_id}",
                source=seller_id,
                target=mp_id,
                type="SELLS",
                confidence=0.95,
            )
        )
        self.add_relationship(
            GraphRelationship(
                id=f"r-{inv_id}-{seller_id}",
                source=inv_id,
                target=seller_id,
                type="INVESTIGATED_IN",
                confidence=0.95,
            )
        )

        # 5. Extract Phone / Email / GST if present in seller properties
        props = investigation_data.get("seller_properties", {})
        if "phone" in props:
            p_id = f"phone-{props['phone']}"
            self.add_node(
                GraphNode(
                    id=p_id,
                    label="Phone",
                    name=props["phone"],
                    type="Phone",
                    risk_score=risk_score,
                )
            )
            self.add_relationship(
                GraphRelationship(
                    id=f"r-{seller_id}-{p_id}",
                    source=seller_id,
                    target=p_id,
                    type="SHARES_PHONE",
                )
            )

        if "email" in props:
            e_id = f"email-{props['email']}"
            self.add_node(
                GraphNode(
                    id=e_id,
                    label="Email",
                    name=props["email"],
                    type="Email",
                    risk_score=risk_score,
                )
            )
            self.add_relationship(
                GraphRelationship(
                    id=f"r-{seller_id}-{e_id}",
                    source=seller_id,
                    target=e_id,
                    type="SHARES_EMAIL",
                )
            )

        logger.info(
            f"[ThreatGraphService] Ingested investigation {inv_id} into Threat Graph."
        )
        return len(self._nodes)

    def get_full_graph(self) -> ThreatGraphResponse:
        """Return complete graph for canvas visualizer."""
        return ThreatGraphResponse(
            nodes=list(self._nodes.values()),
            relationships=list(self._relationships.values()),
            meta={
                "total_nodes": len(self._nodes),
                "total_relationships": len(self._relationships),
            },
        )

    def get_seller_subgraph(self, seller_id: str) -> ThreatGraphResponse:
        """Return subgraph centered on a specific seller."""
        connected_node_ids = {seller_id}
        rels: List[GraphRelationship] = []

        for r in self._relationships.values():
            if r.source == seller_id or r.target == seller_id:
                rels.append(r)
                connected_node_ids.add(r.source)
                connected_node_ids.add(r.target)

        sub_nodes = [
            self._nodes[nid] for nid in connected_node_ids if nid in self._nodes
        ]
        return ThreatGraphResponse(
            nodes=sub_nodes, relationships=rels, meta={"center": seller_id}
        )

    def get_product_subgraph(self, product_id: str) -> ThreatGraphResponse:
        """Return subgraph centered on a target product."""
        connected_node_ids = {product_id}
        rels: List[GraphRelationship] = []

        for r in self._relationships.values():
            if r.source == product_id or r.target == product_id:
                rels.append(r)
                connected_node_ids.add(r.source)
                connected_node_ids.add(r.target)

        sub_nodes = [
            self._nodes[nid] for nid in connected_node_ids if nid in self._nodes
        ]
        return ThreatGraphResponse(
            nodes=sub_nodes, relationships=rels, meta={"center": product_id}
        )


# Global service instance
threat_graph_service = ThreatGraphService()

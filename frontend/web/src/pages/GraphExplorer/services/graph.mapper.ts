import type { GraphData, GraphNode, GraphEdge, GraphStatistics, NodeDetails } from "../models/graph";

export const GraphMapper = {
  toGraphData(dto: any): GraphData {
    const rawNodes = dto.nodes ?? dto.elements?.nodes ?? [];
    const rawEdges = dto.relationships ?? dto.edges ?? dto.elements?.edges ?? [];

    const nodes: GraphNode[] = rawNodes.map((n: any) => ({
      id: n.data?.id ?? n.id,
      label: n.data?.name ?? n.name ?? n.data?.label ?? n.label,
      type: n.data?.type ?? n.type ?? n.label ?? 'unknown',
      riskScore: n.data?.riskScore ?? n.data?.risk_score ?? n.risk_score ?? n.riskScore ?? 50,
      properties: n.data?.props ?? n.properties ?? {}
    }));

    const edges: GraphEdge[] = rawEdges.map((e: any) => ({
      id: e.data?.id ?? e.id,
      source: e.data?.source ?? e.source,
      target: e.data?.target ?? e.target,
      label: e.data?.type ?? e.type ?? e.data?.label ?? e.label ?? ''
    }));

    const layout = dto.layout && dto.layout.name ? dto.layout : { name: "cose" };

    return { nodes, edges, layout };
  },

  toStatistics(dto: any): GraphStatistics {
    return {
      totalNodes: dto.n_count ?? dto.totalNodes ?? 0,
      totalEdges: dto.r_count ?? dto.totalEdges ?? 0,
      communities: dto.comm_count ?? dto.communities ?? 0,
      largestComponent: dto.largest_comp ?? dto.largestComponent ?? 0,
      averageDegree: dto.avg_deg ?? dto.averageDegree ?? 0.0,
      mostConnectedSeller: dto.top_seller ?? dto.mostConnectedSeller ?? "Global Outlet"
    };
  },

  toNodeDetails(dto: any): NodeDetails {
    if (!dto) {
      throw new Error("Node details object is empty");
    }
    const rawNode = dto.node || dto;
    return {
      node: {
        id: rawNode.id || dto.id || "unknown-node",
        label: rawNode.label || dto.label || "Unnamed Entity",
        type: rawNode.type || dto.type || "product",
        riskScore: rawNode.riskScore ?? rawNode.risk_score ?? dto.riskScore ?? dto.risk_score ?? 75,
        properties: rawNode.properties || rawNode.props || dto.properties || dto.props || {}
      },
      degree: dto.degree ?? (dto.connectedEntities?.length || dto.connected_edges?.length || 3),
      relatedInvestigations: dto.relatedInvestigations ?? dto.related_investigations ?? 2,
      confidence: dto.confidence ?? 95,
      connectedEntities: (dto.connectedEntities || dto.connected_entities || []).map((e: any) => ({
        id: e.id || e.target || e.source || "entity",
        label: e.label || e.target || e.id || "Connected Entity",
        type: e.type || "entity",
        relationship: e.relationship || e.label || "connected_to"
      }))
    };
  }
};

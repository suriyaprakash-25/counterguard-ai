import type { GraphData, GraphNode, GraphEdge, GraphStatistics } from "../models/graph";

export const GraphMapper = {
  toGraphData(dto: any): GraphData {
    const nodes: GraphNode[] = dto.elements.nodes.map((n: any) => ({
      id: n.data.id,
      label: n.data.label,
      type: n.data.type,
      riskScore: n.data.risk,
      properties: n.data.props
    }));

    const edges: GraphEdge[] = dto.elements.edges.map((e: any) => ({
      id: e.data.id,
      source: e.data.source,
      target: e.data.target,
      label: e.data.label
    }));

    return { nodes, edges };
  },

  toStatistics(dto: any): GraphStatistics {
    return {
      totalNodes: dto.n_count,
      totalEdges: dto.r_count,
      communities: dto.comm_count,
      largestComponent: dto.largest_comp,
      averageDegree: dto.avg_deg,
      mostConnectedSeller: dto.top_seller
    };
  }
};

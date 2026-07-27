import { GraphMapper } from "./graph.mapper";
import { MOCK_GRAPH_DTO, MOCK_GRAPH_STATS_DTO } from "./graph.mock";
import type { NodeDetails } from "../models/graph";

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const graphService = {
  async getGraphData() {
    await delay(1200);
    return GraphMapper.toGraphData(MOCK_GRAPH_DTO);
  },

  async getGraphStats() {
    await delay(800);
    return GraphMapper.toStatistics(MOCK_GRAPH_STATS_DTO);
  },

  async getNodeDetails(nodeId: string): Promise<NodeDetails> {
    await delay(400);
    const data = GraphMapper.toGraphData(MOCK_GRAPH_DTO);
    const node = data.nodes.find(n => n.id === nodeId);
    if (!node) throw new Error("Node not found");

    const connectedEdges = data.edges.filter(e => e.source === nodeId || e.target === nodeId);
    const connectedEntities = connectedEdges.map(e => {
      const otherId = e.source === nodeId ? e.target : e.source;
      const otherNode = data.nodes.find(n => n.id === otherId)!;
      return {
        id: otherNode.id,
        label: otherNode.label,
        type: otherNode.type,
        relationship: e.label
      };
    });

    return {
      node,
      degree: connectedEdges.length,
      relatedInvestigations: Math.floor(Math.random() * 10),
      confidence: Math.floor(Math.random() * 20) + 80,
      connectedEntities
    };
  }
};

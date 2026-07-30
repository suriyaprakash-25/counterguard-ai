import { apiClient, endpoints } from '../../../shared/api';
import { GraphMapper } from './graph.mapper';
import type { GraphData, GraphStatistics, NodeDetails } from '../models/graph';

export const GraphRepository = {
  async getGraphData(): Promise<GraphData> {
    const { data } = await apiClient.get(endpoints.threatGraph.full);
    return GraphMapper.toGraphData(data);
  },

  async getGraphStats(): Promise<GraphStatistics> {
    const { data } = await apiClient.get(endpoints.graph.stats);
    return GraphMapper.toStatistics(data.data);
  },

  async getNodeDetails(nodeId: string): Promise<NodeDetails> {
    if (!nodeId) throw new Error("No nodeId provided");
    const { data } = await apiClient.get(endpoints.graph.nodeDetails(nodeId));
    return GraphMapper.toNodeDetails(data.data);
  }
};

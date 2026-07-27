import { apiClient, endpoints } from '../../../shared/api';
import { GraphMapper } from './graph.mapper';
import type { GraphData } from '../models/graph';

export const GraphRepository = {
  async getGraphData(): Promise<GraphData> {
    const { data } = await apiClient.get(endpoints.graph.data);
    return GraphMapper.toGraphData(data.data);
  }
};

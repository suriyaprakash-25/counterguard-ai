import { apiClient, endpoints } from '../../../shared/api';

export const IntelligenceRepository = {
  async getIntelligence(): Promise<any> {
    const { data } = await apiClient.get(endpoints.intelligence.globalSummary);
    // Backend now returns camelCase directly
    return data.data;
  },

  async getSellers(): Promise<any[]> {
    const { data } = await apiClient.get(endpoints.intelligence.knownSellers);
    return data.data ?? [];
  },

  async getFraudRings(): Promise<any[]> {
    const { data } = await apiClient.get(endpoints.intelligence.fraudRings);
    return data.data ?? [];
  },

  async getPatterns(): Promise<any[]> {
    const { data } = await apiClient.get(endpoints.intelligence.knownPatterns);
    return data.data ?? [];
  },

  async getImages(): Promise<any[]> {
    const { data } = await apiClient.get(endpoints.intelligence.repeatedImages);
    return data.data ?? [];
  },

  async getPhones(): Promise<any[]> {
    const { data } = await apiClient.get(endpoints.intelligence.repeatedPhones);
    return data.data ?? [];
  },

  async getInvoices(): Promise<any[]> {
    const { data } = await apiClient.get(endpoints.intelligence.repeatedInvoices);
    return data.data ?? [];
  },

  async getMemoryInsights(): Promise<any[]> {
    const { data } = await apiClient.get(endpoints.intelligence.memoryInsights);
    return data.data ?? [];
  },

  async getGraphStats(): Promise<any> {
    const { data } = await apiClient.get('/api/v1/graph/stats');
    const d = data.data;
    return {
      nodeCount: d.n_count ?? d.totalNodes ?? 0,
      relationshipCount: d.r_count ?? d.totalEdges ?? 0,
      communities: d.comm_count ?? d.communities ?? 0,
      largestFraudRingSize: d.largest_comp ?? d.largestComponent ?? 0,
      averageConnectivity: d.avg_deg ?? d.averageDegree ?? 0,
      graphDensity: d.density ?? 0,
    };
  },
};

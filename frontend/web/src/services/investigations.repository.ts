import { apiClient, endpoints } from '../shared/api';
import type { InvestigationSummary, InvestigationWorkspaceDetails, TimelineEvent } from '../types/investigations';
import { InvestigationsMapper } from './investigations.mapper';

export const InvestigationRepository = {
  async getInvestigations(page: number, filters: any): Promise<any> {
    const { data } = await apiClient.get(endpoints.investigations.list, { params: { page, ...filters } });
    const items = data.data.items || data.data || [];
    return items.map((item: any) => InvestigationsMapper.toSummary(item));
  },

  async getInvestigation(id: string): Promise<InvestigationWorkspaceDetails> {
    const { data } = await apiClient.get(endpoints.investigations.details(id));
    return InvestigationsMapper.toWorkspaceDetails(data.data);
  },

  async getTimeline(id: string): Promise<TimelineEvent[]> {
    const { data } = await apiClient.get(endpoints.investigations.timeline(id));
    return data.data;
  },

  async createInvestigation(payload: any): Promise<{ id: string }> {
    const { data } = await apiClient.post(endpoints.investigations.create, payload);
    return data.data;
  },

  async deleteInvestigation(id: string): Promise<void> {
    await apiClient.delete(endpoints.investigations.delete(id));
  },

  async cancelInvestigation(id: string): Promise<void> {
    await apiClient.post(endpoints.investigations.cancel(id));
  },

  async retryInvestigation(id: string): Promise<void> {
    await apiClient.post(endpoints.investigations.retry(id));
  },

  async getGraph(id: string): Promise<any> {
    const { data } = await apiClient.get(endpoints.investigations.graph(id));
    return data.data;
  },

  async getReasoning(id: string): Promise<any> {
    const { data } = await apiClient.get(endpoints.investigations.reasoning(id));
    return data.data;
  },

  async getReport(id: string): Promise<any> {
    const { data } = await apiClient.get(endpoints.investigations.report(id));
    return data.data;
  }
};

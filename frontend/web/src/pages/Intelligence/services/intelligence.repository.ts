import { apiClient, endpoints } from '../../../shared/api';
import { IntelligenceMapper } from './intelligence.mapper';
import type { IntelligenceData } from '../models/intelligence';

export const IntelligenceRepository = {
  async getIntelligence(): Promise<IntelligenceData> {
    const { data } = await apiClient.get(endpoints.intelligence.globalSummary);
    return IntelligenceMapper.toIntelligenceData(data.data);
  }
};

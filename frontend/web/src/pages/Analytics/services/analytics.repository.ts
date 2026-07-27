import { apiClient, endpoints } from '../../../shared/api';
import { AnalyticsMapper } from './analytics.mapper';
import type { AnalyticsData } from '../models/analytics';

export const AnalyticsRepository = {
  async getAnalytics(): Promise<AnalyticsData> {
    const { data } = await apiClient.get(endpoints.analytics.dashboard);
    return AnalyticsMapper.toAnalyticsData(data.data);
  }
};

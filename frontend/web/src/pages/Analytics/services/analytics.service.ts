import { AnalyticsMapper } from "./analytics.mapper";
import { MOCK_ANALYTICS_DTO } from "./analytics.mock";
import type { AnalyticsData } from "../models/analytics";

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const analyticsService = {
  async getAnalytics(): Promise<AnalyticsData> {
    await delay(800);
    return AnalyticsMapper.toAnalyticsData(MOCK_ANALYTICS_DTO);
  }
};

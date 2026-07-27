import type { AnalyticsData } from "../models/analytics";

export const AnalyticsMapper = {
  toAnalyticsData(dto: any): AnalyticsData {
    return {
      investigationsTrend: dto.trends.map((t: any) => ({
        date: t.d,
        count: t.c,
        risk: t.r
      })),
      marketplaceDistribution: dto.marketplaces.map((m: any) => ({
        name: m.n,
        value: m.v
      })),
      agentUtilization: dto.agents.map((a: any) => ({
        name: a.n,
        value: a.v
      })),
      topBrands: dto.brands.map((b: any) => ({
        name: b.n,
        value: b.v
      }))
    };
  }
};

import { describe, it, expect } from "vitest";
import { AnalyticsMapper } from "../services/analytics.mapper";
import { MOCK_ANALYTICS_DTO } from "../services/analytics.mock";

describe("Analytics Mapper", () => {
  it("maps analytics DTO correctly", () => {
    const result = AnalyticsMapper.toAnalyticsData(MOCK_ANALYTICS_DTO);
    expect(result.investigationsTrend).toHaveLength(7);
    expect(result.investigationsTrend[0].date).toBe("2026-07-20");

    expect(result.marketplaceDistribution).toHaveLength(5);
    expect(result.marketplaceDistribution[0].name).toBe("Amazon");

    expect(result.agentUtilization).toHaveLength(4);
    expect(result.topBrands).toHaveLength(4);
  });
});

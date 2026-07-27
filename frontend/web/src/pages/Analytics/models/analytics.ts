export interface TimeSeriesData {
  date: string;
  count: number;
  risk: number;
}

export interface DistributionData {
  name: string;
  value: number;
}

export interface AnalyticsData {
  investigationsTrend: TimeSeriesData[];
  marketplaceDistribution: DistributionData[];
  agentUtilization: DistributionData[];
  topBrands: DistributionData[];
}

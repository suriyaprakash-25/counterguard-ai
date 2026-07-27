import { apiClient, endpoints } from '../shared/api';
import type {
  DashboardSummary,
  InvestigationSummary,
  AlertSummary,
  MarketplaceMetrics,
  RiskTrendPoint,
  SystemHealth,
  FraudNodePreview
} from '../types/dashboard';

export const DashboardRepository = {
  async getSummary(): Promise<DashboardSummary> {
    const { data } = await apiClient.get(endpoints.dashboard.metrics);
    return data.data; // Assuming ApiResponse<T> where the body is { data: ... }
  },

  async getRecentInvestigations(): Promise<InvestigationSummary[]> {
    const { data } = await apiClient.get(endpoints.investigations.list, { params: { limit: 5 } });
    return data.data.map((inv: any) => ({
      id: inv.id,
      title: inv.title,
      type: inv.type,
      marketplace: inv.marketplace,
      status: inv.status,
      riskLevel: inv.riskLevel,
      agentCount: inv.agentCount,
      lastUpdated: inv.lastUpdated,
    }));
  },

  async getRecentAlerts(): Promise<AlertSummary[]> {
    const { data } = await apiClient.get(endpoints.alerts.list, { params: { limit: 4 } });
    return data.data.map((alert: any) => ({
      id: alert._id || alert.id,
      title: alert.headline || alert.title,
      severity: alert.level || alert.severity,
      timestamp: alert.time || alert.timestamp,
      marketplace: alert.platform || alert.marketplace,
    }));
  },

  async getMarketplaceMetrics(): Promise<MarketplaceMetrics[]> {
    const { data } = await apiClient.get(endpoints.dashboard.marketplaceMetrics);
    return data.data;
  },

  async getRiskTrend(): Promise<RiskTrendPoint[]> {
    const { data } = await apiClient.get(endpoints.dashboard.riskTrend);
    return data.data;
  },

  async getSystemHealth(): Promise<SystemHealth> {
    const { data } = await apiClient.get(endpoints.dashboard.systemHealth);
    return data.data;
  },

  async getFraudNodePreview(): Promise<FraudNodePreview[]> {
    const { data } = await apiClient.get(endpoints.dashboard.fraudNodePreview);
    return data.data;
  }
};

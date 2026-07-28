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
import { resolveInvestigationTitle } from './target_normalization';

export const DashboardRepository = {
  async getSummary(): Promise<DashboardSummary> {
    const { data } = await apiClient.get(endpoints.dashboard.metrics);
    return data.data || {
      activeInvestigations: 0,
      activeAlerts: 0,
      highRiskSellers: 0,
      fraudRingsDetected: 0,
      investigationTrend: 0,
      alertTrend: 0,
      sellerTrend: 0,
      ringTrend: 0
    };
  },

  async getRecentInvestigations(): Promise<InvestigationSummary[]> {
    const { data } = await apiClient.get(endpoints.investigations.list, { params: { page_size: 5 } });
    const rawItems = Array.isArray(data?.data) ? data.data : (data?.data?.items || []);
    return rawItems.map((inv: any) => {
      const displayTitle = resolveInvestigationTitle(inv);
      return {
        id: inv.id,
        name: displayTitle,
        displayTitle,
        originalTarget: inv.original_target || inv.listing_url || '',
        marketplace: inv.marketplace || 'Global Search',
        status: inv.status || 'completed',
        riskScore: inv.riskScore ?? inv.risk_score ?? 0,
        createdAt: inv.createdAt || inv.created_at || new Date().toISOString(),
      };
    });
  },


  async getRecentAlerts(): Promise<AlertSummary[]> {
    const { data } = await apiClient.get(endpoints.alerts.list, { params: { limit: 4 } });
    const rawAlerts = Array.isArray(data?.data) ? data.data : (data?.data?.items || []);
    return rawAlerts.map((alert: any) => ({
      id: alert._id || alert.id,
      title: alert.headline || alert.title || 'Security Alert',
      reason: alert.reason || alert.detail || 'Automated risk detection flag',
      severity: alert.level || alert.severity || 'high',
      timestamp: alert.time || alert.timestamp || new Date().toISOString(),
    }));
  },

  async getMarketplaceMetrics(): Promise<MarketplaceMetrics[]> {
    const { data } = await apiClient.get(endpoints.dashboard.marketplaceMetrics);
    return Array.isArray(data?.data) ? data.data : [];
  },

  async getRiskTrend(): Promise<RiskTrendPoint[]> {
    const { data } = await apiClient.get(endpoints.dashboard.riskTrend);
    return Array.isArray(data?.data) ? data.data : [];
  },

  async getSystemHealth(): Promise<SystemHealth> {
    const { data } = await apiClient.get(endpoints.dashboard.systemHealth);
    return data?.data || {
      fastapi: "healthy",
      langgraph: "healthy",
      sqlite: "healthy",
      neo4j: "healthy",
      chromadb: "healthy",
      graphrag: "healthy",
      automation: "healthy",
    };
  },

  async getFraudNodePreview(): Promise<FraudNodePreview[]> {
    const { data } = await apiClient.get(endpoints.dashboard.fraudNodePreview);
    return Array.isArray(data?.data) ? data.data : [];
  }
};

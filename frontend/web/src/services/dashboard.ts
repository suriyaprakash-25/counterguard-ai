import type {
  DashboardSummary,
  InvestigationSummary,
  AlertSummary,
  MarketplaceMetrics,
  RiskTrendPoint,
  SystemHealth,
  FraudNodePreview
} from "../types/dashboard";

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const dashboardService = {
  async getSummary(): Promise<DashboardSummary> {
    await delay(800);
    return {
      activeInvestigations: 142,
      activeAlerts: 23,
      highRiskSellers: 89,
      fraudRingsDetected: 12,
      investigationTrend: 12.5,
      alertTrend: -5.2,
      sellerTrend: 8.4,
      ringTrend: 2.1,
    };
  },

  async getRecentInvestigations(): Promise<InvestigationSummary[]> {
    await delay(1200);
    return [
      { id: "INV-8932", name: "Suspicious iPhone 15 Pro Batch", marketplace: "Amazon", status: "in_progress", riskScore: 88, createdAt: "2026-07-27T08:15:00Z" },
      { id: "INV-8931", name: "Counterfeit Nike Air Max", marketplace: "eBay", status: "completed", riskScore: 95, createdAt: "2026-07-27T07:30:00Z" },
      { id: "INV-8930", name: "Grey Market Sony Headphones", marketplace: "Flipkart", status: "in_progress", riskScore: 65, createdAt: "2026-07-27T06:45:00Z" },
      { id: "INV-8929", name: "Rolex Daytona Replicas", marketplace: "Alibaba", status: "completed", riskScore: 99, createdAt: "2026-07-26T18:20:00Z" },
      { id: "INV-8928", name: "Fake Samsung Chargers", marketplace: "Temu", status: "in_progress", riskScore: 72, createdAt: "2026-07-26T14:10:00Z" },
    ];
  },

  async getRecentAlerts(): Promise<AlertSummary[]> {
    await delay(1000);
    return [
      { id: "ALT-105", title: "Fraud Ring Expansion", reason: "Shared phone number detected across 5 Amazon sellers", severity: "critical", timestamp: "2026-07-27T08:10:00Z" },
      { id: "ALT-104", title: "High-Risk Seller Returns", reason: "Previously banned seller matched by image EXIF data", severity: "high", timestamp: "2026-07-27T07:45:00Z" },
      { id: "ALT-103", title: "Price Anomaly Detected", reason: "New listing 60% below market average", severity: "medium", timestamp: "2026-07-26T22:30:00Z" },
      { id: "ALT-102", title: "New Marketplace Detected", reason: "Seller began operations on Flipkart", severity: "low", timestamp: "2026-07-26T19:15:00Z" },
    ];
  },

  async getMarketplaceMetrics(): Promise<MarketplaceMetrics[]> {
    await delay(1100);
    return [
      { name: "Amazon", investigations: 450 },
      { name: "eBay", investigations: 320 },
      { name: "Flipkart", investigations: 210 },
      { name: "Alibaba", investigations: 180 },
      { name: "Temu", investigations: 150 },
    ];
  },

  async getRiskTrend(): Promise<RiskTrendPoint[]> {
    await delay(900);
    const trend: RiskTrendPoint[] = [];
    const now = new Date();
    for (let i = 30; i >= 0; i--) {
      const date = new Date(now);
      date.setDate(date.getDate() - i);
      trend.push({
        date: date.toISOString().split('T')[0],
        averageRisk: Math.floor(Math.random() * (90 - 40 + 1) + 40)
      });
    }
    return trend;
  },

  async getSystemHealth(): Promise<SystemHealth> {
    await delay(600);
    return {
      fastapi: "healthy",
      langgraph: "healthy",
      sqlite: "healthy",
      neo4j: "healthy",
      chromadb: "warning",
      graphrag: "healthy",
      automation: "healthy",
    };
  },

  async getFraudNodePreview(): Promise<FraudNodePreview[]> {
    await delay(1400);
    return [
      { id: "n1", type: "seller", label: "GlobalTech Store" },
      { id: "n2", type: "phone", label: "+1 555-0198" },
      { id: "n3", type: "seller", label: "BestDeals LLC" },
      { id: "n4", type: "listing", label: "iPhone 15 Pro Max 256GB" },
      { id: "n5", type: "invoice", label: "INV-99081" },
    ];
  }
};

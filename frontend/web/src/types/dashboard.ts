export interface DashboardSummary {
  activeInvestigations: number;
  activeAlerts: number;
  highRiskSellers: number;
  fraudRingsDetected: number;
  investigationTrend: number;
  alertTrend: number;
  sellerTrend: number;
  ringTrend: number;
}

export interface InvestigationSummary {
  id: string;
  name: string;
  marketplace: string;
  status: "in_progress" | "completed" | "failed";
  riskScore: number;
  createdAt: string;
}

export interface AlertSummary {
  id: string;
  title: string;
  reason: string;
  severity: "critical" | "high" | "medium" | "low";
  timestamp: string;
}

export interface MarketplaceMetrics {
  name: string;
  investigations: number;
}

export interface RiskTrendPoint {
  date: string;
  averageRisk: number;
}

export interface SystemHealth {
  fastapi: "healthy" | "warning" | "offline";
  langgraph: "healthy" | "warning" | "offline";
  sqlite: "healthy" | "warning" | "offline";
  neo4j: "healthy" | "warning" | "offline";
  chromadb: "healthy" | "warning" | "offline";
  graphrag: "healthy" | "warning" | "offline";
  automation: "healthy" | "warning" | "offline";
}

export interface FraudNodePreview {
  id: string;
  type: "seller" | "phone" | "invoice" | "listing";
  label: string;
}

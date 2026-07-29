export interface DashboardSummary {
  totalInvestigations: number;
  completedInvestigations: number;
  runningInvestigations: number;
  failedInvestigations: number;
  activeInvestigations: number;
  activeAlerts: number;
  highRiskSellers: number;
  fraudRingsDetected: number;
  investigationTrend: number;
  alertTrend: number;
  sellerTrend: number;
  ringTrend: number;
  totalTrend: number;
  averageRiskScore: number;
  investigationSuccessRate: number;
  totalEvidenceCollected: number;
  totalAiExecutions: number;
}

export interface InvestigationSummary {
  id: string;
  name: string;
  displayTitle?: string;
  originalTarget?: string;
  product: string;
  marketplace: string;
  seller: string;
  status: "in_progress" | "completed" | "failed";
  riskScore: number;
  confidence: number;
  agentsUsed: number;
  executionTimeMs: number;
  createdAt: string;
  agentActivity?: any[];
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
  highRiskCount: number;
  averageRisk: number;
  counterfeitPercentage: number;
}

export interface SuspiciousSeller {
  rank: number;
  name: string;
  marketplace: string;
  investigationsCount: number;
  averageRisk: number;
  riskLevel: "CRITICAL" | "HIGH" | "MEDIUM";
  trend: "up" | "down" | "stable";
}

export interface SwarmAgentState {
  agent: string;
  title: string;
  status: "completed" | "running" | "waiting" | "failed";
  executionTimeMs: number;
  confidence: number;
  toolsUsed: string[];
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

export interface AlertSummary {
  id: string;
  severity: "critical" | "high" | "medium" | "low";
  title: string;
  marketplace: string;
  timestamp: string;
  sourceInvestigation: string;
  status: "new" | "acknowledged" | "dismissed";
  riskScore: number;
}

export interface AlertDetails extends AlertSummary {
  type: "Counterfeit Detection" | "Grey Market" | "Risk Spike" | "Repeated Asset" | "Memory Match" | "Fraud Ring Expansion" | "Consensus Escalation";
  description: string;
  relatedEntities: Array<{ id: string, type: string, label: string }>;
  recommendedActions: string[];
}

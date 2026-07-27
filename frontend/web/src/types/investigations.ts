export interface InvestigationSummary {
  id: string;
  name: string;
  marketplace: string;
  status: "pending" | "in_progress" | "completed" | "failed";
  riskScore: number;
  investigationType: string;
  plannerPriority: "critical" | "high" | "medium" | "low";
  agentCount: number;
  createdAt: string;
  lastUpdated: string;
}

export interface TimelineEvent {
  id: string;
  timestamp: string;
  title: string;
  description: string;
  iconType: "system" | "agent" | "alert" | "memory";
}

export interface EvidenceItem {
  id: string;
  type: "image" | "text" | "metadata" | "link";
  confidence: number;
  description: string;
  source: string;
}

export interface GraphNodePreview {
  id: string;
  type: "seller" | "listing" | "phone" | "image" | "invoice";
  label: string;
  relationship: string;
}

export interface MemoryContext {
  previousInvestigations: number;
  semanticMatches: number;
  historicalRisk: number;
  knownPatterns: string[];
}

export interface ConsensusDetails {
  agreementScore: number;
  explanation: string;
  agentVotes: {
    agent: string;
    vote: "fraud" | "authentic" | "inconclusive";
    confidence: number;
  }[];
}

export interface AgentActivity {
  id: string;
  agent: string;
  status: "success" | "running" | "failed";
  runtimeMs: number;
  confidence: number | null;
  timestamp: string;
}

export interface InvestigationWorkspaceDetails extends InvestigationSummary {
  finalVerdict: "fraud" | "authentic" | "inconclusive" | "pending";
  verdictConfidence: number;
  aiSummary: string;
  timeline: TimelineEvent[];
  evidence: EvidenceItem[];
  graphPreview: GraphNodePreview[];
  memoryContext: MemoryContext;
  consensus: ConsensusDetails;
  explainability: {
    reasoning: string;
    supportingEvidenceIds: string[];
  };
  recommendations: string[];
  agentActivity: AgentActivity[];
}

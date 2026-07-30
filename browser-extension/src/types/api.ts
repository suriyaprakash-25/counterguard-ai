/**
 * api.ts — FastAPI backend response types for Extension API Client
 */

export interface HealthCheckResponse {
  status: string;
  app: string;
  version: string;
  timestamp: string;
  components?: Record<string, string>;
}

export interface CandidateSearchResponse {
  query: string;
  total_discovered: number;
  candidates: Array<{
    id: string;
    marketplace: string;
    title: string;
    url: string;
    price: number;
    seller: string;
    confidence: number;
  }>;
}

export interface ProviderHealthItem {
  marketplace: string;
  status: "HEALTHY" | "DEGRADED" | "BLOCKED" | "RATE_LIMITED";
  success_rate_pct: number;
  average_latency_ms: number;
}

export interface ProviderHealthResponse {
  providers: ProviderHealthItem[];
}

export interface BrowserAnalysisResponse {
  risk_score: number;
  threat_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE";
  seller_trust: number;
  recommendation: string;
  investigation_id: string;
  evidence_id: string;
  findings: string[];
  analyzed_at: string;
}


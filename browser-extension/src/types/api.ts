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

export interface TrustedAlternativeItem {
  seller_name: string;
  marketplace: string;
  price: number;
  currency: string;
  trust_score: number;
  availability: string;
  is_best_recommendation: boolean;
  url: string;
}

export interface BrowserAnalysisResponse {
  risk_score: number;
  threat_level: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE";
  seller_trust: number;
  recommendation: string;
  investigation_id: string;
  evidence_id: string;
  evidence_count: number;
  fraud_ring?: string;
  historical_matches: number;
  trusted_alternatives: TrustedAlternativeItem[];
  findings: string[];
  analyzed_at: string;
}




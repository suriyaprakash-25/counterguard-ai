export interface InvestigationSummary {
  id: string;
  name: string;
  displayTitle: string;
  originalTarget?: string;
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
  agent?: string;
  severity?: "critical" | "high" | "medium" | "low" | "info";
}

export interface EvidenceItem {
  id: string;
  type: "image" | "text" | "metadata" | "link";
  confidence: number;
  description: string;
  source: string;
  title?: string;
  value?: string;
  agent?: string;
}

export interface GraphNodePreview {
  id: string;
  type: "seller" | "listing" | "phone" | "image" | "invoice" | "product" | "trademark" | "domain" | "pattern";
  label: string;
  relationship: string;
}

export interface MemoryContext {
  previousInvestigations: number;
  semanticMatches: number;
  historicalRisk: number;
  knownPatterns: string[];
  knownSeller?: string;
  topSimilarCase?: string;
}

export interface ConsensusDetails {
  agreementScore: number;
  explanation: string;
  agentVotes: {
    agent: string;
    vote: string;
    riskScore?: number;
    confidence: number;
  }[];
}

export interface CategorizedRecommendation {
  category: "Immediate" | "Manual Review" | "Monitor" | "Ignore";
  priority: "High" | "Medium" | "Low";
  action: string;
  reason: string;
}

export interface AgentActivity {
  id: string;
  agent: string;
  status: "success" | "running" | "failed";
  runtimeMs: number;
  confidence: number | null;
  timestamp: string;
  riskScore?: number;
  toolsUsed?: string[];
}

export interface ScoreBreakdown {
  model_match: number;
  official_source: number;
  seller_trust: number;
  price_match: number;
  metadata_completeness: number;
  total: number;
}

export interface RetrievalProvenance {
  retrieved_url: string;
  retrieved_at: string;
  http_status: number;
  domain: string;
  search_query: string;
  provider: string;
  content_hash: string;
  extraction_confidence: number;
  verification_status: string;
}

export interface SellerVerification {
  status: string;
  verification_reason: string;
  verification_source: string;
  sold_by: string;
  ships_from: string;
}

export interface RecommendedProduct {
  id?: string;
  product_name?: string;
  brand: string;
  model: string;
  store: string;
  store_type?: string;
  official: boolean;
  price: number;
  currency: string;
  availability: string;
  warranty: string;
  image_url?: string;
  image?: string;
  product_url: string;
  url?: string;
  retrieved_at?: string;
  source_provider?: string;
  domain?: string;
  metadata_completeness?: number;
  search_confidence?: number;
  score: number;
  score_breakdown?: ScoreBreakdown;
  provenance?: RetrievalProvenance;
  seller_verification?: SellerVerification;
  verification_badge?: string;
  verification_reason?: string;
  why_recommended?: string;
  evidence_ids?: string[];
}

export interface PriceIntelligence {
  msrp: number;
  lowest_price: number;
  highest_price: number;
  average_price: number;
  savings: number;
  savings_percent: number;
  price_deviation: number;
  best_value_store: string;
  market_confidence: number;
}

export interface RecommendationSummary {
  verified_stores_count: number;
  lowest_price: number;
  lowest_price_store: string;
  official_store: string;
  official_store_price: number;
  average_price: number;
  best_value_store: string;
  market_confidence: number;
}

export interface ProviderHealth {
  name: string;
  status: "Healthy" | "Degraded" | "Unhealthy";
  avg_response_ms: number;
  success_rate: number;
  total_queries: number;
  failed_queries: number;
  last_successful_retrieval: string;
  last_failure?: string;
}

export interface ProductComparisonSide {
  title: string;
  store: string;
  price: number;
  currency: string;
  warranty: string;
  seller_trust: string;
  risk_score: number;
  authenticity: string;
  domain?: string;
}

export interface ProductComparison {
  suspicious_listing: ProductComparisonSide;
  verified_product: ProductComparisonSide;
}

export interface InvestigationWorkspaceDetails extends InvestigationSummary {
  finalVerdict: "authentic" | "low_risk" | "suspicious" | "likely_counterfeit" | "fraud" | "inconclusive" | "pending";
  verdictConfidence: number;
  aiSummary: string;
  timeline: TimelineEvent[];
  evidence: EvidenceItem[];
  graphPreview: GraphNodePreview[];
  memoryContext: MemoryContext | null;
  consensus: ConsensusDetails | null;
  explainability: {
    reasoning: string;
    supportingEvidenceIds: string[];
    sections?: {
      priceAnalysis?: string;
      brandAnalysis?: string;
      sellerAnalysis?: string;
      reviewAnalysis?: string;
      conclusion?: string;
    };
  };
  recommendations: (string | CategorizedRecommendation)[];
  agentActivity: AgentActivity[];
  recommendedProducts?: RecommendedProduct[];
  productComparison?: ProductComparison;
  priceIntelligence?: PriceIntelligence;
  recommendationSummary?: RecommendationSummary;
  evidenceSummary?: any;
  dataConfidenceWarning?: string | null;
}

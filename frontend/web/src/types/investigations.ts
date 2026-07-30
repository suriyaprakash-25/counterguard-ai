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
  agent_name?: string;
  category?: string;
  severity?: "critical" | "high" | "medium" | "low" | "info";
  timestamp?: string;
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
  overallReasoning?: string[];
  supportingEvidence?: EvidenceItem[];
  conflictingEvidence?: EvidenceItem[];
  confidenceTimeline?: ConfidenceStepDTO[];
  reasoningTimeline?: ReasoningStepDTO[];
  evidenceGraph?: EvidenceGraphDTO;
  sharedContext?: {
    observations: { id?: string; source_agent: string; content: string; timestamp?: string }[];
    evidenceCount: number;
    confidenceHistory: ConfidenceStepDTO[];
    agentContributions: { agent: string; status: string; confidence: number; runtimeMs: number; observations: string }[];
  };
}

export type EvidenceCategory =
  | "PRICE"
  | "SELLER"
  | "BRAND"
  | "SPECIFICATION"
  | "METADATA"
  | "REVIEWS"
  | "VISUAL"
  | "MEMORY"
  | "GRAPH"
  | "NETWORK"
  | "PROVENANCE"
  | "MARKETPLACE"
  | "GENERAL";

export interface ConfidenceStepDTO {
  previous_confidence: number;
  current_confidence: number;
  reason: string;
  agent: string;
  timestamp: string;
  agent_name?: string;
  confidence?: number;
  reasoning?: string;
}

export interface ReasoningStepDTO {
  sequence_number: number;
  originating_evidence_ids: string[];
  confidence_impact: number;
  explanation: string;
  agent_name: string;
}

export interface EvidenceNodeData {
  id: string;
  label: string;
  category: EvidenceCategory | string;
  severity: "critical" | "high" | "medium" | "low" | "info";
  confidence: number;
  agent: string;
  description: string;
  timestamp: string;
}

export interface EvidenceEdgeData {
  id: string;
  source: string;
  target: string;
  relationship: "derived_from" | "supports" | "conflicts_with";
}

export interface EvidenceGraphDTO {
  nodes: { data: EvidenceNodeData }[];
  edges: { data: EvidenceEdgeData }[];
}

export interface InvestigationFlowStageDTO {
  id: string;
  name: string;
  agentName: string;
  status: "completed" | "in_progress" | "pending" | "failed";
  runtimeMs: number;
  evidenceCount: number;
  confidenceContribution: number;
}

export interface BrandIntelligenceResultDTO {
  official_brand_verified: boolean;
  manufacturer_verified: boolean;
  product_family: string;
  catalog_match_confidence: number;
  suspicious_branding_detected: boolean;
  evidence: EvidenceItem[];
}

export interface SpecificationValidationResultDTO {
  missing_specifications: string[];
  impossible_specifications: string[];
  inconsistent_specifications: string[];
  specs_validated: Record<string, any>;
  evidence: EvidenceItem[];
}

export interface AuthorizedSellerResultDTO {
  seller_status: "official_seller" | "marketplace_fulfilled" | "verified_seller" | "trusted_reseller" | "unknown_seller";
  authorization_confidence: number;
  seller_risk_delta: number;
  evidence: EvidenceItem[];
}

export interface MetadataIntelligenceResultDTO {
  title_analysis: Record<string, any>;
  description_analysis: Record<string, any>;
  duplicate_wording_detected: boolean;
  grammar_error_count: number;
  spam_score: number;
  keyword_stuffing_detected: boolean;
  evidence: EvidenceItem[];
}

export interface InvestigationContextDTO {
  investigation_id: string;
  product_info: Record<string, any>;
  marketplace: string;
  seller_info: Record<string, any>;
  extracted_metadata: Record<string, any>;
  shared_evidence: EvidenceItem[];
  shared_observations: { id?: string; source_agent: string; content: string; timestamp?: string }[];
  confidence_timeline: ConfidenceStepDTO[];
  reasoning_timeline?: ReasoningStepDTO[];
  intermediate_risk: number;
  final_verdict?: string;
}

export interface UnifiedVerdictDTO {
  final_verdict: string;
  risk_score: number;
  risk_level: string;
  confidence: number;
  confidence_percentage: number;
  summary: string;
  reasoning: string;
  canonical_product_name: string;
  marketplace: string;
  seller: string;
  price: number;
  recommended_actions: CategorizedRecommendation[];
  comparison_matrix: ProductComparison;
  evidence_findings: string[];
  data_confidence_warning?: string | null;
  overall_confidence: number;
  overall_reasoning: string[];
  supporting_evidence: EvidenceItem[];
  conflicting_evidence: EvidenceItem[];
  confidence_timeline?: ConfidenceStepDTO[];
  reasoning_timeline?: ReasoningStepDTO[];
  evidence_graph?: EvidenceGraphDTO;
}

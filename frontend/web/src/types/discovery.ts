// TypeScript interfaces for Sprint 2.1 + 2.2 — Product Search & Discovery Layer

export interface ListingCandidate {
  id: string;
  marketplace: string;
  title: string;
  url: string;
  price: number;
  seller: string;
  thumbnail?: string | null;
  currency: string;
  availability: string;
  discovery_source: string;
  confidence: number;

  // ── Multi-Stage Discovery Confidence & Provenance (Refinements 3 & 4) ────────
  search_confidence?: number;
  matching_confidence?: number;
  discovery_confidence?: number;
  investigation_confidence?: number | null;
  discovered_via?: string;
  provenance_chain?: string[];

  metadata?: Record<string, unknown>;
}

export interface DiscoverySearchRequest {
  query: string;
  marketplaces?: string[] | null;
  limit_per_marketplace?: number;
  use_memory_cache?: boolean;
}

// ── Marketplace Health Score Interface ────────────────────────────────────────

export interface MarketplaceHealthInfo {
  marketplace: string;
  health_score: number;
  status: string;
  latency_ms: number;
  captcha_rate: number;
  data_quality_score: number;
}

// ── Sprint 2.2: Deduplication & Ranking types ─────────────────────────────

export interface PriorityScore {
  total_priority_score: number;        // 0–100
  price_anomaly_score: number;         // 0–1
  seller_trust_score: number;          // 0–1 (higher = less trusted)
  marketplace_risk_score: number;      // 0–1
  listing_completeness_score: number;  // 0–1 (higher = more incomplete)
  metadata_quality_score: number;      // 0–1 (higher = lower quality)
  reasoning: string[];
}

export type InvestigationPriority = 'critical' | 'high' | 'normal' | 'low';

export interface ListingGroup {
  group_id: string;
  canonical_title: string;
  normalized_product_name: string;
  listings: ListingCandidate[];
  representative?: ListingCandidate | null;
  unique_marketplaces: string[];
  unique_sellers: string[];
  price_range: { min?: number; max?: number; avg?: number };
  similarity_basis: string;
  listing_count: number;
  priority_score?: PriorityScore | null;
  investigation_priority: InvestigationPriority;
  created_at: string;
}

export interface DiscoverySearchResponse {
  query: string;
  normalized_query: string;
  marketplaces_searched: string[];
  // Sprint 2.1 — flat candidates list (preserved for backward compat)
  candidates: ListingCandidate[];
  // Sprint 2.2 — deduplicated + ranked groups
  listing_groups: ListingGroup[];
  top_investigation_targets: ListingCandidate[];
  metadata: {
    candidate_count: number;
    group_count?: number;
    top_target_count?: number;
    duration_ms: number;
    timestamp: string;
    search_engine_version: string;
    deduplication_reduction?: number;
    marketplace_health_scores?: Record<string, MarketplaceHealthInfo>;
    from_memory?: boolean;
    cached_at?: string;
  };
}

export interface SupportedMarketplacesResponse {
  supported_marketplaces: string[];
  count: number;
}

// ── Helper functions ──────────────────────────────────────────────────────────

export type ConfidenceTier = 'high' | 'medium' | 'low';

export function getConfidenceTier(confidence: number): ConfidenceTier {
  if (confidence >= 0.85) return 'high';
  if (confidence >= 0.65) return 'medium';
  return 'low';
}

export function formatConfidence(confidence: number): string {
  return `${Math.round(confidence * 100)}%`;
}

export function getPriorityColor(priority: InvestigationPriority): {
  bg: string; text: string; border: string;
} {
  switch (priority) {
    case 'critical': return { bg: 'bg-red-500/20', text: 'text-red-300', border: 'border-red-500/40' };
    case 'high':     return { bg: 'bg-orange-500/20', text: 'text-orange-300', border: 'border-orange-500/40' };
    case 'normal':   return { bg: 'bg-blue-500/20', text: 'text-blue-300', border: 'border-blue-500/40' };
    case 'low':      return { bg: 'bg-slate-500/20', text: 'text-slate-400', border: 'border-slate-600/40' };
  }
}

export function formatPriorityScore(score: number): string {
  return `${Math.round(score)}/100`;
}

// ── Sprint 2.3: Parallel Investigation Launcher types ─────────────────────────

export interface CandidateLaunchItem {
  candidate_id: string;
  marketplace: string;
  title: string;
  url: string;
  price?: number;
  seller?: string;
  currency?: string;
}

export interface ParallelLaunchRequest {
  candidates: CandidateLaunchItem[];
  investigation_type?: string;
  planner_strategy?: string;
  objectives?: string[];
  priority?: 'low' | 'medium' | 'high' | 'critical';
  notes?: string | null;
  advanced_options?: Record<string, unknown> | null;
}

export type JobStatus = 'pending' | 'in_progress' | 'completed' | 'failed' | 'unknown';

export interface LaunchJobStatus {
  candidate_id: string;
  investigation_id: string;
  marketplace: string;
  title: string;
  url: string;
  status: JobStatus;
  launched_at: string;
}

export interface ParallelLaunchResponse {
  batch_id: string;
  total_launched: number;
  jobs: LaunchJobStatus[];
  investigation_ids: string[];
  summary: string;
  metadata: {
    batch_id: string;
    launched_at: string;
    investigation_type: string;
    planner_strategy: string;
    candidate_count: number;
    marketplace_count: number;
  };
}

export interface BatchStatusResponse {
  batch_id: string;
  total: number;
  completed: number;
  in_progress: number;
  pending: number;
  failed: number;
  progress_pct: number;
  jobs: LaunchJobStatus[];
  is_complete: boolean;
}

// Convert a ListingCandidate to a CandidateLaunchItem
export function candidateToLaunchItem(c: ListingCandidate): CandidateLaunchItem {
  return {
    candidate_id: c.id,
    marketplace: c.marketplace,
    title: c.title,
    url: c.url,
    price: c.price,
    seller: c.seller,
    currency: c.currency,
  };
}

// ── Sprint 2.5: Product Intelligence Report types ─────────────────────────────

export interface ListingReportItem {
  investigation_id: string;
  marketplace: string;
  listing_url: string;
  title: string;
  seller: string;
  price: number;
  risk_score: number;
  verdict: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  evidence_count: number;
  top_risk_factor?: string | null;
  last_updated: string;
}

export interface ProductIntelligenceReportRequest {
  investigation_ids: string[];
  product_name?: string;
}

export interface ProductIntelligenceReport {
  report_id: string;
  product_name: string;
  generated_at: string;
  total_listings: number;
  safe_listings: number;
  suspicious_listings: number;
  overall_product_risk: number;
  overall_risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  highest_risk_marketplace: string;
  recommended_seller?: string | null;
  marketplace_distribution: Record<string, number>;
  evidence_summary: string[];
  coordinator_summary: string;
  investigations: ListingReportItem[];
  recommendations: string[];
  metadata?: Record<string, unknown>;
}

// Fake Backend DTOs
export interface IntelligenceSummaryDTO {
  total_sellers: number;
  total_rings: number;
  total_listings: number;
  total_assets: number;
  total_investigations: number;
  total_episodes: number;
  nodes: number;
  relationships: number;
}

export const MOCK_SUMMARY_DTO: IntelligenceSummaryDTO = {
  total_sellers: 12450,
  total_rings: 84,
  total_listings: 45210,
  total_assets: 8900,
  total_investigations: 1420,
  total_episodes: 5600,
  nodes: 125000,
  relationships: 450000
};

export const MOCK_SELLERS_DTO = [
  { id: "S-1", seller_name: "GlobalTech Store", platform: "Amazon", risk: 92, inv_count: 5, rings: ["R-12"], state: "banned" },
  { id: "S-2", seller_name: "BestDeals LLC", platform: "eBay", risk: 85, inv_count: 3, rings: ["R-12"], state: "active" },
  { id: "S-3", seller_name: "SuperChargers", platform: "Temu", risk: 78, inv_count: 2, rings: [], state: "monitoring" },
];

export const MOCK_RINGS_DTO = [
  { id: "R-12", ring_name: "Shenzhen Electronics Ring", member_count: 45, avg_risk: 88, listings: 1200, sellers: 45, last_seen: "2026-07-27T08:00:00Z" },
  { id: "R-15", ring_name: "EU Luxury Replicas", member_count: 12, avg_risk: 95, listings: 300, sellers: 12, last_seen: "2026-07-26T14:00:00Z" },
];

export const MOCK_PATTERNS_DTO = [
  { id: "P-1", pattern_type: "image", name: "Recycled AirPods Box", count: 450, desc: "Same packaging image used across 45 sellers." },
  { id: "P-2", pattern_type: "pricing", name: "60% Below MSRP", count: 120, desc: "Electronics listed exactly 60% below retail value." },
  { id: "P-3", pattern_type: "description", name: "Generic SEO Spam", count: 890, desc: "Copy-pasted product description with excessive keyword stuffing." },
];

export const MOCK_IMAGE_CLUSTERS_DTO = [
  { id: "IMG-1", url: "https://example.com/mock-airpods.jpg", count: 45, sellers: 12, listings: 45, similarity: 0.98, evidence: 120 },
  { id: "IMG-2", url: "https://example.com/mock-rolex.jpg", count: 23, sellers: 5, listings: 23, similarity: 0.95, evidence: 65 },
];

export const MOCK_PHONE_CLUSTERS_DTO = [
  { id: "PH-1", phone: "+1 555-0198", count: 89, sellers: 15, risk: 99 },
  { id: "PH-2", phone: "+44 7700 900077", count: 45, sellers: 8, risk: 85 },
];

export const MOCK_INVOICE_CLUSTERS_DTO = [
  { id: "INV-1", doc_id: "INV-99081", count: 12, sellers: 4, platform: "Amazon", risk: 95 },
  { id: "INV-2", doc_id: "PO-44512", count: 8, sellers: 3, platform: "eBay", risk: 88 },
];

export const MOCK_MEMORY_INSIGHTS_DTO = [
  { id: "M-1", title: "Resurgence of iPhone 15 Fake Packaging", desc: "Similar packaging detected in 5 new investigations.", conf: 92, type: "similar_investigation", ctx: "Matches pattern from Q3 2025." },
  { id: "M-2", title: "New VOIP Provider Detected", desc: "Multiple banned sellers migrating to new VOIP block.", conf: 85, type: "new_pattern", ctx: "Prefix +1-988 highly correlated with fraud." },
];

export const MOCK_GRAPH_STATS_DTO = {
  n_count: 125000,
  r_count: 450000,
  comm_count: 450,
  max_ring: 120,
  avg_conn: 3.6,
  density: 0.00015
};

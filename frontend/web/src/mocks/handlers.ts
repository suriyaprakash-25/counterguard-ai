import { http, HttpResponse } from 'msw';
import { endpoints } from '../shared/api/endpoints';

// Import all existing mock data
import { MOCK_ALERTS_DTO } from '../pages/Alerts/services/alerts.mock';
import { MOCK_ANALYTICS_DTO } from '../pages/Analytics/services/analytics.mock';
import { MOCK_GRAPH_DTO, MOCK_GRAPH_STATS_DTO } from '../pages/GraphExplorer/services/graph.mock';
import { MOCK_SUMMARY_DTO } from '../pages/Intelligence/services/intelligence.mock';
import { MOCK_SETTINGS_DTO } from '../pages/Settings/services/settings.mock';
import { MOCK_INVESTIGATIONS, MOCK_WORKSPACE_DETAILS } from '../services/investigations.mock';

const buildUrl = (path: string) => `*${path}`;

const MOCK_USER = {
  id: 'usr_123',
  email: 'investigator@counterguard.ai',
  firstName: 'Jane',
  lastName: 'Doe',
  role: 'Administrator',
  organization: 'Cyber Fraud Unit'
};

const MOCK_MARKETPLACE_METRICS = [
  { name: 'Amazon', activeInvestigations: 45, alerts: 12, riskScore: 85, trend: 5 },
  { name: 'eBay', activeInvestigations: 30, alerts: 8, riskScore: 72, trend: -2 },
  { name: 'Walmart', activeInvestigations: 22, alerts: 5, riskScore: 60, trend: 1 }
];

const MOCK_RISK_TREND = [
  { date: '2026-07-20', riskScore: 45 },
  { date: '2026-07-21', riskScore: 52 },
  { date: '2026-07-22', riskScore: 48 },
  { date: '2026-07-23', riskScore: 61 },
  { date: '2026-07-24', riskScore: 59 },
  { date: '2026-07-25', riskScore: 75 },
  { date: '2026-07-26', riskScore: 82 }
];

const MOCK_SYSTEM_HEALTH = {
  fastapi: 'healthy',
  langgraph: 'healthy',
  sqlite: 'healthy',
  neo4j: 'healthy',
  chromadb: 'warning',
  graphrag: 'healthy',
  automation: 'healthy'
};

const MOCK_FRAUD_NODE_PREVIEW = [
  { id: 'N1', type: 'Seller', label: 'TechBros', risk: 'critical' },
  { id: 'N2', type: 'Phone', label: '+1 555-0192', risk: 'high' },
  { id: 'N3', type: 'Address', label: '123 Fake St', risk: 'medium' }
];

export const handlers = [
  // Auth
  http.post(buildUrl(endpoints.auth.login), () => {
    return HttpResponse.json({
      data: {
        user: MOCK_USER,
        accessToken: 'mock_access_token',
        refreshToken: 'mock_refresh_token'
      }
    });
  }),

  http.post(buildUrl(endpoints.auth.logout), () => {
    return HttpResponse.json({ data: { success: true } });
  }),

  http.post(buildUrl(endpoints.auth.refresh), () => {
    return HttpResponse.json({
      data: {
        user: MOCK_USER,
        accessToken: 'new_mock_access_token',
        refreshToken: 'new_mock_refresh_token'
      }
    });
  }),

  http.get(buildUrl(endpoints.auth.me), ({ request }) => {
    const authHeader = request.headers.get('Authorization');
    if (!authHeader) {
      return new HttpResponse(null, { status: 401 });
    }
    return HttpResponse.json({ data: MOCK_USER });
  }),

  // Dashboard
  http.get(buildUrl(endpoints.dashboard.metrics), () => {
    return HttpResponse.json({
      data: {
        activeInvestigations: 18,
        activeAlerts: 3,
        highRiskSellers: 12,
        fraudRingsDetected: 4,
        investigationTrend: 12,
        alertTrend: -8,
        sellerTrend: 15,
        ringTrend: 2
      }
    });
  }),
  http.get(buildUrl(endpoints.dashboard.marketplaceMetrics), () => {
    return HttpResponse.json({ data: MOCK_MARKETPLACE_METRICS });
  }),
  http.get(buildUrl(endpoints.dashboard.riskTrend), () => {
    return HttpResponse.json({ data: MOCK_RISK_TREND });
  }),
  http.get(buildUrl(endpoints.dashboard.systemHealth), () => {
    return HttpResponse.json({ data: MOCK_SYSTEM_HEALTH });
  }),
  http.get(buildUrl(endpoints.dashboard.fraudNodePreview), () => {
    return HttpResponse.json({ data: MOCK_FRAUD_NODE_PREVIEW });
  }),

  // Investigations
  http.get('*/api/v1/investigations', () => {
    return HttpResponse.json({ data: MOCK_INVESTIGATIONS });
  }),
  http.post('*/api/v1/investigations', async ({ request }) => {
    const body: any = await request.json();
    return HttpResponse.json({
      data: {
        id: `INV-${Date.now()}`,
        status: 'in_progress',
        name: body.investigation_name || 'New Investigation',
        createdAt: new Date().toISOString()
      }
    });
  }),
  http.get('*/api/v1/investigations/:id', ({ params }) => {
    const id = params.id as string;
    return HttpResponse.json({
      data: {
        ...MOCK_WORKSPACE_DETAILS,
        id: id || MOCK_WORKSPACE_DETAILS.id,
        investigation: {
          ...MOCK_WORKSPACE_DETAILS.investigation,
          id: id || MOCK_WORKSPACE_DETAILS.investigation.id,
        }
      }
    });
  }),
  http.delete('*/api/v1/investigations/:id', () => {
    return HttpResponse.json({ data: { success: true } });
  }),

  // Alerts
  http.get(buildUrl(endpoints.alerts.list), () => {
    return HttpResponse.json({ data: MOCK_ALERTS_DTO });
  }),
  http.get(buildUrl(endpoints.alerts.details(':id')), ({ params }) => {
    const alert = MOCK_ALERTS_DTO.items.find(a => a._id === params.id) || MOCK_ALERTS_DTO.items[0];
    return HttpResponse.json({ data: alert });
  }),

  // Analytics
  http.get(buildUrl(endpoints.analytics.dashboard), () => {
    return HttpResponse.json({ data: MOCK_ANALYTICS_DTO });
  }),

  // Settings
  http.get(buildUrl(endpoints.settings.config), () => {
    return HttpResponse.json({ data: MOCK_SETTINGS_DTO });
  }),

  // Graph
  http.get(buildUrl(endpoints.graph.data), () => {
    return HttpResponse.json({ data: MOCK_GRAPH_DTO });
  }),
  http.get(buildUrl(endpoints.graph.stats), () => {
    return HttpResponse.json({ data: MOCK_GRAPH_STATS_DTO });
  }),

  // Intelligence
  http.get(buildUrl(endpoints.intelligence.globalSummary), () => {
    return HttpResponse.json({ data: MOCK_SUMMARY_DTO });
  }),

  // Product Discovery
  http.get(buildUrl(endpoints.discovery.marketplaces), () => {
    return HttpResponse.json({
      supported_marketplaces: ['Amazon', 'Flipkart', 'Meesho', 'TradeIndia', 'AJIO', 'Myntra'],
      count: 6,
    });
  }),

  http.post(buildUrl(endpoints.discovery.search), async ({ request }) => {
    const body = await request.json() as { query: string };
    return HttpResponse.json({
      query: body.query,
      normalized_query: body.query,
      marketplaces_searched: ['Amazon', 'Flipkart', 'Meesho', 'TradeIndia', 'AJIO', 'Myntra'],
      candidates: [
        {
          id: 'cand-test001',
          marketplace: 'Amazon',
          title: `${body.query} (Official Brand Listing)`,
          url: `https://www.amazon.com/s?k=${body.query}`,
          price: 2999,
          seller: 'Amazon Official',
          thumbnail: null,
          currency: 'INR',
          availability: 'In Stock',
          discovery_source: 'Amazon Search Index',
          confidence: 0.95,
        },
        {
          id: 'cand-test002',
          marketplace: 'Meesho',
          title: `${body.query} Replica Master Copy`,
          url: `https://www.meesho.com/search?q=${body.query}`,
          price: 299,
          seller: 'Fashion Hub Wholesale Surat',
          thumbnail: null,
          currency: 'INR',
          availability: 'In Stock',
          discovery_source: 'Meesho Seller Feed',
          confidence: 0.55,
        },
      ],
      listing_groups: [
        {
          group_id: 'grp-mock001',
          canonical_title: `${body.query} (Official Brand Listing)`,
          normalized_product_name: body.query,
          listings: [
            {
              id: 'cand-test001',
              marketplace: 'Amazon',
              title: `${body.query} (Official Brand Listing)`,
              url: `https://www.amazon.com/s?k=${body.query}`,
              price: 2999,
              seller: 'Amazon Official',
              thumbnail: null,
              currency: 'INR',
              availability: 'In Stock',
              discovery_source: 'Amazon Search Index',
              confidence: 0.95,
            },
            {
              id: 'cand-test002',
              marketplace: 'Meesho',
              title: `${body.query} Replica Master Copy`,
              url: `https://www.meesho.com/search?q=${body.query}`,
              price: 299,
              seller: 'Fashion Hub Wholesale Surat',
              thumbnail: null,
              currency: 'INR',
              availability: 'In Stock',
              discovery_source: 'Meesho Seller Feed',
              confidence: 0.55,
            },
          ],
          representative: {
            id: 'cand-test002',
            marketplace: 'Meesho',
            title: `${body.query} Replica Master Copy`,
            url: `https://www.meesho.com/search?q=${body.query}`,
            price: 299,
            seller: 'Fashion Hub Wholesale Surat',
            thumbnail: null,
            currency: 'INR',
            availability: 'In Stock',
            discovery_source: 'Meesho Seller Feed',
            confidence: 0.55,
          },
          unique_marketplaces: ['Amazon', 'Meesho'],
          unique_sellers: ['Amazon Official', 'Fashion Hub Wholesale Surat'],
          price_range: { min: 299, max: 2999, avg: 1649 },
          similarity_basis: 'title',
          listing_count: 2,
          priority_score: {
            total_priority_score: 68.5,
            price_anomaly_score: 0.88,
            seller_trust_score: 0.95,
            marketplace_risk_score: 0.45,
            listing_completeness_score: 0.55,
            metadata_quality_score: 0.60,
            reasoning: [
              'Price anomaly: ₹299 is >60% below group average ₹1,649',
              "High-risk seller: 'Fashion Hub Wholesale Surat' contains suspicious keywords",
              'High-risk marketplace: Meesho has elevated counterfeit prevalence',
            ],
          },
          investigation_priority: 'high',
          created_at: new Date().toISOString(),
        },
      ],
      top_investigation_targets: [
        {
          id: 'cand-test002',
          marketplace: 'Meesho',
          title: `${body.query} Replica Master Copy`,
          url: `https://www.meesho.com/search?q=${body.query}`,
          price: 299,
          seller: 'Fashion Hub Wholesale Surat',
          thumbnail: null,
          currency: 'INR',
          availability: 'In Stock',
          discovery_source: 'Meesho Seller Feed',
          confidence: 0.55,
        },
      ],
      metadata: {
        candidate_count: 2,
        group_count: 1,
        top_target_count: 1,
        duration_ms: 120,
        timestamp: new Date().toISOString(),
        search_engine_version: 'CounterGuard-Discovery-v2.2',
        deduplication_reduction: 1,
      },
    });
  }),

  // ── Sprint 2.3: Parallel Investigation Launcher ────────────────────────────

  // POST /api/v1/discovery/launch — accepts candidates and returns batch receipt
  http.post(buildUrl(endpoints.discovery.launch), async ({ request }) => {
    const body = await request.json() as { candidates: Array<{ candidate_id: string; marketplace: string; title: string; url: string }> };
    const candidates = body.candidates ?? [];
    const batchId = `batch-mock-${Date.now().toString(36)}`;
    const launchedAt = new Date().toISOString();

    const mockInvestigationIds = candidates.map(() =>
      `${crypto.randomUUID()}`
    );

    const jobs = candidates.map((c, i) => ({
      candidate_id: c.candidate_id,
      investigation_id: mockInvestigationIds[i],
      marketplace: c.marketplace,
      title: c.title,
      url: c.url,
      status: 'pending',
      launched_at: launchedAt,
    }));

    return HttpResponse.json({
      batch_id: batchId,
      total_launched: candidates.length,
      jobs,
      investigation_ids: mockInvestigationIds,
      summary: `Launched ${candidates.length} concurrent investigation(s). Batch ID: ${batchId}`,
      metadata: {
        batch_id: batchId,
        launched_at: launchedAt,
        investigation_type: 'Counterfeit Detection',
        planner_strategy: 'Balanced Investigation',
        candidate_count: candidates.length,
        marketplace_count: new Set(candidates.map((c) => c.marketplace)).size,
      },
    }, { status: 202 });
  }),

  // GET /api/v1/discovery/launch/:batch_id/status — returns mock batch status
  http.get(buildUrl('/api/v1/discovery/launch/:batchId/status'), ({ params }) => {
    const { batchId } = params;
    return HttpResponse.json({
      batch_id: batchId,
      total: 2,
      completed: 1,
      in_progress: 1,
      pending: 0,
      failed: 0,
      progress_pct: 50.0,
      jobs: [
        {
          candidate_id: 'cand-test001',
          investigation_id: `mock-inv-001`,
          marketplace: 'Amazon',
          title: 'Mock Product (Official Brand Listing)',
          url: 'https://www.amazon.com/mock',
          status: 'completed',
          launched_at: new Date().toISOString(),
        },
        {
          candidate_id: 'cand-test002',
          investigation_id: `mock-inv-002`,
          marketplace: 'Meesho',
          title: 'Mock Product Replica Master Copy',
          url: 'https://www.meesho.com/mock',
          status: 'in_progress',
          launched_at: new Date().toISOString(),
        },
      ],
      is_complete: false,
    });
  }),

  // ── Sprint 2.5: Product Intelligence Report ────────────────────────────

  http.post(buildUrl(endpoints.discovery.report), async ({ request }) => {
    const body = await request.json() as { investigation_ids: string[]; product_name?: string };
    const ids = body.investigation_ids ?? [];
    return HttpResponse.json({
      report_id: `rpt-mock-${Date.now()}`,
      product_name: body.product_name || 'CMF Buds 2a',
      generated_at: new Date().toISOString(),
      total_listings: ids.length || 2,
      safe_listings: 1,
      suspicious_listings: Math.max(1, ids.length - 1),
      overall_product_risk: 62.5,
      overall_risk_level: 'HIGH',
      highest_risk_marketplace: 'Meesho',
      recommended_seller: 'Official Nothing Store',
      marketplace_distribution: { Amazon: 1, Meesho: 1, Flipkart: 1 },
      evidence_summary: [
        'Seller created recently on Meesho (< 30 days old).',
        '87% below MSRP price anomaly detected.',
        'Missing official manufacturer warranty documentation.',
      ],
      coordinator_summary: 'Cross-marketplace audit detected severe price anomalies and unverified seller accounts on Meesho and Flipkart. Amazon listing was confirmed authentic.',
      investigations: ids.map((id, index) => ({
        investigation_id: id,
        marketplace: index % 2 === 0 ? 'Amazon' : 'Meesho',
        listing_url: `https://marketplace.example.com/item/${id}`,
        title: `Discovered Product Item ${index + 1}`,
        seller: index % 2 === 0 ? 'Official Nothing Store' : 'Surat Replica Hub',
        price: index % 2 === 0 ? 2999 : 399,
        risk_score: index % 2 === 0 ? 15.0 : 88.0,
        verdict: index % 2 === 0 ? 'LOW' : 'CRITICAL',
        confidence: 0.88,
        evidence_count: 5,
        top_risk_factor: index % 2 === 0 ? null : '87% price drop below MSRP',
        last_updated: new Date().toISOString(),
      })),
      recommendations: [
        'Issue immediate legal cease and desist notice to Surat Replica Hub.',
        'Monitor Meesho for recurring duplicate listing assets.',
      ],
    });
  }),
];

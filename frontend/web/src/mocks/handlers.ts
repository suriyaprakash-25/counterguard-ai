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

  // Dashboard (Mocks removed - now hitting real backend)
  // http.get(buildUrl(endpoints.dashboard.metrics), ...),
  // http.get(buildUrl(endpoints.dashboard.marketplaceMetrics), ...),
  // http.get(buildUrl(endpoints.dashboard.riskTrend), ...),
  // http.get(buildUrl(endpoints.dashboard.systemHealth), ...),
  // http.get(buildUrl(endpoints.dashboard.fraudNodePreview), ...),

  // Investigations
  // http.get(buildUrl(endpoints.investigations.list), ...),
  // http.post(buildUrl(endpoints.investigations.create), ...),
  // http.get(buildUrl(endpoints.investigations.details(':id')), ...),
  // http.delete(buildUrl(endpoints.investigations.delete(':id')), ...),
  // http.post(buildUrl(endpoints.investigations.cancel(':id')), ...),
  // http.post(buildUrl(endpoints.investigations.retry(':id')), ...),
  // http.get(buildUrl(endpoints.investigations.timeline(':id')), ...),
  // http.get(buildUrl(endpoints.investigations.graph(':id')), ...),
  // http.get(buildUrl(endpoints.investigations.reasoning(':id')), ...),
  // http.get(buildUrl(endpoints.investigations.report(':id')), ...),
  // http.get(buildUrl('/api/v1/investigations/:id/stream'), ...),

  // Alerts
  // http.get(buildUrl(endpoints.alerts.list), ...),
  // http.get(buildUrl(endpoints.alerts.details(':id')), ...),

  // Analytics
  // http.get(buildUrl(endpoints.analytics.dashboard), ...),

  // Settings
  // http.get(buildUrl(endpoints.settings.config), ...),

  // Graph
  // http.get(buildUrl(endpoints.graph.data), ...),
  // http.get(buildUrl(endpoints.graph.stats), ...),

  // Intelligence
  // http.get(buildUrl(endpoints.intelligence.globalSummary), ...),
];

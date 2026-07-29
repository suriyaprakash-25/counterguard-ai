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
  })
];

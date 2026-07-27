export const endpoints = {
  dashboard: {
    metrics: '/api/v1/dashboard/metrics',
    recentActivity: '/api/v1/dashboard/activity',
  },
  investigations: {
    list: '/api/v1/investigations',
    details: (id: string) => `/api/v1/investigations/${id}`,
    timeline: (id: string) => `/api/v1/investigations/${id}/timeline`,
    evidence: (id: string) => `/api/v1/investigations/${id}/evidence`,
    consensus: (id: string) => `/api/v1/investigations/${id}/consensus`,
  },
  alerts: {
    list: '/api/v1/alerts',
    details: (id: string) => `/api/v1/alerts/${id}`,
    acknowledge: (id: string) => `/api/v1/alerts/${id}/acknowledge`,
  },
  analytics: {
    dashboard: '/api/v1/analytics',
  },
  settings: {
    config: '/api/v1/settings',
    update: '/api/v1/settings',
  },
  graph: {
    data: '/api/v1/graph/data',
    stats: '/api/v1/graph/stats',
    nodeDetails: (id: string) => `/api/v1/graph/nodes/${id}`,
  },
  intelligence: {
    globalSummary: '/api/v1/intelligence/summary',
    knownSellers: '/api/v1/intelligence/sellers',
    fraudRings: '/api/v1/intelligence/rings',
    knownPatterns: '/api/v1/intelligence/patterns',
    repeatedImages: '/api/v1/intelligence/images',
    repeatedPhones: '/api/v1/intelligence/phones',
    repeatedInvoices: '/api/v1/intelligence/invoices',
    memoryInsights: '/api/v1/intelligence/memory',
  }
} as const;

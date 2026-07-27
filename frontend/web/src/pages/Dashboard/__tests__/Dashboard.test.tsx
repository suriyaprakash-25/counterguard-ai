import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Dashboard from "../index";
import { dashboardService } from "../../../services/dashboard";

// Mock the Recharts components to prevent SVG layout errors in JSDOM
vi.mock("recharts", async (importOriginal) => {
  const actual = await importOriginal<typeof import("recharts")>();
  return {
    ...actual,
    ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
    LineChart: () => <div data-testid="mock-line-chart" />,
    BarChart: () => <div data-testid="mock-bar-chart" />,
  };
});

vi.mock("../../../services/dashboard", () => ({
  dashboardService: {
    getSummary: vi.fn().mockResolvedValue({
      activeInvestigations: 142,
      activeAlerts: 23,
      highRiskSellers: 89,
      fraudRingsDetected: 12,
    }),
    getRecentInvestigations: vi.fn().mockResolvedValue([
      { id: "INV-8932", name: "Suspicious iPhone 15 Pro Batch", marketplace: "Amazon", status: "in_progress", riskScore: 88, createdAt: "2026-07-27T08:15:00Z" }
    ]),
    getRecentAlerts: vi.fn().mockResolvedValue([]),
    getMarketplaceMetrics: vi.fn().mockResolvedValue([]),
    getRiskTrend: vi.fn().mockResolvedValue([]),
    getSystemHealth: vi.fn().mockResolvedValue({
      fastapi: "healthy", langgraph: "healthy", sqlite: "healthy", neo4j: "healthy", chromadb: "warning", graphrag: "healthy", automation: "healthy"
    }),
    getFraudNodePreview: vi.fn().mockResolvedValue([]),
  }
}));

describe("Dashboard Page", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    });
  });

  const renderDashboard = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <Dashboard />
        </BrowserRouter>
      </QueryClientProvider>
    );

  it("renders the dashboard header", () => {
    renderDashboard();
    expect(screen.getByText("CounterGuard Dashboard")).toBeInTheDocument();
  });

  it("renders the metric cards after loading", async () => {
    renderDashboard();
    // Assuming mock service returns 142 active investigations
    await waitFor(() => {
      expect(screen.getByText("142")).toBeInTheDocument();
    });
    expect(screen.getByText("Active Investigations")).toBeInTheDocument();
    expect(screen.getByText("Active Alerts")).toBeInTheDocument();
  });

  it("renders the investigations list widget", async () => {
    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText("Recent Investigations")).toBeInTheDocument();
      expect(screen.getByText("Suspicious iPhone 15 Pro Batch")).toBeInTheDocument();
    });
  });

  it("handles empty state in investigations", async () => {
    vi.spyOn(dashboardService, "getRecentInvestigations").mockResolvedValueOnce([]);
    renderDashboard();
    await waitFor(() => {
      expect(screen.getByText("No Investigations Found")).toBeInTheDocument();
    });
  });
});

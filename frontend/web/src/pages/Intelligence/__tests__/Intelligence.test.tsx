import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, beforeEach, vi } from "vitest";
import IntelligenceCenter from "../index";

vi.mock("../services/intelligence.service", () => ({
  intelligenceService: {
    getSummary: vi.fn().mockResolvedValue({
      knownSellers: 10, knownFraudRings: 2, knownCounterfeitListings: 100,
      repeatedAssets: 5, historicalInvestigations: 20, memoryEpisodes: 50,
      graphNodes: 200, graphRelationships: 500
    }),
    getKnownSellers: vi.fn().mockResolvedValue([
      { id: "S-1", name: "GlobalTech Store", marketplace: "Amazon", riskScore: 92, historicalInvestigations: 5, status: "banned" }
    ]),
    getFraudRings: vi.fn().mockResolvedValue([]),
    getKnownPatterns: vi.fn().mockResolvedValue([]),
    getRepeatedImages: vi.fn().mockResolvedValue([]),
    getRepeatedPhones: vi.fn().mockResolvedValue([]),
    getRepeatedInvoices: vi.fn().mockResolvedValue([]),
    getMemoryInsights: vi.fn().mockResolvedValue([]),
    getKnowledgeGraphStats: vi.fn().mockResolvedValue({
      nodeCount: 125000, relationshipCount: 450000, communities: 450, largestFraudRingSize: 120, averageConnectivity: 3.6, graphDensity: 0.00015
    }),
  }
}));

describe("Intelligence Center Page", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
  });

  const renderPage = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <IntelligenceCenter />
        </BrowserRouter>
      </QueryClientProvider>
    );

  it("renders page header and search", () => {
    renderPage();
    expect(screen.getByText("Intelligence Center")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Search for Seller/)).toBeInTheDocument();
  });

  it("renders global summary widget", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Global Intelligence Summary")).toBeInTheDocument();
      expect(screen.getByText("10")).toBeInTheDocument(); // knownSellers
    });
  });

  it("renders known sellers widget", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("GlobalTech Store")).toBeInTheDocument();
    });
  });
});

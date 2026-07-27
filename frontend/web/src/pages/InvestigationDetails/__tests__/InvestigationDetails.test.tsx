import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, beforeEach, vi } from "vitest";
import InvestigationDetails from "../index";
import { investigationService } from "../../../services/investigations.service";
import { MOCK_WORKSPACE_DETAILS } from "../../../services/investigations.mock";

vi.mock("react-router-dom", async (importOriginal) => {
  const actual = await importOriginal<typeof import("react-router-dom")>();
  return {
    ...actual,
    useParams: () => ({ id: "INV-9001" }),
  };
});

vi.mock("../../../services/investigations.service", () => ({
  investigationService: {
    getInvestigationDetails: vi.fn().mockResolvedValue(null),
  }
}));

describe("Investigation Workspace Page", () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    vi.clearAllMocks();
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    });
  });

  const renderPage = () =>
    render(
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <InvestigationDetails />
        </BrowserRouter>
      </QueryClientProvider>
    );

  it("renders workspace sections with data", async () => {
    vi.mocked(investigationService.getInvestigationDetails).mockResolvedValue(MOCK_WORKSPACE_DETAILS);
    renderPage();

    await waitFor(() => {
      expect(screen.getByText("INV-9001")).toBeInTheDocument();
    });

    // Check Header
    expect(screen.getByText("Suspicious iPhone 15 Pro Batch")).toBeInTheDocument();

    // Check Summary Card
    expect(screen.getByText("FRAUD")).toBeInTheDocument();

    // Check Timeline
    expect(screen.getByText("Investigation Timeline")).toBeInTheDocument();

    // Check Evidence
    expect(screen.getByText("Collected Evidence")).toBeInTheDocument();

    // Check Consensus
    expect(screen.getByText("Multi-Agent Consensus")).toBeInTheDocument();

    // Check Recommendations
    expect(screen.getByText("Recommended Actions")).toBeInTheDocument();

    // Check Agent Activity
    expect(screen.getByText("Agent Execution Log")).toBeInTheDocument();
  });
});

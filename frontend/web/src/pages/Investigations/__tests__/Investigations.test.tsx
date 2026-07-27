import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Investigations from "../index";
import { investigationService } from "../../../services/investigations.service";
import { MOCK_INVESTIGATIONS } from "../../../services/investigations.mock";

vi.mock("../../../services/investigations.service", () => ({
  investigationService: {
    getInvestigations: vi.fn().mockResolvedValue([]),
  }
}));

describe("Investigations List Page", () => {
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
          <Investigations />
        </BrowserRouter>
      </QueryClientProvider>
    );

  it("renders the header", () => {
    renderPage();
    expect(screen.getByText("Investigations")).toBeInTheDocument();
  });

  it("renders empty state when no data", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("No Investigations Found")).toBeInTheDocument();
    });
  });

  it("renders table with data", async () => {
    vi.mocked(investigationService.getInvestigations).mockResolvedValue(MOCK_INVESTIGATIONS);
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("INV-9001")).toBeInTheDocument();
      expect(screen.getByText("Suspicious iPhone 15 Pro Batch")).toBeInTheDocument();
    });
  });
});

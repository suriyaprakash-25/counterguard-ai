import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, beforeEach, vi } from "vitest";
import IntelligenceCenter from "../index";

// MSW handles requests now
// MSW handles requests now

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

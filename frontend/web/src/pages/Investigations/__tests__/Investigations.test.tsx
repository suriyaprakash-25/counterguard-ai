import { render, screen, waitFor } from "@testing-library/react";
import { http, HttpResponse } from "msw";
import { server } from "../../../mocks/server";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, beforeEach, vi } from "vitest";
import Investigations from "../index";

vi.mock("../../../features/auth/AuthContext", () => ({
  useAuth: vi.fn(() => ({
    user: { id: "1", name: "Test User", role: "admin" },
    isAuthenticated: true,
  })),
  AuthProvider: ({ children }: any) => children,
}));

// Mock the API layer
vi.mock("../../../shared/api/apiClient");

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false } },
});

describe("Investigations List Page", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
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
    expect(
      screen.getByText("Manage and monitor autonomous investigations across all marketplaces.")
    ).toBeInTheDocument();
  });

  it("renders empty state when no data", async () => {
    server.use(
      http.get("*/api/v1/investigations", () => HttpResponse.json({ data: [] }))
    );
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("No Investigations Found")).toBeInTheDocument();
    });
  });

  it("renders table with data", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Suspicious iPhone 15 Pro Batch")).toBeInTheDocument();
      expect(screen.getByText("Counterfeit Nike Air Max")).toBeInTheDocument();
    });
  });
});

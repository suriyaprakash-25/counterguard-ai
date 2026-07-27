import { render, screen, waitFor } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import { describe, it, expect, beforeEach, vi } from "vitest";
import GraphExplorer from "../index";

vi.mock("../services/graph.service", () => ({
  graphService: {
    getGraphData: vi.fn().mockResolvedValue({
      nodes: Array(8).fill({}),
      edges: Array(7).fill({})
    }),
    getGraphStats: vi.fn().mockResolvedValue({}),
    getNodeDetails: vi.fn().mockResolvedValue({})
  }
}));

// Mock cytoscape since it requires a real DOM layout to render properly in jsdom
vi.mock("react-cytoscapejs", () => {
  return {
    default: ({ elements }: any) => (
      <div data-testid="mock-cytoscape">
        Mock Cytoscape - {elements.length} elements
      </div>
    )
  };
});

describe("Graph Explorer Page", () => {
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
          <GraphExplorer />
        </BrowserRouter>
      </QueryClientProvider>
    );

  it("renders header and toolbar", () => {
    renderPage();
    expect(screen.getByText("Knowledge Graph Explorer")).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Search nodes/)).toBeInTheDocument();
  });

  it("renders graph canvas with mocked cytoscape", async () => {
    renderPage();
    await waitFor(() => {
      // 8 nodes + 7 edges = 15 elements
      expect(screen.getByTestId("mock-cytoscape")).toHaveTextContent("Mock Cytoscape - 15 elements");
    });
  });

  it("renders empty node inspector initially", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("No Node Selected")).toBeInTheDocument();
    });
  });
});

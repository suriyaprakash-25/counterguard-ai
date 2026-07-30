import { describe, it, expect } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter } from "react-router-dom";
import ProductIntelligence from "../index";

const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = createTestQueryClient();
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>{ui}</MemoryRouter>
    </QueryClientProvider>
  );
}

describe("ProductIntelligence Workspace", () => {
  it("renders header and search input", () => {
    renderWithProviders(<ProductIntelligence />);
    expect(screen.getAllByText(/Product Intelligence/i).length).toBeGreaterThan(0);
    expect(
      screen.getByPlaceholderText(/Search any product/i)
    ).toBeInTheDocument();
  });

  it("updates search input value on user typing", () => {
    renderWithProviders(<ProductIntelligence />);
    const input = screen.getByPlaceholderText(/Search any product/i) as HTMLInputElement;
    fireEvent.change(input, { target: { value: "CMF Buds 2a" } });
    expect(input.value).toBe("CMF Buds 2a");
  });

  it("renders quick search suggestions when query is empty", () => {
    renderWithProviders(<ProductIntelligence />);
    expect(screen.getAllByText("CMF Buds 2a").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Sony WH-1000XM5").length).toBeGreaterThan(0);
  });
});

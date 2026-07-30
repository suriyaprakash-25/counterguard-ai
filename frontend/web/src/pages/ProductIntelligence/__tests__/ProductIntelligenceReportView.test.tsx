import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { ProductIntelligenceReportView } from "../components/ProductIntelligenceReportView";
import type { ProductIntelligenceReport } from "../../../types/discovery";

const mockReport: ProductIntelligenceReport = {
  report_id: "rpt-test-001",
  product_name: "CMF Buds 2a",
  generated_at: "2026-07-29T12:00:00Z",
  total_listings: 3,
  safe_listings: 1,
  suspicious_listings: 2,
  overall_product_risk: 72.5,
  overall_risk_level: "HIGH",
  highest_risk_marketplace: "Meesho",
  recommended_seller: "Official Nothing Store",
  marketplace_distribution: { Amazon: 1, Meesho: 1, Flipkart: 1 },
  evidence_summary: [
    "Seller created recently (< 30 days old)",
    "87% below MSRP price anomaly detected",
  ],
  coordinator_summary: "Cross-marketplace audit detected high counterfeit probability on Meesho.",
  investigations: [
    {
      investigation_id: "inv-001",
      marketplace: "Amazon",
      listing_url: "https://amazon.in/dp/B001",
      title: "CMF Buds 2a Original",
      seller: "Official Nothing Store",
      price: 2999,
      risk_score: 12.0,
      verdict: "LOW",
      confidence: 0.9,
      evidence_count: 4,
      last_updated: "2026-07-29T12:00:00Z",
    },
    {
      investigation_id: "inv-002",
      marketplace: "Meesho",
      listing_url: "https://meesho.com/s/123",
      title: "CMF Buds 2a Replica",
      seller: "FakeSeller",
      price: 299,
      risk_score: 88.0,
      verdict: "CRITICAL",
      confidence: 0.85,
      evidence_count: 6,
      top_risk_factor: "87% below MSRP price anomaly",
      last_updated: "2026-07-29T12:00:00Z",
    },
  ],
  recommendations: ["Issue immediate takedown notice to Meesho."],
};

describe("ProductIntelligenceReportView", () => {
  it("renders report title and canonical product name", () => {
    render(
      <MemoryRouter>
        <ProductIntelligenceReportView report={mockReport} />
      </MemoryRouter>
    );
    expect(screen.getByText("Product Intelligence Report")).toBeInTheDocument();
    expect(screen.getByText("CMF Buds 2a")).toBeInTheDocument();
    expect(screen.getByText("HIGH RISK")).toBeInTheDocument();
  });

  it("renders key metrics: total listings, safe, suspicious, highest risk market, recommended seller", () => {
    render(
      <MemoryRouter>
        <ProductIntelligenceReportView report={mockReport} />
      </MemoryRouter>
    );
    expect(screen.getByText("3")).toBeInTheDocument(); // total listings
    expect(screen.getByText("1")).toBeInTheDocument(); // safe listings
    expect(screen.getByText("2")).toBeInTheDocument(); // suspicious listings
    expect(screen.getAllByText("Meesho").length).toBeGreaterThan(0); // highest risk marketplace
    expect(screen.getAllByText("Official Nothing Store").length).toBeGreaterThan(0); // recommended seller
  });

  it("renders coordinator summary and evidence points", () => {
    render(
      <MemoryRouter>
        <ProductIntelligenceReportView report={mockReport} />
      </MemoryRouter>
    );
    expect(
      screen.getByText("Cross-marketplace audit detected high counterfeit probability on Meesho.")
    ).toBeInTheDocument();
    expect(screen.getByText("87% below MSRP price anomaly detected")).toBeInTheDocument();
  });

  it("renders drill-down table with case links", () => {
    render(
      <MemoryRouter>
        <ProductIntelligenceReportView report={mockReport} />
      </MemoryRouter>
    );
    expect(screen.getByText("CMF Buds 2a Original")).toBeInTheDocument();
    expect(screen.getByText("CMF Buds 2a Replica")).toBeInTheDocument();
    expect(screen.getAllByText("View Case").length).toBe(2);
  });
});

/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach, vi } from "vitest";
import { JSDOM } from "jsdom";
import { OverlayEngine } from "../overlayEngine";
import { BackendApiClient } from "../../api/client";

vi.mock("../../api/client", () => ({
  BackendApiClient: {
    analyzeProductCard: vi.fn().mockImplementation(async (_baseUrl, cardData) => {
      if (cardData.title.includes("Replica")) {
        return {
          risk_score: 85.0,
          threat_level: "CRITICAL",
          verdict: "COUNTERFEIT_RISK",
          recommendation: "High Counterfeit Risk — Replica listing detected.",
        };
      }
      return {
        risk_score: 15.0,
        threat_level: "SAFE",
        verdict: "VERIFIED",
        recommendation: "CounterGuard Verified — Authentic listing.",
      };
    }),
  },
}));

describe("OverlayEngine Per-Card Dynamic Overlay Unit Tests", () => {
  let overlayEngine: OverlayEngine;

  beforeEach(() => {
    overlayEngine = new OverlayEngine();
  });

  afterEach(() => {
    overlayEngine.cleanup();
  });

  it("extracts card data and requests live backend analysis per product card", async () => {
    const html = `
      <html>
        <body>
          <div data-component-type="s-search-result" id="item-1">
            <h2><a href="https://amazon.in/dp/B001"><span>Sony WH-1000XM5 Headphones</span></a></h2>
            <span class="a-price-whole">29,990</span>
          </div>
          <div data-component-type="s-search-result" id="item-2">
            <h2><a href="https://amazon.in/dp/B002"><span>Super Replica Copy Headphones</span></a></h2>
            <span class="a-price-whole">499</span>
          </div>
        </body>
      </html>
    `;
    const dom = new JSDOM(html);
    const doc = dom.window.document;

    await overlayEngine.initialize("Amazon", doc);

    // Allow async microtasks to settle
    await new Promise((resolve) => setTimeout(resolve, 50));

    expect(BackendApiClient.analyzeProductCard).toHaveBeenCalledTimes(2);

    const safeBadge = doc.querySelector("#item-1 .cg-badge");
    const riskBadge = doc.querySelector("#item-2 .cg-badge");

    expect(safeBadge?.textContent).toContain("Verified Authentic");
    expect(riskBadge?.textContent).toContain("High Counterfeit Risk");
  });

  it("cleanly removes injected badges on cleanup()", async () => {
    const html = `
      <html>
        <body>
          <div data-component-type="s-search-result" id="item-3">
            <h2><a href="https://amazon.in/dp/B003"><span>Nike Air Max</span></a></h2>
          </div>
        </body>
      </html>
    `;
    const dom = new JSDOM(html);
    const doc = dom.window.document;

    await overlayEngine.initialize("Amazon", doc);
    await new Promise((resolve) => setTimeout(resolve, 50));

    expect(doc.querySelectorAll(".cg-badge-container").length).toBe(1);

    overlayEngine.cleanup(doc);
    expect(doc.querySelectorAll(".cg-badge-container").length).toBe(0);
  });
});

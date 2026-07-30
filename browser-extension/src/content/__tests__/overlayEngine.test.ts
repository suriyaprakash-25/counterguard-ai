/**
 * @vitest-environment jsdom
 */
import { describe, it, expect, beforeEach, afterEach } from "vitest";
import { JSDOM } from "jsdom";
import { OverlayEngine } from "../overlayEngine";

describe("OverlayEngine Dynamic Overlay Unit Tests", () => {
  let overlayEngine: OverlayEngine;

  beforeEach(() => {
    overlayEngine = new OverlayEngine();
  });

  afterEach(() => {
    overlayEngine.cleanup();
  });

  it("injects security badges into Amazon product card elements in DOM", () => {
    const html = `
      <html>
        <body>
          <div data-component-type="s-search-result" id="item-1">
            <h2><a href="#"><span>Sony WH-1000XM5 Headphones</span></a></h2>
            <span class="a-price-whole">29,990</span>
          </div>
        </body>
      </html>
    `;
    const dom = new JSDOM(html);
    const doc = dom.window.document;

    overlayEngine.initialize("Amazon", doc);

    const injected = doc.querySelector("#item-1 .cg-badge-container");
    expect(injected).not.toBeNull();
    expect(injected?.querySelector(".cg-badge")?.textContent).toContain("Verified Authentic");
    expect(injected?.querySelector(".cg-tooltip")?.textContent).toContain("CounterGuard Verified");
  });

  it("injects Counterfeit Risk badge for replica product keywords", () => {
    const html = `
      <html>
        <body>
          <div data-component-type="s-search-result" id="item-2">
            <h2><a href="#"><span>Super Replica Copy Sony Headphones</span></a></h2>
          </div>
        </body>
      </html>
    `;
    const dom = new JSDOM(html);
    const doc = dom.window.document;

    overlayEngine.initialize("Amazon", doc);

    const badge = doc.querySelector("#item-2 .cg-badge");
    expect(badge?.textContent).toContain("Counterfeit Risk");
  });

  it("cleanly removes injected badges on cleanup()", () => {
    const html = `
      <html>
        <body>
          <div data-component-type="s-search-result" id="item-3">
            <h2><a href="#"><span>Nike Air Max</span></a></h2>
          </div>
        </body>
      </html>
    `;
    const dom = new JSDOM(html);
    const doc = dom.window.document;

    overlayEngine.initialize("Amazon", doc);
    expect(doc.querySelectorAll(".cg-badge-container").length).toBe(1);

    overlayEngine.cleanup(doc);
    expect(doc.querySelectorAll(".cg-badge-container").length).toBe(0);
  });
});


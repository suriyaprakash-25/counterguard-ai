import { describe, it, expect } from "vitest";
import { MarketplaceDetector } from "../marketplaceDetector.service";

describe("MarketplaceDetector Unit Test Suite", () => {
  // ── 1. Amazon Tests ────────────────────────────────────────────────────────
  describe("Amazon Detection", () => {
    it("detects Amazon product page and extracts ASIN", () => {
      const url = "https://www.amazon.in/dp/B0CX237A12";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Amazon");
      expect(result.pageType).toBe("PRODUCT");
      expect(result.asin).toBe("B0CX237A12");
      expect(result.productId).toBe("B0CX237A12");
    });

    it("detects Amazon gp/product style URL", () => {
      const url = "https://www.amazon.com/gp/product/B08N5WRWNW/ref=ppx_yo_dt_b_asin_title";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Amazon");
      expect(result.pageType).toBe("PRODUCT");
      expect(result.asin).toBe("B08N5WRWNW");
    });

    it("detects Amazon search page and query", () => {
      const url = "https://www.amazon.in/s?k=sony+wh-1000xm5+headphones";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Amazon");
      expect(result.pageType).toBe("SEARCH");
      expect(result.searchQuery).toBe("sony wh-1000xm5 headphones");
    });

    it("detects Amazon seller store page", () => {
      const url = "https://www.amazon.in/sp?seller=A3K184L69X499";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Amazon");
      expect(result.pageType).toBe("SELLER");
      expect(result.sellerId).toBe("A3K184L69X499");
    });
  });

  // ── 2. Flipkart Tests ──────────────────────────────────────────────────────
  describe("Flipkart Detection", () => {
    it("detects Flipkart product page and itm ID", () => {
      const url = "https://www.flipkart.com/sony-wh-1000xm5-headphone/p/itm1234567890123";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Flipkart");
      expect(result.pageType).toBe("PRODUCT");
      expect(result.flipkartId).toBe("itm1234567890123");
      expect(result.productId).toBe("itm1234567890123");
    });

    it("detects Flipkart product page with pid param", () => {
      const url = "https://www.flipkart.com/apple-iphone-15/p/itm123?pid=MOBGTAGQAFZ";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Flipkart");
      expect(result.pageType).toBe("PRODUCT");
      expect(result.flipkartId).toBe("itm123");
    });

    it("detects Flipkart search page and query", () => {
      const url = "https://www.flipkart.com/search?q=wireless+earbuds";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Flipkart");
      expect(result.pageType).toBe("SEARCH");
      expect(result.searchQuery).toBe("wireless earbuds");
    });

    it("detects Flipkart seller page", () => {
      const url = "https://www.flipkart.com/sellers/retailnet";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Flipkart");
      expect(result.pageType).toBe("SELLER");
      expect(result.sellerId).toBe("retailnet");
    });
  });

  // ── 3. Myntra Tests ────────────────────────────────────────────────────────
  describe("Myntra Detection", () => {
    it("detects Myntra product page and numeric ID", () => {
      const url = "https://www.myntra.com/casual-shoes/nike/nike-air-max/24589210/buy";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Myntra");
      expect(result.pageType).toBe("PRODUCT");
      expect(result.productId).toBe("24589210");
    });

    it("detects Myntra search page", () => {
      const url = "https://www.myntra.com/nike-shoes?f=Gender%3Amen";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Myntra");
      expect(result.pageType).toBe("SEARCH");
    });
  });

  // ── 4. AJIO Tests ──────────────────────────────────────────────────────────
  describe("AJIO Detection", () => {
    it("detects AJIO product page and product ID", () => {
      const url = "https://www.ajio.com/nike-air-force-1/p/469123456_blue";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("AJIO");
      expect(result.pageType).toBe("PRODUCT");
      expect(result.productId).toBe("469123456_blue");
    });

    it("detects AJIO search page and text query", () => {
      const url = "https://www.ajio.com/search/?text=running%20shoes";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("AJIO");
      expect(result.pageType).toBe("SEARCH");
      expect(result.searchQuery).toBe("running shoes");
    });
  });

  // ── 5. Meesho Tests ────────────────────────────────────────────────────────
  describe("Meesho Detection", () => {
    it("detects Meesho product page and product ID", () => {
      const url = "https://www.meesho.com/sartorial-kurti/p/1a2b3c";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Meesho");
      expect(result.pageType).toBe("PRODUCT");
      expect(result.productId).toBe("1a2b3c");
    });

    it("detects Meesho search page and query", () => {
      const url = "https://www.meesho.com/search?q=saree";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Meesho");
      expect(result.pageType).toBe("SEARCH");
      expect(result.searchQuery).toBe("saree");
    });

    it("detects Meesho supplier page", () => {
      const url = "https://www.meesho.com/supplier/shop12345";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("Meesho");
      expect(result.pageType).toBe("SELLER");
      expect(result.sellerId).toBe("shop12345");
    });
  });

  // ── 6. TradeIndia Tests ───────────────────────────────────────────────────
  describe("TradeIndia Detection", () => {
    it("detects TradeIndia product page and fp ID", () => {
      const url = "https://www.tradeindia.com/fp123456/industrial-pump.html";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("TradeIndia");
      expect(result.pageType).toBe("PRODUCT");
      expect(result.productId).toBe("123456");
    });

    it("detects TradeIndia search page and query", () => {
      const url = "https://www.tradeindia.com/search.html?ss=hydraulic+valves";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("TradeIndia");
      expect(result.pageType).toBe("SEARCH");
      expect(result.searchQuery).toBe("hydraulic valves");
    });

    it("detects TradeIndia supplier subdomain store", () => {
      const url = "https://abcexporters.tradeindia.com";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(true);
      expect(result.marketplace).toBe("TradeIndia");
      expect(result.pageType).toBe("SELLER");
      expect(result.sellerId).toBe("abcexporters");
    });
  });

  // ── 7. Non-Marketplace Generic URL Tests ──────────────────────────────────
  describe("Generic Non-Marketplace URL Fallback", () => {
    it("handles non-marketplace generic URL gracefully", () => {
      const url = "https://example.com/about-us";
      const result = MarketplaceDetector.detect(url);

      expect(result.isMarketplace).toBe(false);
      expect(result.marketplace).toBe("Unknown");
      expect(result.pageType).toBe("UNKNOWN");
    });

    it("handles invalid or empty URL strings gracefully", () => {
      const result = MarketplaceDetector.detect("");

      expect(result.isMarketplace).toBe(false);
      expect(result.marketplace).toBe("Unknown");
      expect(result.pageType).toBe("UNKNOWN");
    });
  });
});

/**
 * marketplaceDetector.service.ts — Intelligent Marketplace & Page Type Detector
 * Identifies Amazon, Flipkart, Myntra, AJIO, Meesho, and TradeIndia marketplace URLs,
 * classifies page type (PRODUCT, SEARCH, SELLER, UNKNOWN), and extracts product IDs,
 * ASIN, Flipkart ID, search queries, and seller IDs without DOM scraping.
 */

import {
  MarketplaceDetectionResult,
  MarketplaceType,
  PageType,
} from "../types/marketplace";

export class MarketplaceDetector {
  /**
   * Primary entry point: Detect marketplace, page type, IDs, and metadata from URL string
   */
  static detect(url: string): MarketplaceDetectionResult {
    const fallback: MarketplaceDetectionResult = {
      isMarketplace: false,
      marketplace: "Unknown",
      url: url,
      pageType: "UNKNOWN",
      metadata: {},
    };

    if (!url || typeof url !== "string") {
      return fallback;
    }

    try {
      const parsedUrl = new URL(url);
      const host = parsedUrl.hostname.toLowerCase().replace(/^www\./, "");
      const pathname = parsedUrl.pathname;
      const searchParams = parsedUrl.searchParams;

      // 1. Amazon Detection
      if (host.includes("amazon.")) {
        return this.detectAmazon(url, parsedUrl, pathname, searchParams);
      }

      // 2. Flipkart Detection
      if (host.includes("flipkart.com")) {
        return this.detectFlipkart(url, parsedUrl, pathname, searchParams);
      }

      // 3. Myntra Detection
      if (host.includes("myntra.com")) {
        return this.detectMyntra(url, parsedUrl, pathname, searchParams);
      }

      // 4. AJIO Detection
      if (host.includes("ajio.com")) {
        return this.detectAjio(url, parsedUrl, pathname, searchParams);
      }

      // 5. Meesho Detection
      if (host.includes("meesho.com")) {
        return this.detectMeesho(url, parsedUrl, pathname, searchParams);
      }

      // 6. TradeIndia Detection
      if (host.includes("tradeindia.com")) {
        return this.detectTradeIndia(url, parsedUrl, pathname, searchParams, host);
      }

      return fallback;
    } catch {
      return fallback;
    }
  }

  // ── 1. Amazon ────────────────────────────────────────────────────────────────

  private static detectAmazon(
    url: string,
    parsedUrl: URL,
    pathname: string,
    searchParams: URLSearchParams
  ): MarketplaceDetectionResult {
    let pageType: PageType = "UNKNOWN";
    let asin: string | undefined;
    let sellerId: string | undefined;
    let searchQuery: string | undefined;

    // ASIN Pattern: /dp/B0CX237A12 or /gp/product/B0CX237A12
    const dpMatch = pathname.match(/\/(?:dp|gp\/product|product-reviews)\/([A-Z0-9]{10})/i);
    if (dpMatch && dpMatch[1]) {
      pageType = "PRODUCT";
      asin = dpMatch[1].toUpperCase();
    }

    // Seller Pattern: /sp?seller=A123456789 or /shops/A123456789 or /seller/A123456789
    if (searchParams.has("seller")) {
      sellerId = searchParams.get("seller") || undefined;
      if (pageType === "UNKNOWN") pageType = "SELLER";
    } else {
      const sellerMatch = pathname.match(/\/(?:shops|seller|stores)\/([a-zA-Z0-9_-]+)/i);
      if (sellerMatch && sellerMatch[1]) {
        sellerId = sellerMatch[1];
        if (pageType === "UNKNOWN") pageType = "SELLER";
      }
    }

    // Search Pattern: /s?k=query or /s/ or /b?node=
    if (pathname.startsWith("/s") || pathname.includes("/search/") || searchParams.has("k") || searchParams.has("keywords")) {
      if (pageType === "UNKNOWN") pageType = "SEARCH";
      searchQuery = searchParams.get("k") || searchParams.get("keywords") || searchParams.get("field-keywords") || undefined;
    }

    return {
      isMarketplace: true,
      marketplace: "Amazon",
      url,
      pageType,
      productId: asin,
      asin,
      searchQuery,
      sellerId,
      metadata: {
        domain: parsedUrl.hostname,
        tld: parsedUrl.hostname.split(".").pop() || "com",
        hasAsin: Boolean(asin),
      },
    };
  }

  // ── 2. Flipkart ─────────────────────────────────────────────────────────────

  private static detectFlipkart(
    url: string,
    parsedUrl: URL,
    pathname: string,
    searchParams: URLSearchParams
  ): MarketplaceDetectionResult {
    let pageType: PageType = "UNKNOWN";
    let flipkartId: string | undefined;
    let sellerId: string | undefined;
    let searchQuery: string | undefined;

    // Flipkart Item ID Pattern: /p/itm123456789 or pid query param
    const itmMatch = pathname.match(/\/p\/(itm[a-zA-Z0-9]+)/i);
    if (itmMatch && itmMatch[1]) {
      pageType = "PRODUCT";
      flipkartId = itmMatch[1];
    } else if (pathname.includes("/p/") || searchParams.has("pid")) {
      pageType = "PRODUCT";
      flipkartId = searchParams.get("pid") || undefined;
    }

    // Seller Pattern: /sellers/seller-name or sellerId param
    if (searchParams.has("sellerId")) {
      sellerId = searchParams.get("sellerId") || undefined;
      if (pageType === "UNKNOWN") pageType = "SELLER";
    } else if (pathname.includes("/sellers/")) {
      const parts = pathname.split("/sellers/");
      if (parts[1]) sellerId = parts[1].split("/")[0];
      if (pageType === "UNKNOWN") pageType = "SELLER";
    }

    // Search Pattern: /search?q=query or /pr?sid=
    if (pathname.includes("/search") || searchParams.has("q") || pathname.startsWith("/pr")) {
      if (pageType === "UNKNOWN") pageType = "SEARCH";
      searchQuery = searchParams.get("q") || undefined;
    }

    return {
      isMarketplace: true,
      marketplace: "Flipkart",
      url,
      pageType,
      productId: flipkartId,
      flipkartId,
      searchQuery,
      sellerId,
      metadata: {
        hasFlipkartId: Boolean(flipkartId),
      },
    };
  }

  // ── 3. Myntra ───────────────────────────────────────────────────────────────

  private static detectMyntra(
    url: string,
    parsedUrl: URL,
    pathname: string,
    searchParams: URLSearchParams
  ): MarketplaceDetectionResult {
    let pageType: PageType = "UNKNOWN";
    let productId: string | undefined;
    let sellerId: string | undefined;
    let searchQuery: string | undefined;

    // Product Pattern: /category/brand/title/24589210/buy or /24589210/buy
    const buyMatch = pathname.match(/\/([0-9]{5,10})(?:\/buy)?$/i);
    if (buyMatch && buyMatch[1]) {
      pageType = "PRODUCT";
      productId = buyMatch[1];
    } else if (pathname.endsWith("/buy")) {
      pageType = "PRODUCT";
      const digits = pathname.match(/([0-9]{5,10})/);
      if (digits) productId = digits[1];
    }

    // Search Pattern: /search/nike or /nike-shoes?f=... or /shop/
    if (pathname.includes("/search/") || searchParams.has("rawQuery") || searchParams.has("f")) {
      if (pageType === "UNKNOWN") pageType = "SEARCH";
      searchQuery = searchParams.get("rawQuery") || pathname.split("/").pop()?.replace(/-/g, " ") || undefined;
    } else if (pageType === "UNKNOWN" && pathname.length > 2 && !pathname.includes("/checkout")) {
      // Myntra uses slug-based category search pages e.g. /men-casual-shoes
      pageType = "SEARCH";
      searchQuery = pathname.replace(/^\//, "").replace(/-/g, " ");
    }

    if (searchParams.has("seller")) {
      sellerId = searchParams.get("seller") || undefined;
      if (pageType === "UNKNOWN") pageType = "SELLER";
    }

    return {
      isMarketplace: true,
      marketplace: "Myntra",
      url,
      pageType,
      productId,
      searchQuery,
      sellerId,
      metadata: {
        hasProductId: Boolean(productId),
      },
    };
  }

  // ── 4. AJIO ─────────────────────────────────────────────────────────────────

  private static detectAjio(
    url: string,
    parsedUrl: URL,
    pathname: string,
    searchParams: URLSearchParams
  ): MarketplaceDetectionResult {
    let pageType: PageType = "UNKNOWN";
    let productId: string | undefined;
    let searchQuery: string | undefined;

    // Product Pattern: /brand-title/p/469123456_blue or /p/469123456
    const pMatch = pathname.match(/\/p\/([a-zA-Z0-9_]+)/i);
    if (pMatch && pMatch[1]) {
      pageType = "PRODUCT";
      productId = pMatch[1];
    }

    // Search Pattern: /search/?text=query or /s/
    if (pathname.includes("/search") || searchParams.has("text") || pathname.startsWith("/s/")) {
      if (pageType === "UNKNOWN") pageType = "SEARCH";
      searchQuery = searchParams.get("text") || undefined;
    }

    return {
      isMarketplace: true,
      marketplace: "AJIO",
      url,
      pageType,
      productId,
      searchQuery,
      metadata: {
        hasProductId: Boolean(productId),
      },
    };
  }

  // ── 5. Meesho ───────────────────────────────────────────────────────────────

  private static detectMeesho(
    url: string,
    parsedUrl: URL,
    pathname: string,
    searchParams: URLSearchParams
  ): MarketplaceDetectionResult {
    let pageType: PageType = "UNKNOWN";
    let productId: string | undefined;
    let sellerId: string | undefined;
    let searchQuery: string | undefined;

    // Product Pattern: /p/1a2b3 or /product-title/p/1a2b3
    const pMatch = pathname.match(/\/p\/([a-zA-Z0-9]+)/i);
    if (pMatch && pMatch[1]) {
      pageType = "PRODUCT";
      productId = pMatch[1];
    }

    // Supplier / Seller Pattern: /s/shop/12345 or /supplier/12345
    const sellerMatch = pathname.match(/\/(?:s\/shop|supplier)\/([a-zA-Z0-9_-]+)/i);
    if (sellerMatch && sellerMatch[1]) {
      pageType = "SELLER";
      sellerId = sellerMatch[1];
    }

    // Search Pattern: /search?q=query
    if (pathname.includes("/search") || searchParams.has("q")) {
      if (pageType === "UNKNOWN") pageType = "SEARCH";
      searchQuery = searchParams.get("q") || undefined;
    }

    return {
      isMarketplace: true,
      marketplace: "Meesho",
      url,
      pageType,
      productId,
      searchQuery,
      sellerId,
      metadata: {
        hasProductId: Boolean(productId),
      },
    };
  }

  // ── 6. TradeIndia ───────────────────────────────────────────────────────────

  private static detectTradeIndia(
    url: string,
    parsedUrl: URL,
    pathname: string,
    searchParams: URLSearchParams,
    host: string
  ): MarketplaceDetectionResult {
    let pageType: PageType = "UNKNOWN";
    let productId: string | undefined;
    let sellerId: string | undefined;
    let searchQuery: string | undefined;

    // Subdomain Seller Store Pattern: companyname.tradeindia.com
    if (host !== "tradeindia.com" && host.endsWith(".tradeindia.com")) {
      pageType = "SELLER";
      sellerId = host.replace(".tradeindia.com", "");
    }

    // Product Pattern: /fp123456/title.html or /product/title-123456.html
    const fpMatch = pathname.match(/\/fp([0-9]+)\//i) || pathname.match(/-([0-9]+)\.html$/i);
    if (fpMatch && fpMatch[1]) {
      pageType = "PRODUCT";
      productId = fpMatch[1];
    }

    // Search Pattern: /search.html?ss=query or /search?q=query
    if (pathname.includes("/search") || searchParams.has("ss") || searchParams.has("q") || pathname.includes("/Seller/")) {
      if (pageType === "UNKNOWN") pageType = "SEARCH";
      searchQuery = searchParams.get("ss") || searchParams.get("q") || undefined;
    }

    // Exporter / Company Page Pattern
    if (pathname.includes("/exporter/") || pathname.includes("/company/")) {
      if (pageType === "UNKNOWN") pageType = "SELLER";
      const parts = pathname.split("/");
      sellerId = parts[2]?.replace(".html", "") || sellerId;
    }

    return {
      isMarketplace: true,
      marketplace: "TradeIndia",
      url,
      pageType,
      productId,
      searchQuery,
      sellerId,
      metadata: {
        hasProductId: Boolean(productId),
        isSubdomainStore: host !== "tradeindia.com",
      },
    };
  }
}

/**
 * marketplace.ts — Strict TypeScript type definitions for Intelligent Marketplace Detector
 */

export type MarketplaceType =
  | "Amazon"
  | "Flipkart"
  | "Myntra"
  | "AJIO"
  | "Meesho"
  | "TradeIndia"
  | "Unknown";

export type PageType = "SEARCH" | "PRODUCT" | "SELLER" | "UNKNOWN";

export interface MarketplaceDetectionResult {
  isMarketplace: boolean;
  marketplace: MarketplaceType;
  url: string;
  pageType: PageType;
  productId?: string;
  asin?: string;
  flipkartId?: string;
  searchQuery?: string;
  sellerId?: string;
  metadata: Record<string, string | number | boolean>;
}

/**
 * productCard.ts — Strict TypeScript DTO for Extracted Product Details
 */

export interface ExtractedProductCard {
  title: string;
  seller: string;
  price: number;
  currency: string;
  url: string;
  image?: string;
  rating?: number;
  reviewCount?: number;
  deliveryInfo?: string;
  specifications: Record<string, string>;
  availability: string;
  brand?: string;
  marketplace: string;
  extractedAt: string;
  confidenceScore: number; // 0.0 to 100.0
  failedSelectors: string[];
}

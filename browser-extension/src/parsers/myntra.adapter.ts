/**
 * myntra.adapter.ts — Myntra DOM Parser Adapter
 */

import { BaseParserAdapter } from "./base.adapter";
import { ExtractedProductCard } from "../types/productCard";

export class MyntraAdapter extends BaseParserAdapter {
  readonly marketplaceName = "Myntra";

  private readonly TITLE_SELECTORS = [
    "h1.pdp-name",
    "h1.pdp-title",
    ".pdp-name",
    "meta[property='og:title']",
  ];

  private readonly BRAND_SELECTORS = [
    "h1.pdp-title",
    ".pdp-title",
  ];

  private readonly PRICE_SELECTORS = [
    "span.pdp-price",
    ".pdp-price strong",
    "span.pdp-mrp",
  ];

  private readonly SELLER_SELECTORS = [
    ".seller-name",
    ".pdp-seller-name",
    ".supplier-name",
    "span.supplier-name",
  ];

  private readonly IMAGE_SELECTORS = [
    "div.image-grid-image",
    "img.pdp-image",
    "meta[property='og:image']",
  ];

  private readonly RATING_SELECTORS = [
    "div.index-overallRating div",
    "span.index-overallRating",
  ];

  private readonly REVIEWS_SELECTORS = [
    "div.index-ratingsCount",
  ];

  parse(doc: Document, url: string): ExtractedProductCard {
    const failedSelectors: string[] = [];

    const rawTitle = this.getTextBySelectors(doc, this.TITLE_SELECTORS, "title", failedSelectors);
    const rawBrand = this.getTextBySelectors(doc, this.BRAND_SELECTORS, "brand", failedSelectors);
    const rawPrice = this.getTextBySelectors(doc, this.PRICE_SELECTORS, "price", failedSelectors);
    const rawSeller = this.getTextBySelectors(doc, this.SELLER_SELECTORS, "seller", failedSelectors);
    const image = this.getImageBySelectors(doc, this.IMAGE_SELECTORS, "image", failedSelectors);
    const rawRating = this.getTextBySelectors(doc, this.RATING_SELECTORS, "rating", failedSelectors);
    const rawReviews = this.getTextBySelectors(doc, this.REVIEWS_SELECTORS, "reviewCount", failedSelectors);

    const price = rawPrice ? this.cleanPrice(rawPrice) : 0;
    const rating = rawRating ? this.cleanNumber(rawRating) : undefined;
    const reviewCount = rawReviews ? this.cleanNumber(rawReviews) : undefined;

    // Specifications
    const specifications: Record<string, string> = {};
    doc.querySelectorAll("div.index-row").forEach((row) => {
      const label = row.querySelector("div.index-rowKey")?.textContent?.trim();
      const val = row.querySelector("div.index-rowValue")?.textContent?.trim();
      if (label && val) {
        specifications[label] = val;
      }
    });

    const card: ExtractedProductCard = {
      title: rawTitle ? `${rawBrand ? rawBrand + " " : ""}${rawTitle}`.trim() : "Unknown Myntra Product",
      seller: rawSeller || "Verified Myntra Partner",
      price,
      currency: "INR",
      url,
      image,
      rating,
      reviewCount,
      specifications,
      availability: "In Stock",
      brand: rawBrand,
      marketplace: this.marketplaceName,
      extractedAt: new Date().toISOString(),
      confidenceScore: 0,
      failedSelectors,
    };

    card.confidenceScore = this.calculateConfidence(card);
    return card;
  }
}

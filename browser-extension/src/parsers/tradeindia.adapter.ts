/**
 * tradeindia.adapter.ts — TradeIndia B2B DOM Parser Adapter
 */

import { BaseParserAdapter } from "./base.adapter";
import { ExtractedProductCard } from "../types/productCard";

export class TradeIndiaAdapter extends BaseParserAdapter {
  readonly marketplaceName = "TradeIndia";

  private readonly TITLE_SELECTORS = [
    "h1.title",
    ".product-name",
    "h1.heading",
    "h1",
  ];

  private readonly PRICE_SELECTORS = [
    ".price",
    ".product-price",
    ".offer-price",
    "span.price-val",
  ];

  private readonly SELLER_SELECTORS = [
    ".company-name",
    ".co-name",
    ".seller-details a",
    ".supplier-name",
  ];

  private readonly IMAGE_SELECTORS = [
    ".product-image img",
    "img.main-img",
    "img.prod-img",
  ];

  parse(doc: Document, url: string): ExtractedProductCard {
    const failedSelectors: string[] = [];

    const rawTitle = this.getTextBySelectors(doc, this.TITLE_SELECTORS, "title", failedSelectors);
    const rawPrice = this.getTextBySelectors(doc, this.PRICE_SELECTORS, "price", failedSelectors);
    const rawSeller = this.getTextBySelectors(doc, this.SELLER_SELECTORS, "seller", failedSelectors);
    const image = this.getImageBySelectors(doc, this.IMAGE_SELECTORS, "image", failedSelectors);

    const price = rawPrice ? this.cleanPrice(rawPrice) : 0;

    const specifications: Record<string, string> = {};
    doc.querySelectorAll(".product-specs tr, .spec-table tr").forEach((row) => {
      const label = row.querySelector("th, td:first-child")?.textContent?.trim();
      const val = row.querySelector("td:last-child")?.textContent?.trim();
      if (label && val) specifications[label] = val;
    });

    const card: ExtractedProductCard = {
      title: rawTitle || "Unknown TradeIndia Product",
      seller: rawSeller || "TradeIndia Verified Supplier",
      price,
      currency: "INR",
      url,
      image,
      specifications,
      availability: "In Stock",
      marketplace: this.marketplaceName,
      extractedAt: new Date().toISOString(),
      confidenceScore: 0,
      failedSelectors,
    };

    card.confidenceScore = this.calculateConfidence(card);
    return card;
  }
}

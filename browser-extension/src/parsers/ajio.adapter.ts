/**
 * ajio.adapter.ts — AJIO DOM Parser Adapter
 */

import { BaseParserAdapter } from "./base.adapter";
import { ExtractedProductCard } from "../types/productCard";

export class AJIOAdapter extends BaseParserAdapter {
  readonly marketplaceName = "AJIO";

  private readonly TITLE_SELECTORS = [
    "h1.prod-name",
    ".prod-title",
    "h2.brand-name",
    "meta[property='og:title']",
  ];

  private readonly BRAND_SELECTORS = [
    "h2.brand-name",
    ".brand-name",
  ];

  private readonly PRICE_SELECTORS = [
    ".prod-sp",
    ".prod-cp",
    "div.price-val",
    "span.price-val",
  ];

  private readonly SELLER_SELECTORS = [
    ".seller-name",
    ".vendor-name",
    "span.mandatory-info-value",
  ];

  private readonly IMAGE_SELECTORS = [
    "img.rilrtl-lazy-img",
    ".img-container img",
    "meta[property='og:image']",
  ];

  parse(doc: Document, url: string): ExtractedProductCard {
    const failedSelectors: string[] = [];

    const rawTitle = this.getTextBySelectors(doc, this.TITLE_SELECTORS, "title", failedSelectors);
    const rawBrand = this.getTextBySelectors(doc, this.BRAND_SELECTORS, "brand", failedSelectors);
    const rawPrice = this.getTextBySelectors(doc, this.PRICE_SELECTORS, "price", failedSelectors);
    const rawSeller = this.getTextBySelectors(doc, this.SELLER_SELECTORS, "seller", failedSelectors);
    const image = this.getImageBySelectors(doc, this.IMAGE_SELECTORS, "image", failedSelectors);

    const price = rawPrice ? this.cleanPrice(rawPrice) : 0;

    const specifications: Record<string, string> = {};
    doc.querySelectorAll("section.prod-desc li").forEach((li) => {
      const text = li.textContent?.trim();
      if (text && text.includes(":")) {
        const [k, v] = text.split(":");
        if (k && v) specifications[k.trim()] = v.trim();
      }
    });

    const card: ExtractedProductCard = {
      title: rawTitle ? `${rawBrand ? rawBrand + " " : ""}${rawTitle}`.trim() : "Unknown AJIO Product",
      seller: rawSeller || "Reliance Retail / AJIO Verified",
      price,
      currency: "INR",
      url,
      image,
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

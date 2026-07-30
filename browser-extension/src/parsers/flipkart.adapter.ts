/**
 * flipkart.adapter.ts — Flipkart DOM Parser Adapter
 */

import { BaseParserAdapter } from "./base.adapter";
import { ExtractedProductCard } from "../types/productCard";

export class FlipkartAdapter extends BaseParserAdapter {
  readonly marketplaceName = "Flipkart";

  private readonly TITLE_SELECTORS = [
    "span.VU-VGd",
    ".B_NuH2",
    "h1._6ERy96",
    "span.B_NuH2",
    "h1 span",
  ];

  private readonly PRICE_SELECTORS = [
    "div.Nx9bqj._1pcnmf",
    "div._30jeq3._16JgWd",
    "div._30jeq3",
    "div.Nx9bqj",
    "._3iEr18",
  ];

  private readonly SELLER_SELECTORS = [
    "#sellerName",
    "div._1RLoy span",
    "div._2m_Rj6",
    "div._1RLoy",
    "span._2M_Rj6",
  ];

  private readonly IMAGE_SELECTORS = [
    "img._396cs4._2amPTt._3qWZwn",
    "img._396cs4",
    "img._2r_T1I",
    "img.D9MuR4",
  ];

  private readonly RATING_SELECTORS = [
    "div._3LWZlK",
    "div._3LWZlK._1BLPMq",
    "div.X18hSpecification",
  ];

  private readonly REVIEWS_SELECTORS = [
    "span._2_R_DZ",
    "span.W_uj1a",
  ];

  parse(doc: Document, url: string): ExtractedProductCard {
    const failedSelectors: string[] = [];

    const rawTitle = this.getTextBySelectors(doc, this.TITLE_SELECTORS, "title", failedSelectors);
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
    doc.querySelectorAll("tr._1s5BxE, div._1uhK2W").forEach((row) => {
      const label = row.querySelector("td._1h_7y, div._2Hzd71")?.textContent?.trim();
      const val = row.querySelector("td.URCorrelation, div._3F54n")?.textContent?.trim();
      if (label && val) {
        specifications[label] = val;
      }
    });

    const card: ExtractedProductCard = {
      title: rawTitle || "Unknown Flipkart Product",
      seller: rawSeller ? rawSeller.replace(/\s*7 Days Replacement Policy.*$/i, "").trim() : "Unverified Flipkart Seller",
      price,
      currency: "INR",
      url,
      image,
      rating,
      reviewCount,
      deliveryInfo: doc.querySelector("div._3XINDu")?.textContent?.trim() || undefined,
      specifications,
      availability: doc.querySelector("div._16FRp0") ? "Out of Stock" : "In Stock",
      marketplace: this.marketplaceName,
      extractedAt: new Date().toISOString(),
      confidenceScore: 0,
      failedSelectors,
    };

    card.confidenceScore = this.calculateConfidence(card);
    return card;
  }
}

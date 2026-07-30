/**
 * amazon.adapter.ts — Amazon DOM Parser Adapter
 */

import { BaseParserAdapter } from "./base.adapter";
import { ExtractedProductCard } from "../types/productCard";

export class AmazonAdapter extends BaseParserAdapter {
  readonly marketplaceName = "Amazon";

  private readonly TITLE_SELECTORS = [
    "#productTitle",
    ".a-size-large.product-title-word-break",
    "#title span",
    "h1.a-size-large",
    "meta[name='title']",
  ];

  private readonly PRICE_SELECTORS = [
    ".a-price-whole",
    "#priceblock_ourprice",
    "#priceblock_dealprice",
    ".a-offscreen",
    "#corePrice_feature_div .a-offscreen",
    "span.a-color-price",
  ];

  private readonly SELLER_SELECTORS = [
    "#sellerProfileTriggerId",
    "#merchant-info a",
    "#merchant-info",
    ".tabular-buybox-text[merchant_name]",
    "#bylineInfo",
  ];

  private readonly IMAGE_SELECTORS = [
    "#landingImage",
    "#imgBlkFront",
    "img.a-dynamic-image",
    "#main-image-container img",
  ];

  private readonly RATING_SELECTORS = [
    "span.a-icon-alt",
    "#acrPopover",
    "i.a-icon-star span",
  ];

  private readonly REVIEWS_SELECTORS = [
    "#acrCustomerReviewText",
    "#reviews-med-link",
  ];

  private readonly BRAND_SELECTORS = [
    "#bylineInfo",
    "a#bylineInfo",
    ".po-brand .a-span9 span",
  ];

  parse(doc: Document, url: string): ExtractedProductCard {
    const failedSelectors: string[] = [];

    const rawTitle = this.getTextBySelectors(doc, this.TITLE_SELECTORS, "title", failedSelectors);
    const rawPrice = this.getTextBySelectors(doc, this.PRICE_SELECTORS, "price", failedSelectors);
    const rawSeller = this.getTextBySelectors(doc, this.SELLER_SELECTORS, "seller", failedSelectors);
    const image = this.getImageBySelectors(doc, this.IMAGE_SELECTORS, "image", failedSelectors);
    const rawRating = this.getTextBySelectors(doc, this.RATING_SELECTORS, "rating", failedSelectors);
    const rawReviews = this.getTextBySelectors(doc, this.REVIEWS_SELECTORS, "reviewCount", failedSelectors);
    const rawBrand = this.getTextBySelectors(doc, this.BRAND_SELECTORS, "brand", failedSelectors);

    const price = rawPrice ? this.cleanPrice(rawPrice) : 0;
    const rating = rawRating ? this.cleanNumber(rawRating) : undefined;
    const reviewCount = rawReviews ? this.cleanNumber(rawReviews) : undefined;

    // Specifications
    const specifications: Record<string, string> = {};
    doc.querySelectorAll("#productDetails_techSpec_section_1 tr, #detailBullets_feature_div li").forEach((row) => {
      const label = row.querySelector("th, span.a-text-bold")?.textContent?.trim().replace(/:$/, "");
      const val = row.querySelector("td, span:not(.a-text-bold)")?.textContent?.trim();
      if (label && val) {
        specifications[label] = val;
      }
    });

    const availabilityEl = doc.querySelector("#availability span");
    const availability = availabilityEl?.textContent?.trim() || "In Stock";

    const card: ExtractedProductCard = {
      title: rawTitle || "Unknown Amazon Product",
      seller: rawSeller || "Unverified Amazon Seller",
      price,
      currency: "INR",
      url,
      image,
      rating,
      reviewCount,
      deliveryInfo: doc.querySelector("#mir-bft-message-link")?.textContent?.trim() || undefined,
      specifications,
      availability,
      brand: rawBrand?.replace(/^Brand:\s*/i, "").replace(/^Visit the\s*/i, "").replace(/\s*Store$/i, ""),
      marketplace: this.marketplaceName,
      extractedAt: new Date().toISOString(),
      confidenceScore: 0,
      failedSelectors,
    };

    card.confidenceScore = this.calculateConfidence(card);
    return card;
  }
}

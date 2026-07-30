/**
 * meesho.adapter.ts — Meesho DOM Parser Adapter
 */

import { BaseParserAdapter } from "./base.adapter";
import { ExtractedProductCard } from "../types/productCard";

export class MeeshoAdapter extends BaseParserAdapter {
  readonly marketplaceName = "Meesho";

  private readonly TITLE_SELECTORS = [
    "h1.ProductDescription__Title",
    "span.ProductTitle",
    "h1",
    "meta[property='og:title']",
  ];

  private readonly PRICE_SELECTORS = [
    "h4.ProductPrice__Price",
    "h4.price",
    "span.price",
    "h4",
  ];

  private readonly SELLER_SELECTORS = [
    "span.SupplierName",
    ".shop-name",
    "span.SupplierCard__ShopName",
  ];

  private readonly IMAGE_SELECTORS = [
    "img.ProductImage",
    "img.carousel-img",
    "meta[property='og:image']",
  ];

  private readonly RATING_SELECTORS = [
    "span.Rating__RatingCount",
    "span.RatingBar__RatingCount",
  ];

  parse(doc: Document, url: string): ExtractedProductCard {
    const failedSelectors: string[] = [];

    const rawTitle = this.getTextBySelectors(doc, this.TITLE_SELECTORS, "title", failedSelectors);
    const rawPrice = this.getTextBySelectors(doc, this.PRICE_SELECTORS, "price", failedSelectors);
    const rawSeller = this.getTextBySelectors(doc, this.SELLER_SELECTORS, "seller", failedSelectors);
    const image = this.getImageBySelectors(doc, this.IMAGE_SELECTORS, "image", failedSelectors);
    const rawRating = this.getTextBySelectors(doc, this.RATING_SELECTORS, "rating", failedSelectors);

    const price = rawPrice ? this.cleanPrice(rawPrice) : 0;
    const rating = rawRating ? this.cleanNumber(rawRating) : undefined;

    const card: ExtractedProductCard = {
      title: rawTitle || "Unknown Meesho Product",
      seller: rawSeller || "Meesho Verified Supplier",
      price,
      currency: "INR",
      url,
      image,
      rating,
      specifications: {},
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

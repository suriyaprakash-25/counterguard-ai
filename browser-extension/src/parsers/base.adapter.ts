/**
 * base.adapter.ts — Abstract Base Parser Adapter & Helper Utilities
 * Provides resilient multi-selector fallback cascades, price cleaning,
 * error logging via ExtensionLogger, and extraction confidence calculation.
 */

import { ExtractedProductCard } from "../types/productCard";
import { ExtensionLogger } from "../services/logger.service";

export abstract class BaseParserAdapter {
  abstract readonly marketplaceName: string;

  /**
   * Primary entry point: Parse Document and return ExtractedProductCard
   */
  abstract parse(doc: Document, url: string): ExtractedProductCard;

  /**
   * Extracts text content using an ordered array of CSS selectors (Fallback Cascade)
   */
  protected getTextBySelectors(
    doc: Document,
    selectors: string[],
    fieldName: string,
    failedSelectors: string[]
  ): string | undefined {
    for (const selector of selectors) {
      try {
        const el = doc.querySelector(selector);
        if (el) {
          const text = el.textContent?.trim();
          if (text) return text;
        }
      } catch (err) {
        ExtensionLogger.debug(`Invalid selector '${selector}' for field '${fieldName}'`);
      }
      failedSelectors.push(`${fieldName}:${selector}`);
    }
    ExtensionLogger.debug(`[${this.marketplaceName}] Field '${fieldName}' absent via selectors.`);
    return undefined;
  }

  /**
   * Extracts numeric value (e.g. price, rating, review count) using selector fallback array
   */
  protected getNumberBySelectors(
    doc: Document,
    selectors: string[],
    fieldName: string,
    failedSelectors: string[]
  ): number | undefined {
    const rawText = this.getTextBySelectors(doc, selectors, fieldName, failedSelectors);
    if (!rawText) return undefined;
    return this.cleanNumber(rawText);
  }

  /**
   * Extracts image URL using selector fallback array (checks src, data-src, srcset)
   */
  protected getImageBySelectors(
    doc: Document,
    selectors: string[],
    fieldName: string,
    failedSelectors: string[]
  ): string | undefined {
    for (const selector of selectors) {
      try {
        const imgEl = doc.querySelector(selector) as HTMLImageElement | null;
        if (imgEl) {
          const src =
            imgEl.getAttribute("src") ||
            imgEl.getAttribute("data-src") ||
            imgEl.getAttribute("data-old-hires") ||
            imgEl.getAttribute("srcset")?.split(" ")[0];
          if (src && !src.startsWith("data:image/svg")) return src;
        }
      } catch (err) {
        // ignore
      }
      failedSelectors.push(`${fieldName}:${selector}`);
    }
    return undefined;
  }

  /**
   * Clean numeric strings (e.g. "₹1,499.00" -> 1499.0, "Rs. 12995" -> 12995)
   */
  protected cleanPrice(raw: string): number {
    if (!raw) return 0;
    const cleanedText = raw.replace(/^[^0-9]*/, "").replace(/,/g, "");
    const match = cleanedText.match(/([0-9]+(?:\.[0-9]{1,2})?)/);
    if (match && match[1]) {
      const parsed = parseFloat(match[1]);
      return isNaN(parsed) ? 0 : parsed;
    }
    return 0;
  }


  /**
   * Clean general numbers (e.g. "4.2 out of 5" -> 4.2, "(1,234 reviews)" -> 1234)
   */
  protected cleanNumber(raw: string): number | undefined {
    if (!raw) return undefined;
    const match = raw.replace(/,/g, "").match(/([0-9]+(?:\.[0-9]+)?)/);
    if (match && match[1]) {
      const num = parseFloat(match[1]);
      return isNaN(num) ? undefined : num;
    }
    return undefined;
  }

  /**
   * Compute extraction quality confidence score (0.0 to 100.0)
   */
  protected calculateConfidence(card: Partial<ExtractedProductCard>): number {
    let score = 0;
    if (card.title && card.title !== "Unknown Product") score += 35;
    if (card.price && card.price > 0) score += 30;
    if (card.seller && card.seller !== "Unverified Seller") score += 20;
    if (card.image) score += 15;
    return Math.min(score, 100);
  }
}

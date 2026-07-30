/**
 * index.ts — Marketplace DOM Extraction Engine Registry & Factory
 * Extensible Adapter Pattern registry supporting Amazon, Flipkart, Myntra, AJIO, Meesho, TradeIndia.
 */

import { BaseParserAdapter } from "./base.adapter";
import { AmazonAdapter } from "./amazon.adapter";
import { FlipkartAdapter } from "./flipkart.adapter";
import { MyntraAdapter } from "./myntra.adapter";
import { AJIOAdapter } from "./ajio.adapter";
import { MeeshoAdapter } from "./meesho.adapter";
import { TradeIndiaAdapter } from "./tradeindia.adapter";
import { ExtractedProductCard } from "../types/productCard";
import { ExtensionLogger } from "../services/logger.service";

export class DomExtractionEngine {
  private static adapters: Map<string, BaseParserAdapter> = new Map();

  static {
    // Register standard marketplace parser adapters
    this.registerAdapter(new AmazonAdapter());
    this.registerAdapter(new FlipkartAdapter());
    this.registerAdapter(new MyntraAdapter());
    this.registerAdapter(new AJIOAdapter());
    this.registerAdapter(new MeeshoAdapter());
    this.registerAdapter(new TradeIndiaAdapter());
  }

  /**
   * Register a new marketplace parser adapter (Extensible Adapter Pattern)
   */
  static registerAdapter(adapter: BaseParserAdapter): void {
    this.adapters.set(adapter.marketplaceName.toLowerCase(), adapter);
    ExtensionLogger.info(`Registered parser adapter for marketplace: '${adapter.marketplaceName}'`);
  }

  /**
   * Primary DOM Extraction entry point
   */
  static extract(doc: Document, marketplace: string, url: string): ExtractedProductCard {
    const key = marketplace.toLowerCase();
    const adapter = this.adapters.get(key);

    if (adapter) {
      ExtensionLogger.info(`Executing DOM extraction adapter for '${adapter.marketplaceName}'...`);
      return adapter.parse(doc, url);
    }

    ExtensionLogger.warn(`No registered parser adapter for marketplace '${marketplace}'. Returning fallback.`);
    return {
      title: doc.title || "Generic Product Page",
      seller: "Unverified Seller",
      price: 0,
      currency: "INR",
      url,
      specifications: {},
      availability: "Unknown",
      marketplace: marketplace || "Unknown",
      extractedAt: new Date().toISOString(),
      confidenceScore: 10.0,
      failedSelectors: ["generic:no_adapter"],
    };
  }
}

export {
  BaseParserAdapter,
  AmazonAdapter,
  FlipkartAdapter,
  MyntraAdapter,
  AJIOAdapter,
  MeeshoAdapter,
  TradeIndiaAdapter,
};

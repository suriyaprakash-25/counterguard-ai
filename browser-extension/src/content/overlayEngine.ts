/**
 * overlayEngine.ts — High Performance Dynamic Overlay Engine
 * Per-Card Independent Analysis Architecture
 * Injects security badges ONLY after explicit backend response per card.
 * Zero default "Verified Authentic" badges.
 */

import { BadgeConfig, BadgeType, MarketplaceCardSelectorMap } from "../types/overlay";
import { ExtensionLogger } from "../services/logger.service";
import { BackendApiClient } from "../api/client";
import { ChromeStorageService } from "../services/storage.service";
import { BrowserAnalysisResponse } from "../types/api";

export interface ExtractedCardData {
  cardId: string;
  title: string;
  price: number;
  seller: string;
  url: string;
  marketplace: string;
}

export class OverlayEngine {
  private observer: MutationObserver | null = null;
  private cleanupObserver: IntersectionObserver | null = null;
  private processedElements: WeakSet<Element> = new WeakSet();
  private badgeMap: WeakMap<Element, HTMLElement> = new WeakMap();
  private elementByCardId: Map<string, Element> = new Map();

  /** Per-card analysis cache keyed by unique cardId (marketplace:productId) */
  private cardAnalysisCache: Map<string, BrowserAnalysisResponse> = new Map();
  /** Track currently pending card analyses to prevent duplicate network calls */
  private pendingAnalysis: Set<string> = new Set();

  private debounceTimer: number | null = null;
  private activeMarketplace: string = "Unknown";
  private isScanning: boolean = false;
  private injectedCount: number = 0;
  private backendBaseUrl: string = "http://localhost:8000";

  private static readonly BADGE_CONFIGS: Record<BadgeType, BadgeConfig> = {
    VERIFIED: {
      type: "VERIFIED",
      label: "Verified Authentic",
      icon: "🛡️",
      bgClass: "cg-badge-verified",
      borderClass: "border-emerald-500",
      textClass: "text-emerald-300",
      tooltipText: "CounterGuard Verified — Matches authorized brand registry & trusted distributor catalog.",
    },
    TRUSTED_SELLER: {
      type: "TRUSTED_SELLER",
      label: "Trusted Brand Seller",
      icon: "💎",
      bgClass: "cg-badge-trusted-seller",
      borderClass: "border-blue-500",
      textClass: "text-blue-300",
      tooltipText: "Authorized Seller — Verified official distributor with 98%+ customer satisfaction.",
    },
    SUSPICIOUS: {
      type: "SUSPICIOUS",
      label: "Suspicious Listing",
      icon: "⚠️",
      bgClass: "cg-badge-suspicious",
      borderClass: "border-amber-500",
      textClass: "text-amber-300",
      tooltipText: "Unverified Seller — Unusually low price variance detected. Exercise caution before purchasing.",
    },
    COUNTERFEIT_RISK: {
      type: "COUNTERFEIT_RISK",
      label: "High Counterfeit Risk",
      icon: "🚨",
      bgClass: "cg-badge-counterfeit-risk",
      borderClass: "border-red-500",
      textClass: "text-red-300",
      tooltipText: "High Counterfeit Risk — Probability > 85% of unauthorized replica or fake listing.",
    },
    RECOMMENDED: {
      type: "RECOMMENDED",
      label: "Recommended Takedown",
      icon: "⚡",
      bgClass: "cg-badge-recommended",
      borderClass: "border-purple-500",
      textClass: "text-purple-300",
      tooltipText: "Brand Infringement — Flagged for automated cease & desist takedown notice.",
    },
    OFFLINE: {
      type: "OFFLINE",
      label: "Offline Analysis",
      icon: "📡",
      bgClass: "cg-badge-offline",
      borderClass: "border-slate-500",
      textClass: "text-slate-300",
      tooltipText: "Offline Mode — Backend engine unreachable. Showing local fallback telemetry.",
    },
  };

  private static readonly SELECTOR_MAPS: Record<string, MarketplaceCardSelectorMap> = {
    amazon: {
      cardSelectors: [
        "div[data-component-type='s-search-result']",
        "div.s-result-item[data-asin]",
      ],
      titleSelectors: ["h2 a span", "span.a-size-medium", "#productTitle"],
      priceSelectors: ["span.a-price-whole", "span.a-offscreen"],
    },
    flipkart: {
      cardSelectors: [
        "div._1AtVbE",
        "div._75WgSt",
        "div[data-id]",
        "div.cPHRSc",
        "div.slrT20",
        "div._2kHMtA",
      ],
      titleSelectors: ["div._3pLy-c a", "a.s1Q98W", "span.VU-VGd", "div.KzBfdU", "a.IRwTfw"],
      priceSelectors: ["div._30jeq3", "div.Nx9bqj", "div._25bWAu"],
    },
    myntra: {
      cardSelectors: ["li.product-base"],
      titleSelectors: ["h3.product-brand", "h4.product-product"],
      priceSelectors: ["div.product-price", "span.product-discountedPrice"],
    },
    ajio: {
      cardSelectors: ["div.item", "div.rilrtl-products-list__item"],
      titleSelectors: ["div.nameCls", "div.brand"],
      priceSelectors: ["span.price", "div.prod-sp"],
    },
    meesho: {
      cardSelectors: ["div.ProductList__GridCol", "div.sc-dkzDqG"],
      titleSelectors: ["p.ProductTitle", "span.ProductTitle"],
      priceSelectors: ["h5.ProductPrice", "h4.ProductPrice__Price"],
    },
    tradeindia: {
      cardSelectors: ["div.product-card", "div.co-card"],
      titleSelectors: ["h2.title", "a.title"],
      priceSelectors: ["span.price", "div.price"],
    },
  };

  /**
   * Start Overlay Engine on target page
   */
  public async initialize(marketplace: string, rootDoc: Document = document): Promise<void> {
    this.activeMarketplace = marketplace.toLowerCase();
    this.injectedCount = 0;

    try {
      const settings = await ChromeStorageService.getSettings();
      if (settings?.backendUrl) {
        this.backendBaseUrl = settings.backendUrl;
      }
    } catch {
      // Default to http://localhost:8000
    }

    ExtensionLogger.info(`[OverlayEngine] Initialized per-card engine for '${marketplace}' connected to '${this.backendBaseUrl}'`);

    // Setup IntersectionObserver for auto-cleanup of off-screen badge elements
    if (typeof IntersectionObserver !== "undefined") {
      this.cleanupObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) {
              const badge = this.badgeMap.get(entry.target);
              if (badge && !badge.isConnected) {
                badge.remove();
                this.badgeMap.delete(entry.target);
              }
            }
          });
        },
        { threshold: 0 }
      );
    }

    // Initial scan
    this.scanAndInject(rootDoc);

    // Setup debounced MutationObserver for dynamic DOM loads (infinite scrolling)
    if (typeof MutationObserver !== "undefined") {
      this.observer = new MutationObserver(() => {
        this.debouncedScan(rootDoc);
      });

      this.observer.observe(rootDoc.body || rootDoc.documentElement, {
        childList: true,
        subtree: true,
      });
    }
  }

  private debouncedScan(rootDoc: Document): void {
    if (this.debounceTimer !== null) {
      clearTimeout(this.debounceTimer);
    }
    this.debounceTimer = window.setTimeout(() => {
      this.scanAndInject(rootDoc);
    }, 250);
  }

  /**
   * Primary Scan & Per-Card Analysis Engine
   */
  public scanAndInject(rootDoc: Document = document): void {
    if (this.isScanning) return;
    this.isScanning = true;

    try {
      const selectors = OverlayEngine.SELECTOR_MAPS[this.activeMarketplace] || OverlayEngine.SELECTOR_MAPS["flipkart"];

      selectors.cardSelectors.forEach((selector) => {
        const cardElements = rootDoc.querySelectorAll(selector);
        cardElements.forEach((cardEl) => {
          if (this.processedElements.has(cardEl)) return;

          // Extract per-card data
          const cardData = this.extractCardData(cardEl, selectors);
          if (!cardData.title || cardData.title === "Unknown Product") {
            // Ignore container wrapper elements that do not hold a distinct product title
            return;
          }

          this.processedElements.add(cardEl);
          cardEl.setAttribute("data-cg-card-id", cardData.cardId);
          this.elementByCardId.set(cardData.cardId, cardEl);

          // Check Cache
          if (this.cardAnalysisCache.has(cardData.cardId)) {
            const response = this.cardAnalysisCache.get(cardData.cardId)!;
            const badgeType = this.mapThreatToBadgeType(response.threat_level);
            this.injectBadge(cardEl, badgeType, response);
          } else if (!this.pendingAnalysis.has(cardData.cardId)) {
            // Dispatch asynchronous per-card backend threat analysis
            this.analyzeCardAsynchronously(cardEl, cardData);
          }
        });
      });
    } catch (err) {
      ExtensionLogger.error("[OverlayEngine] Error during scan and inject:", err);
    } finally {
      this.isScanning = false;
    }
  }

  /**
   * Extract product metadata for a specific card element
   */
  private extractCardData(cardEl: Element, selectors: MarketplaceCardSelectorMap): ExtractedCardData {
    let title = "";
    for (const ts of selectors.titleSelectors) {
      const el = cardEl.querySelector(ts);
      if (el?.textContent?.trim()) {
        title = el.textContent.trim();
        break;
      }
    }

    let rawPrice = "";
    for (const ps of selectors.priceSelectors) {
      const el = cardEl.querySelector(ps);
      if (el?.textContent?.trim()) {
        rawPrice = el.textContent.trim();
        break;
      }
    }

    const priceNum = rawPrice ? parseFloat(rawPrice.replace(/[^0-9.]/g, "")) || 0 : 0;
    const linkEl = cardEl.querySelector("a[href]") as HTMLAnchorElement | null;
    const productUrl = linkEl?.href || window.location.href;

    // Unique Card ID derivation
    const asinAttr = cardEl.getAttribute("data-asin") || cardEl.getAttribute("data-id");
    const uniqueSlug = asinAttr || productUrl || title;
    const cardId = `${this.activeMarketplace}:${this.hashString(uniqueSlug + "_" + title.slice(0, 30))}`;

    return {
      cardId,
      title: title || "Unknown Product",
      price: priceNum,
      seller: "Marketplace Seller",
      url: productUrl,
      marketplace: this.activeMarketplace,
    };
  }

  /**
   * Asynchronously analyze product card via POST /api/v1/browser/analyze
   */
  private async analyzeCardAsynchronously(cardEl: Element, cardData: ExtractedCardData): Promise<void> {
    this.pendingAnalysis.add(cardData.cardId);

    try {
      const response = await BackendApiClient.analyzeProductCard(this.backendBaseUrl, {
        title: cardData.title,
        seller: cardData.seller,
        price: cardData.price,
        currency: "INR",
        url: cardData.url,
        marketplace: cardData.marketplace,
      });

      this.cardAnalysisCache.set(cardData.cardId, response);
      const badgeType = this.mapThreatToBadgeType(response.threat_level);

      // Re-query element in case DOM re-rendered during network latency
      const targetElement = this.elementByCardId.get(cardData.cardId) || cardEl;
      if (targetElement && targetElement.isConnected) {
        this.injectBadge(targetElement, badgeType, response);
      }
    } catch (err) {
      ExtensionLogger.warn(`[OverlayEngine] Offline fallback for card '${cardData.cardId}':`, err);
      // Map to OFFLINE badge — NEVER display as Verified Authentic
      if (cardEl.isConnected) {
        this.injectBadge(cardEl, "OFFLINE");
      }
    } finally {
      this.pendingAnalysis.delete(cardData.cardId);
    }
  }

  /**
   * Map FastAPI threat_level → Overlay BadgeType
   */
  private mapThreatToBadgeType(threatLevel: string): BadgeType {
    switch (threatLevel?.toUpperCase()) {
      case "SAFE":
        return "VERIFIED";
      case "MEDIUM":
        return "SUSPICIOUS";
      case "HIGH":
      case "CRITICAL":
        return "COUNTERFEIT_RISK";
      default:
        return "SUSPICIOUS";
    }
  }

  /**
   * Inject non-intrusive badge container into target product card element.
   */
  private injectBadge(cardEl: Element, type: BadgeType, response?: BrowserAnalysisResponse): void {
    if (this.badgeMap.has(cardEl)) {
      // Remove existing container if re-rendering updated result
      const existing = this.badgeMap.get(cardEl);
      existing?.remove();
      this.badgeMap.delete(cardEl);
    }

    const config = OverlayEngine.BADGE_CONFIGS[type];
    const container = document.createElement("div");
    container.className = "cg-badge-container";
    container.setAttribute("aria-hidden", "true");
    container.setAttribute("role", "presentation");

    const badge = document.createElement("span");
    badge.className = `cg-badge ${config.bgClass}`;

    // Include live risk score in badge text if response present
    const scoreStr = response ? ` (${response.risk_score}/100)` : "";
    badge.innerHTML = `<span>${config.icon}</span><span>${config.label}${scoreStr}</span>`;

    const tooltip = document.createElement("div");
    tooltip.className = "cg-tooltip";
    tooltip.textContent = response?.recommendation || config.tooltipText;

    const tooltipId = `cg-tip-${this.injectedCount}`;
    tooltip.id = tooltipId;
    badge.setAttribute("aria-describedby", tooltipId);

    container.appendChild(badge);
    container.appendChild(tooltip);

    this.badgeMap.set(cardEl, container);
    this.injectedCount++;

    if (cardEl.firstChild) {
      cardEl.insertBefore(container, cardEl.firstChild);
    } else {
      cardEl.appendChild(container);
    }

    this.cleanupObserver?.observe(cardEl);
  }

  private hashString(str: string): string {
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = (hash << 5) - hash + str.charCodeAt(i);
      hash |= 0;
    }
    return Math.abs(hash).toString(36);
  }

  public cleanup(rootDoc: Document = document): void {
    if (this.observer) {
      this.observer.disconnect();
      this.observer = null;
    }
    if (this.cleanupObserver) {
      this.cleanupObserver.disconnect();
      this.cleanupObserver = null;
    }
    if (this.debounceTimer !== null) {
      clearTimeout(this.debounceTimer);
      this.debounceTimer = null;
    }
    rootDoc.querySelectorAll(".cg-badge-container").forEach((el) => el.remove());
    this.injectedCount = 0;
    this.cardAnalysisCache.clear();
    this.pendingAnalysis.clear();
    this.elementByCardId.clear();
    ExtensionLogger.info("[OverlayEngine] Cleaned up dynamic overlays and per-card cache.");
  }

  public getMetrics(): { injectedCount: number; marketplace: string; cachedCount: number } {
    return {
      injectedCount: this.injectedCount,
      marketplace: this.activeMarketplace,
      cachedCount: this.cardAnalysisCache.size,
    };
  }
}

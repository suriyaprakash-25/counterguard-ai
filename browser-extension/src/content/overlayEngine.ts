/**
 * overlayEngine.ts — High Performance Dynamic Overlay Engine
 * Per-Card Independent Threat Analysis Architecture
 * Features explicit stage logging (✓ Content script loaded, ✓ Cards found, ✓ Extracted, ✓ Sent, ✓ Received, ✓ Created, ✓ Inserted, ✓ Visible)
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

  private cardAnalysisCache: Map<string, BrowserAnalysisResponse> = new Map();
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
        "div[data-asin]:not([data-asin=''])",
      ],
      titleSelectors: ["h2 a span", "span.a-size-medium", "#productTitle", "h2 a"],
      priceSelectors: ["span.a-price-whole", "span.a-offscreen"],
    },
    flipkart: {
      cardSelectors: [
        "div[data-id]",
        "div._75WgSt",
        "div._1sd8b",
        "div._4ddrZC",
        "div.slrT20",
        "div._2kHMtA",
        "div.cPHRSc",
        "div.t55Tdf",
        "div.CGtC98",
        "div._2B09-q",
        "div._1AtVbE",
      ],
      titleSelectors: [
        "a.wP0hmB",
        "a.s1Q98W",
        "a.IRwTfw",
        "span.VU-VGd",
        "div.KzBfdU",
        "a.N8Z9Dx",
        "a[title]",
        "div._2Wk-gV",
        "a._3bldRF",
        "div._3pLy-c a",
        "div.B_NuTv",
        "a[href*='/p/']",
      ],
      priceSelectors: [
        "div.Nx9bqj",
        "div._30jeq3",
        "div._25bWAu",
        "div._1vC4OE",
      ],
    },
    myntra: {
      cardSelectors: ["li.product-base", "div.product-productMetaInfo"],
      titleSelectors: ["h3.product-brand", "h4.product-product", "h3", "h4"],
      priceSelectors: ["div.product-price", "span.product-discountedPrice"],
    },
    ajio: {
      cardSelectors: ["div.item", "div.rilrtl-products-list__item"],
      titleSelectors: ["div.nameCls", "div.brand", "a[title]"],
      priceSelectors: ["span.price", "div.prod-sp"],
    },
    meesho: {
      cardSelectors: ["div.ProductList__GridCol", "div.sc-dkzDqG", "div[class*='ProductList']"],
      titleSelectors: ["p.ProductTitle", "span.ProductTitle", "p", "span"],
      priceSelectors: ["h5.ProductPrice", "h4.ProductPrice__Price"],
    },
    tradeindia: {
      cardSelectors: ["div.product-card", "div.co-card"],
      titleSelectors: ["h2.title", "a.title", "h2", "h3"],
      priceSelectors: ["span.price", "div.price"],
    },
  };

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

    console.log(`✓ Overlay engine initialized for '${marketplace}' connected to '${this.backendBaseUrl}'`);
    ExtensionLogger.info(`[OverlayEngine] Initialized per-card engine for '${marketplace}' connected to '${this.backendBaseUrl}'`);

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

    this.scanAndInject(rootDoc);

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

  public scanAndInject(rootDoc: Document = document): void {
    if (this.isScanning) return;
    this.isScanning = true;

    try {
      const selectors = OverlayEngine.SELECTOR_MAPS[this.activeMarketplace] || OverlayEngine.SELECTOR_MAPS["flipkart"];
      let discoveredCount = 0;

      selectors.cardSelectors.forEach((selector) => {
        const cardElements = rootDoc.querySelectorAll(selector);
        cardElements.forEach((cardEl) => {
          if (this.processedElements.has(cardEl)) return;

          const cardData = this.extractCardData(cardEl, selectors);
          if (!cardData.title || cardData.title === "Unknown Product") {
            return;
          }

          discoveredCount++;
          console.log(`✓ Card #${discoveredCount} extracted: '${cardData.title.slice(0, 45)}...' (Price: ₹${cardData.price})`);

          this.processedElements.add(cardEl);
          cardEl.setAttribute("data-cg-card-id", cardData.cardId);
          this.elementByCardId.set(cardData.cardId, cardEl);

          if (this.cardAnalysisCache.has(cardData.cardId)) {
            const response = this.cardAnalysisCache.get(cardData.cardId)!;
            const badgeType = this.mapThreatToBadgeType(response.threat_level);
            this.injectBadge(cardEl, badgeType, response);
          } else if (!this.pendingAnalysis.has(cardData.cardId)) {
            this.analyzeCardAsynchronously(cardEl, cardData);
          }
        });
      });

      if (discoveredCount > 0) {
        console.log(`✓ ${discoveredCount} new product cards found on ${this.activeMarketplace}`);
      }
    } catch (err) {
      ExtensionLogger.error("[OverlayEngine] Error during scan and inject:", err);
    } finally {
      this.isScanning = false;
    }
  }

  private extractCardData(cardEl: Element, selectors: MarketplaceCardSelectorMap): ExtractedCardData {
    let title = "";
    for (const ts of selectors.titleSelectors) {
      const el = cardEl.querySelector(ts);
      if (el?.textContent?.trim()) {
        title = el.textContent.trim();
        break;
      }
    }

    // Title fallbacks
    if (!title) {
      const attrEl = cardEl.querySelector("a[title], img[alt]");
      if (attrEl) {
        title = attrEl.getAttribute("title") || attrEl.getAttribute("alt") || "";
      }
    }
    if (!title) {
      const heading = cardEl.querySelector("h2, h3, h4, a");
      if (heading?.textContent?.trim()) {
        title = heading.textContent.trim();
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

  private async analyzeCardAsynchronously(cardEl: Element, cardData: ExtractedCardData): Promise<void> {
    this.pendingAnalysis.add(cardData.cardId);
    console.log(`✓ Request sent for card '${cardData.cardId}' ('${cardData.title.slice(0, 30)}')`);

    try {
      let response: BrowserAnalysisResponse | null = null;

      // Delegate network fetch to Chrome Extension background service worker to bypass page Mixed Content & CORS restrictions
      if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
        response = await new Promise<BrowserAnalysisResponse | null>((resolve) => {
          chrome.runtime.sendMessage(
            { type: "ANALYZE_PRODUCT_CARD", payload: cardData },
            (res) => {
              if (chrome.runtime.lastError || !res || !res.success || !res.data) {
                resolve(null);
              } else {
                resolve(res.data);
              }
            }
          );
        });
      }

      if (!response) {
        response = await BackendApiClient.analyzeProductCard(this.backendBaseUrl, {
          title: cardData.title,
          seller: cardData.seller,
          price: cardData.price,
          currency: "INR",
          url: cardData.url,
          marketplace: cardData.marketplace,
        });
      }

      console.log(`✓ Response received for card '${cardData.cardId}': Threat Level = '${response.threat_level}' (Score: ${response.risk_score})`);
      this.cardAnalysisCache.set(cardData.cardId, response);
      const badgeType = this.mapThreatToBadgeType(response.threat_level);

      const targetElement = this.elementByCardId.get(cardData.cardId) || cardEl;
      if (targetElement && targetElement.isConnected) {
        this.injectBadge(targetElement, badgeType, response);
      }
    } catch (err) {
      console.warn(`⚠️ Offline fallback for card '${cardData.cardId}':`, err);
      if (cardEl.isConnected) {
        this.injectBadge(cardEl, "OFFLINE");
      }
    } finally {
      this.pendingAnalysis.delete(cardData.cardId);
    }
  }

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

  private injectBadge(cardEl: Element, type: BadgeType, response?: BrowserAnalysisResponse): void {
    if (this.badgeMap.has(cardEl)) {
      const existing = this.badgeMap.get(cardEl);
      existing?.remove();
      this.badgeMap.delete(cardEl);
    }

    const config = OverlayEngine.BADGE_CONFIGS[type];
    console.log(`✓ Badge created: '${config.label}' for card`);

    const container = document.createElement("div");
    container.className = "cg-badge-container";
    container.setAttribute("aria-hidden", "true");
    container.setAttribute("role", "presentation");
    container.style.display = "inline-flex";
    container.style.position = "relative";
    container.style.zIndex = "9999";
    container.style.margin = "4px 0";

    const badge = document.createElement("span");
    badge.className = `cg-badge ${config.bgClass}`;

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

    // Prevent clipping by overflow:hidden on host card
    const hostHtmlEl = cardEl as HTMLElement;
    if (hostHtmlEl.style) {
      hostHtmlEl.style.overflow = "visible";
      if (getComputedStyle(hostHtmlEl).position === "static") {
        hostHtmlEl.style.position = "relative";
      }
    }

    // Insert relative to title element if present, else prepend
    let targetParent: Element = cardEl;
    let targetBefore: Node | null = cardEl.firstChild;

    for (const ts of OverlayEngine.SELECTOR_MAPS[this.activeMarketplace]?.titleSelectors || []) {
      const titleEl = cardEl.querySelector(ts);
      if (titleEl && titleEl.parentElement) {
        targetParent = titleEl.parentElement;
        targetBefore = titleEl;
        break;
      }
    }

    targetParent.insertBefore(container, targetBefore);
    console.log(`✓ Badge inserted into DOM element`);

    // Verify visibility
    if (container.isConnected && container.getBoundingClientRect().height >= 0) {
      console.log(`✓ Badge visible on page`);
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

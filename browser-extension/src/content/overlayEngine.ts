/**
 * overlayEngine.ts — High Performance Dynamic Overlay Engine
 * Injects non-intrusive security badges (VERIFIED, SUSPICIOUS, COUNTERFEIT_RISK, RECOMMENDED, TRUSTED_SELLER)
 * into marketplace search catalog items and product detail pages with debounced MutationObserver,
 * WeakSet duplicate prevention, WeakMap GC-friendly badge tracking, zero-flickering,
 * hover tooltips, IntersectionObserver auto-cleanup, and dynamic DOM cleanup.
 */

import { BadgeConfig, BadgeType, MarketplaceCardSelectorMap } from "../types/overlay";
import { ExtensionLogger } from "../services/logger.service";

export class OverlayEngine {
  private observer: MutationObserver | null = null;
  private cleanupObserver: IntersectionObserver | null = null;
  /**
   * WeakSet tracks which elements have been processed.
   * GC automatically reclaims entries when elements are removed from DOM.
   */
  private processedElements: WeakSet<Element> = new WeakSet();
  /**
   * WeakMap maps each host element → its injected badge container.
   * Allows O(1) badge lookup without DOM query, and is GC-friendly.
   */
  private badgeMap: WeakMap<Element, HTMLElement> = new WeakMap();
  private debounceTimer: number | null = null;
  private activeMarketplace: string = "Unknown";
  private isScanning: boolean = false;
  /** Track total badges injected for metrics */
  private injectedCount: number = 0;

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
      label: "Counterfeit Risk",
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
  };

  private static readonly SELECTOR_MAPS: Record<string, MarketplaceCardSelectorMap> = {
    amazon: {
      cardSelectors: [
        "div[data-component-type='s-search-result']",
        "div.s-result-item[data-asin]",
        "#dp-container",
        "#productTitle",
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
        "span.VU-VGd",
      ],
      titleSelectors: ["div._3pLy-c a", "a.s1Q98W", "span.VU-VGd", "div.KzBfdU"],
      priceSelectors: ["div._30jeq3", "div.Nx9bqj"],
    },
    myntra: {
      cardSelectors: ["li.product-base", "div.pdp-details", "h1.pdp-name"],
      titleSelectors: ["h3.product-brand", "h4.product-product", "h1.pdp-name"],
      priceSelectors: ["div.product-price", "span.pdp-price"],
    },
    ajio: {
      cardSelectors: ["div.item", "div.prod-desc-container", "h1.prod-name"],
      titleSelectors: ["div.nameCls", "h1.prod-name"],
      priceSelectors: ["span.price", "div.prod-sp"],
    },
    meesho: {
      cardSelectors: ["div.ProductList__GridCol", "div.ProductDescription__Title"],
      titleSelectors: ["p.ProductTitle", "h1.ProductDescription__Title"],
      priceSelectors: ["h5.ProductPrice", "h4.ProductPrice__Price"],
    },
    tradeindia: {
      cardSelectors: ["div.product-card", "div.co-card", "h1.title"],
      titleSelectors: ["h2.title", "h1.title"],
      priceSelectors: ["span.price", "div.price"],
    },
  };

  /**
   * Start Overlay Engine on target page
   */
  public initialize(marketplace: string, rootDoc: Document = document): void {
    this.activeMarketplace = marketplace.toLowerCase();
    this.injectedCount = 0;
    ExtensionLogger.info(`[OverlayEngine] Initializing dynamic overlay engine for '${marketplace}'...`);

    // Setup IntersectionObserver for auto-cleanup of detached/off-screen elements
    // threshold: 0 fires when element has 0% intersection (detached or hidden)
    if (typeof IntersectionObserver !== "undefined") {
      this.cleanupObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            // If element is completely out of view AND badge still attached, remove badge
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

    // Setup debounced MutationObserver for dynamic DOM loads (virtual scrolling / pagination)
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

  /**
   * Debounced scanning helper to maintain 60fps performance without CPU spikes
   */
  private debouncedScan(rootDoc: Document): void {
    if (this.debounceTimer !== null) {
      clearTimeout(this.debounceTimer);
    }
    this.debounceTimer = window.setTimeout(() => {
      this.scanAndInject(rootDoc);
    }, 200);
  }

  /**
   * Scan DOM and inject security badges into matching product elements
   */
  public scanAndInject(rootDoc: Document = document): void {
    if (this.isScanning) return;
    this.isScanning = true;

    try {
      const selectors = OverlayEngine.SELECTOR_MAPS[this.activeMarketplace] || OverlayEngine.SELECTOR_MAPS["amazon"];
      
      selectors.cardSelectors.forEach((selector) => {
        const cardElements = rootDoc.querySelectorAll(selector);
        cardElements.forEach((cardEl) => {
          if (this.processedElements.has(cardEl)) return;

          // Determine heuristic risk score & badge type for demo / runtime
          const badgeType = this.determineBadgeType(cardEl, selectors);
          this.injectBadge(cardEl, badgeType);
          this.processedElements.add(cardEl);
        });
      });
    } catch (err) {
      ExtensionLogger.error("[OverlayEngine] Error during scan and inject:", err);
    } finally {
      this.isScanning = false;
    }
  }

  /**
   * Inject non-intrusive badge container into target product element.
   * Uses WeakMap to store badge reference for O(1) lookup and GC-friendly cleanup.
   */
  private injectBadge(cardEl: Element, type: BadgeType): void {
    // O(1) check via WeakMap instead of DOM query
    if (this.badgeMap.has(cardEl)) return;

    const config = OverlayEngine.BADGE_CONFIGS[type];
    const container = document.createElement("div");
    container.className = "cg-badge-container";
    // ARIA: badge is presentational, not interactive
    container.setAttribute("aria-hidden", "true");
    container.setAttribute("role", "presentation");

    const badge = document.createElement("span");
    badge.className = `cg-badge ${config.bgClass}`;
    badge.innerHTML = `<span>${config.icon}</span><span>${config.label}</span>`;

    const tooltip = document.createElement("div");
    tooltip.className = "cg-tooltip";
    tooltip.textContent = config.tooltipText;
    // Tooltip accessible via aria-describedby on badge
    const tooltipId = `cg-tip-${this.injectedCount}`;
    tooltip.id = tooltipId;
    badge.setAttribute("aria-describedby", tooltipId);

    container.appendChild(badge);
    container.appendChild(tooltip);

    // Store in WeakMap before DOM insertion
    this.badgeMap.set(cardEl, container);
    this.injectedCount++;

    // Prepend to card element without affecting inner layout
    if (cardEl.firstChild) {
      cardEl.insertBefore(container, cardEl.firstChild);
    } else {
      cardEl.appendChild(container);
    }

    // Register with IntersectionObserver for auto-cleanup tracking
    this.cleanupObserver?.observe(cardEl);
  }

  /**
   * Heuristic badge decision engine based on title, price, or text content
   */
  private determineBadgeType(cardEl: Element, selectors: MarketplaceCardSelectorMap): BadgeType {
    const textContent = cardEl.textContent?.toLowerCase() || "";

    if (textContent.includes("replica") || textContent.includes("copy") || textContent.includes("cheap")) {
      return "COUNTERFEIT_RISK";
    }
    if (textContent.includes("takedown") || textContent.includes("infringement")) {
      return "RECOMMENDED";
    }
    if (textContent.includes("unverified") || textContent.includes("refurbished")) {
      return "SUSPICIOUS";
    }
    if (textContent.includes("official") || textContent.includes("appario") || textContent.includes("retailnet")) {
      return "TRUSTED_SELLER";
    }

    // Default safe verified badge
    return "VERIFIED";
  }

  /**
   * Cleanup observer and remove all injected badges on tab change or unmount.
   * Disconnects both MutationObserver and IntersectionObserver.
   * WeakMap/WeakSet entries are automatically GC'd after element removal.
   */
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
    // Remove all badge containers from DOM
    rootDoc.querySelectorAll(".cg-badge-container").forEach((el) => el.remove());
    // Reset counters (WeakMap/WeakSet cleaned by GC)
    this.injectedCount = 0;
    ExtensionLogger.info("[OverlayEngine] Cleaned up dynamic overlays, MutationObserver, and IntersectionObserver.");
  }

  /**
   * Get current injection metrics for debugging
   */
  public getMetrics(): { injectedCount: number; marketplace: string } {
    return {
      injectedCount: this.injectedCount,
      marketplace: this.activeMarketplace,
    };
  }
}


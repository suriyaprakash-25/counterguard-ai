/**
 * overlay.ts — TypeScript type definitions for Chrome Extension Dynamic Overlay Engine
 */

export type BadgeType =
  | "VERIFIED"
  | "SUSPICIOUS"
  | "COUNTERFEIT_RISK"
  | "RECOMMENDED"
  | "TRUSTED_SELLER"
  | "OFFLINE";

export interface BadgeConfig {
  type: BadgeType;
  label: string;
  sublabel?: string;
  icon: string;
  bgClass: string;
  borderClass: string;
  textClass: string;
  tooltipText: string;
}

export interface MarketplaceCardSelectorMap {
  cardSelectors: string[];
  titleSelectors: string[];
  priceSelectors: string[];
}

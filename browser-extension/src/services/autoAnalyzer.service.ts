/**
 * autoAnalyzer.service.ts — Automatic Marketplace Page Analyzer Engine
 * Provides debouncing, request deduplication, Chrome storage cache management,
 * TTL cache invalidation, SPA route tracking, and infinite scrolling support.
 */

import { SecurityAnalysisResult } from "../types/extension";
import { ChromeStorageService } from "./storage.service";
import { ExtensionLogger } from "./logger.service";

interface CacheEntry {
  result: SecurityAnalysisResult;
  timestamp: number;
}

export class AutoAnalyzer {
  private static cache: Map<string, CacheEntry> = new Map();
  private static debounceTimers: Map<string, number> = new Map();
  private static DEFAULT_TTL_MS = 5 * 60 * 1000; // 5 minutes TTL

  /**
   * Check if a URL needs re-analysis (Returns false if cached within TTL)
   */
  static shouldAnalyze(url: string, ttlMs: number = this.DEFAULT_TTL_MS): boolean {
    if (!url) return false;
    const entry = this.cache.get(url);
    if (!entry) return true;

    const age = Date.now() - entry.timestamp;
    if (age > ttlMs) {
      ExtensionLogger.info(`[AutoAnalyzer] Cache expired for ${url} (Age: ${Math.round(age / 1000)}s)`);
      this.cache.delete(url);
      return true;
    }

    ExtensionLogger.debug(`[AutoAnalyzer] Cache hit for ${url} (Age: ${Math.round(age / 1000)}s)`);
    return false;
  }

  /**
   * Debounce analysis callback for a target URL
   */
  static debounce(url: string, callback: () => Promise<void>, delayMs: number = 750): void {
    const existingTimer = this.debounceTimers.get(url);
    if (existingTimer !== undefined) {
      clearTimeout(existingTimer);
    }

    const timer = setTimeout(async () => {
      this.debounceTimers.delete(url);
      try {
        await callback();
      } catch (err) {
        ExtensionLogger.error(`[AutoAnalyzer] Debounced execution failed for ${url}:`, err);
      }
    }, delayMs) as unknown as number;

    this.debounceTimers.set(url, timer);
  }


  /**
   * Cache analysis result in memory map and Chrome local storage
   */
  static async setCachedResult(url: string, domain: string, result: SecurityAnalysisResult): Promise<void> {
    if (!url) return;
    this.cache.set(url, {
      result,
      timestamp: Date.now(),
    });
    if (domain) {
      await ChromeStorageService.setLastAnalysis(domain, result);
    }
    ExtensionLogger.info(`[AutoAnalyzer] Cached analysis result for ${url}`);
  }

  /**
   * Get cached result if available and valid
   */
  static getCachedResult(url: string, ttlMs: number = this.DEFAULT_TTL_MS): SecurityAnalysisResult | null {
    if (!url) return null;
    const entry = this.cache.get(url);
    if (!entry) return null;

    if (Date.now() - entry.timestamp > ttlMs) {
      this.cache.delete(url);
      return null;
    }
    return entry.result;
  }

  /**
   * Invalidate cache for a single URL or clear all cache
   */
  static invalidateCache(url?: string): void {
    if (url) {
      this.cache.delete(url);
      const timer = this.debounceTimers.get(url);
      if (timer !== undefined) {
        clearTimeout(timer);
        this.debounceTimers.delete(url);
      }
      ExtensionLogger.info(`[AutoAnalyzer] Invalidated cache for ${url}`);
    } else {
      this.cache.clear();
      this.debounceTimers.forEach((timer) => clearTimeout(timer));
      this.debounceTimers.clear();
      ExtensionLogger.info("[AutoAnalyzer] Cleared entire analysis cache.");
    }
  }

  /**
   * Get total cached URLs count
   */
  static getCacheSize(): number {
    return this.cache.size;
  }
}

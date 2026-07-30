import { describe, it, expect, beforeEach, vi } from "vitest";
import { AutoAnalyzer } from "../autoAnalyzer.service";
import { SecurityAnalysisResult } from "../../types/extension";

describe("AutoAnalyzer Unit Test Suite", () => {
  beforeEach(() => {
    AutoAnalyzer.invalidateCache();
    vi.useRealTimers();
  });

  it("returns true for unanalyzed URL and false once cached within TTL", async () => {
    const url = "https://www.amazon.in/dp/B0CX237A12";
    expect(AutoAnalyzer.shouldAnalyze(url)).toBe(true);

    const mockResult: SecurityAnalysisResult = {
      marketplace: "Amazon",
      threatLevel: "SAFE",
      threatScore: 10,
      verdict: "CLEAN",
      matchedListingsCount: 0,
      confidenceScore: 95,
      analyzedAt: new Date().toISOString(),
      findings: [],
    };

    await AutoAnalyzer.setCachedResult(url, "amazon.in", mockResult);
    expect(AutoAnalyzer.shouldAnalyze(url)).toBe(false);
    expect(AutoAnalyzer.getCachedResult(url)).toEqual(mockResult);
  });

  it("debounces rapid duplicate calls for the same URL", async () => {
    vi.useFakeTimers();
    const url = "https://www.flipkart.com/search?q=earbuds";
    const callback = vi.fn().mockResolvedValue(undefined);

    AutoAnalyzer.debounce(url, callback, 500);
    AutoAnalyzer.debounce(url, callback, 500);
    AutoAnalyzer.debounce(url, callback, 500);

    expect(callback).not.toHaveBeenCalled();

    vi.advanceTimersByTime(600);
    expect(callback).toHaveBeenCalledTimes(1);
  });

  it("invalidates cache for specific URL", async () => {
    const url = "https://www.myntra.com/shoes/24589210/buy";
    const mockResult: SecurityAnalysisResult = {
      marketplace: "Myntra",
      threatLevel: "SAFE",
      threatScore: 5,
      verdict: "CLEAN",
      matchedListingsCount: 0,
      confidenceScore: 98,
      analyzedAt: new Date().toISOString(),
      findings: [],
    };

    await AutoAnalyzer.setCachedResult(url, "myntra.com", mockResult);
    expect(AutoAnalyzer.getCacheSize()).toBe(1);

    AutoAnalyzer.invalidateCache(url);
    expect(AutoAnalyzer.getCacheSize()).toBe(0);
    expect(AutoAnalyzer.shouldAnalyze(url)).toBe(true);
  });

  it("clears entire cache when invalidateCache() is called with no args", async () => {
    const mockResult: SecurityAnalysisResult = {
      marketplace: "AJIO",
      threatLevel: "SAFE",
      threatScore: 5,
      verdict: "CLEAN",
      matchedListingsCount: 0,
      confidenceScore: 98,
      analyzedAt: new Date().toISOString(),
      findings: [],
    };

    await AutoAnalyzer.setCachedResult("https://www.ajio.com/p/1", "ajio.com", mockResult);
    await AutoAnalyzer.setCachedResult("https://www.ajio.com/p/2", "ajio.com", mockResult);
    expect(AutoAnalyzer.getCacheSize()).toBe(2);

    AutoAnalyzer.invalidateCache();
    expect(AutoAnalyzer.getCacheSize()).toBe(0);
  });
});

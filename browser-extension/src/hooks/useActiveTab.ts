import { useState, useEffect } from "react";
import { PageMetadata } from "../types/extension";
import { MarketplaceDetector } from "../services/marketplaceDetector.service";

export function useActiveTab() {
  const [page, setPage] = useState<PageMetadata | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    if (typeof chrome !== "undefined" && chrome.tabs && chrome.tabs.query) {
      chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
        const activeTab = tabs[0];
        if (activeTab && activeTab.url) {
          try {
            const urlObj = new URL(activeTab.url);
            const host = urlObj.hostname.replace(/^www\./, "");
            const detection = MarketplaceDetector.detect(activeTab.url);

            setPage({
              url: activeTab.url,
              domain: host,
              title: activeTab.title || host,
              faviconUrl: activeTab.favIconUrl,
              isSupportedMarketplace: detection.isMarketplace,
              marketplaceName: detection.isMarketplace ? detection.marketplace : undefined,
              isSecure: urlObj.protocol === "https:",
              detection: detection,
            });
          } catch {
            setPage(null);
          }
        }
        setLoading(false);
      });
    } else {
      // Mock fallback for browser dev environment
      const mockUrl = "https://www.amazon.in/dp/B0CX237A12";
      const detection = MarketplaceDetector.detect(mockUrl);
      setPage({
        url: mockUrl,
        domain: "amazon.in",
        title: "Sony WH-1000XM5 Wireless Headphones — Amazon.in",
        faviconUrl: "https://www.amazon.in/favicon.ico",
        isSupportedMarketplace: true,
        marketplaceName: "Amazon",
        isSecure: true,
        detection: detection,
      });
      setLoading(false);
    }
  }, []);

  return { page, loading };
}


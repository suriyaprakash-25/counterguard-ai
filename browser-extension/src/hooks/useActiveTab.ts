import { useState, useEffect } from "react";
import { PageMetadata } from "../types/extension";
import { MarketplaceDetector } from "../services/marketplaceDetector.service";

export function useActiveTab() {
  const [page, setPage] = useState<PageMetadata | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);

    const processTab = (activeTab?: chrome.tabs.Tab) => {
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
      } else {
        setPage(null);
      }
      setLoading(false);
    };

    if (typeof chrome !== "undefined" && chrome.tabs && chrome.tabs.query) {
      try {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
          if (chrome.runtime.lastError || !tabs || tabs.length === 0) {
            chrome.tabs.query({ active: true, lastFocusedWindow: true }, (fallbackTabs) => {
              processTab(fallbackTabs ? fallbackTabs[0] : undefined);
            });
          } else {
            processTab(tabs[0]);
          }
        });
      } catch (err) {
        console.warn("[useActiveTab] Query error:", err);
        setLoading(false);
      }
    } else {
      const currentUrl = typeof window !== "undefined" ? window.location.href : "about:blank";
      try {
        const urlObj = new URL(currentUrl);
        const host = urlObj.hostname.replace(/^www\./, "");
        const detection = MarketplaceDetector.detect(currentUrl);
        setPage({
          url: currentUrl,
          domain: host,
          title: typeof document !== "undefined" ? document.title || host : host,
          faviconUrl: undefined,
          isSupportedMarketplace: detection.isMarketplace,
          marketplaceName: detection.isMarketplace ? detection.marketplace : undefined,
          isSecure: urlObj.protocol === "https:",
          detection: detection,
        });
      } catch {
        setPage(null);
      }
      setLoading(false);
    }
  }, []);

  return { page, loading };
}

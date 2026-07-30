/**
 * useActiveTab.ts — Active Tab URL & Metadata inspector hook
 */

import { useState, useEffect } from "react";
import { PageMetadata } from "../types/extension";

const SUPPORTED_MARKETPLACES = [
  "amazon", "flipkart", "tradeindia", "myntra", "meesho", "ajio", "ebay", "aliexpress"
];

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
            
            const matchedMp = SUPPORTED_MARKETPLACES.find(mp => host.toLowerCase().includes(mp));
            
            setPage({
              url: activeTab.url,
              domain: host,
              title: activeTab.title || host,
              faviconUrl: activeTab.favIconUrl,
              isSupportedMarketplace: Boolean(matchedMp),
              marketplaceName: matchedMp ? matchedMp.charAt(0).toUpperCase() + matchedMp.slice(1) : undefined,
              isSecure: urlObj.protocol === "https:",
            });
          } catch {
            setPage(null);
          }
        }
        setLoading(false);
      });
    } else {
      // Mock fallback for browser dev environment
      setPage({
        url: "https://www.amazon.in/dp/B0CX237A12",
        domain: "amazon.in",
        title: "Sony WH-1000XM5 Wireless Headphones — Amazon.in",
        faviconUrl: "https://www.amazon.in/favicon.ico",
        isSupportedMarketplace: true,
        marketplaceName: "Amazon",
        isSecure: true,
      });
      setLoading(false);
    }
  }, []);

  return { page, loading };
}

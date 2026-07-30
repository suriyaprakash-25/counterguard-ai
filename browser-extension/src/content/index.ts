/**
 * content/index.ts — CounterGuard Extension Content Script
 * Injected into active web pages. Detects marketplaces and launches Dynamic Overlay Engine.
 */

import { ExtensionLogger } from "../services/logger.service";
import { MarketplaceDetector } from "../services/marketplaceDetector.service";
import { OverlayEngine } from "./overlayEngine";
import "../styles/overlay.css";

ExtensionLogger.info(`[ContentScript] CounterGuard initialized on: ${window.location.href}`);

const detection = MarketplaceDetector.detect(window.location.href);
let overlayEngine: OverlayEngine | null = null;

if (detection.isMarketplace) {
  ExtensionLogger.info(`[ContentScript] Marketplace detected: '${detection.marketplace}' (Page: ${detection.pageType})`);
  overlayEngine = new OverlayEngine();
  overlayEngine.initialize(detection.marketplace);
}

// Register listener for messages from extension popup / background worker
if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    ExtensionLogger.debug("[ContentScript] Received runtime message:", message);
    
    if (message.type === "PING_CONTENT") {
      sendResponse({
        success: true,
        url: window.location.href,
        title: document.title,
        detection: detection,
      });
    } else if (message.type === "TRIGGER_OVERLAY_SCAN" && overlayEngine) {
      overlayEngine.scanAndInject();
      sendResponse({ success: true });
    }
  });
}

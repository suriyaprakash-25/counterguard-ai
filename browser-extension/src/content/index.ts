/**
 * content/index.ts — CounterGuard Extension Content Script
 * Injected into active web pages. Detects marketplaces and launches Dynamic Overlay Engine.
 *
 * CSS is injected programmatically (not imported) because this file is built as an IIFE.
 * Chrome content scripts loaded as plain scripts cannot use ES import syntax.
 */

import { ExtensionLogger } from "../services/logger.service";
import { MarketplaceDetector } from "../services/marketplaceDetector.service";
import { OverlayEngine } from "./overlayEngine";

/**
 * Inject overlay badge styles into the page.
 * Done via a <style> element so no external CSS file loading is needed.
 */
function injectOverlayStyles(): void {
  if (document.getElementById('cg-overlay-styles')) return; // Already injected
  const style = document.createElement('style');
  style.id = 'cg-overlay-styles';
  style.textContent = `
.cg-badge-container{display:inline-flex;align-items:center;position:relative;z-index:9999;margin:6px 0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;user-select:none}
.cg-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 8px;border-radius:6px;font-size:11px;font-weight:700;line-height:1.2;letter-spacing:.02em;box-shadow:0 2px 8px rgba(0,0,0,.2);backdrop-filter:blur(8px);transition:all .2s cubic-bezier(.4,0,.2,1);cursor:pointer}
.cg-badge:hover{transform:translateY(-1px) scale(1.03);box-shadow:0 4px 12px rgba(0,0,0,.3)}
.cg-badge-verified{background:rgba(6,78,59,.9);border:1px solid rgba(16,185,129,.6);color:#a7f3d0}
.cg-badge-trusted-seller{background:rgba(30,58,138,.9);border:1px solid rgba(59,130,246,.6);color:#bfdbfe}
.cg-badge-suspicious{background:rgba(120,53,15,.9);border:1px solid rgba(245,158,11,.6);color:#fef08a}
.cg-badge-counterfeit-risk{background:rgba(127,29,29,.95);border:1px solid rgba(239,68,68,.7);color:#fca5a5;animation:cg-pulse 2s cubic-bezier(.4,0,.6,1) infinite}
.cg-badge-recommended{background:rgba(88,28,135,.95);border:1px solid rgba(168,85,247,.7);color:#e9d5ff}
.cg-badge-offline{background:rgba(51,65,85,.9);border:1px dashed rgba(148,163,184,.6);color:#cbd5e1}
.cg-tooltip{visibility:hidden;opacity:0;position:absolute;bottom:125%;left:50%;transform:translateX(-50%) translateY(4px);width:220px;background:#0f172a;border:1px solid #334155;color:#f8fafc;padding:8px 10px;border-radius:8px;font-size:10px;font-weight:500;line-height:1.4;box-shadow:0 10px 25px -5px rgba(0,0,0,.5);pointer-events:none;transition:all .2s ease-in-out;z-index:10000}
.cg-badge-container:hover .cg-tooltip{visibility:visible;opacity:1;transform:translateX(-50%) translateY(0)}
@keyframes cg-pulse{0%,100%{opacity:1;box-shadow:0 0 0 0 rgba(239,68,68,.4)}50%{opacity:.85;box-shadow:0 0 0 6px rgba(239,68,68,0)}}
`;
  (document.head || document.documentElement).appendChild(style);
}

console.log("✓ Content script loaded on:", window.location.href);
ExtensionLogger.info(`[ContentScript] CounterGuard initialized on: ${window.location.href}`);

// Inject badge styles before overlay engine runs
injectOverlayStyles();

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

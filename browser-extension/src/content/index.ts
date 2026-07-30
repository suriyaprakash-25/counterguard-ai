/**
 * content/index.ts — CounterGuard Extension Content Script
 * Injected into active web pages. Cleanly registered for DOM inspection & runtime messaging.
 */

import { ExtensionLogger } from "../services/logger.service";

ExtensionLogger.info(`Content Script initialized on: ${window.location.href}`);

// Register listener for messages from extension popup / background worker
if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.onMessage) {
  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    ExtensionLogger.debug("Content script received message:", message);
    if (message.type === "PING_CONTENT") {
      sendResponse({ success: true, url: window.location.href, title: document.title });
    }
  });
}

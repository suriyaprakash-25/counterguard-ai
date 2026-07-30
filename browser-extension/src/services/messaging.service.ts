/**
 * messaging.service.ts — Chrome Runtime Messaging Wrapper
 */

import { ExtensionMessage, MessageResponse } from "../types/extension";
import { ExtensionLogger } from "./logger.service";

export class ExtensionMessagingService {
  /**
   * Send a message to the Background Service Worker
   */
  static async sendMessageToBackground<T, R>(message: ExtensionMessage<T>): Promise<MessageResponse<R>> {
    return new Promise((resolve) => {
      if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.sendMessage) {
        chrome.runtime.sendMessage(message, (response: MessageResponse<R>) => {
          if (chrome.runtime.lastError) {
            ExtensionLogger.warn("Messaging error:", chrome.runtime.lastError.message);
            resolve({
              success: false,
              error: chrome.runtime.lastError.message,
            });
            return;
          }
          resolve(response || { success: true });
        });
      } else {
        ExtensionLogger.info("Non-extension context: Message simulated", message);
        resolve({ success: true });
      }
    });
  }

  /**
   * Send a message to a active tab's Content Script
   */
  static async sendMessageToTab<T, R>(tabId: number, message: ExtensionMessage<T>): Promise<MessageResponse<R>> {
    return new Promise((resolve) => {
      if (typeof chrome !== "undefined" && chrome.tabs && chrome.tabs.sendMessage) {
        chrome.tabs.sendMessage(tabId, message, (response: MessageResponse<R>) => {
          if (chrome.runtime.lastError) {
            ExtensionLogger.warn(`Tab messaging error for tab ${tabId}:`, chrome.runtime.lastError.message);
            resolve({
              success: false,
              error: chrome.runtime.lastError.message,
            });
            return;
          }
          resolve(response || { success: true });
        });
      } else {
        resolve({ success: true });
      }
    });
  }
}

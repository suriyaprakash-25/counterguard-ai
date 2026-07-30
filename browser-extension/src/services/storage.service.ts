/**
 * storage.service.ts — Chrome Storage API wrapper with fallback & strict types
 */

import { ExtensionSettings, SecurityAnalysisResult } from "../types/extension";
import { ExtensionLogger } from "./logger.service";

export const DEFAULT_SETTINGS: ExtensionSettings = {
  backendUrl: "http://localhost:8000",
  apiKey: "",                  // Empty = development/no-auth mode. Set in Options page for production.
  autoAnalyze: true,
  lightMode: false,
  notifications: true,
  theme: "dark",
};

export class ChromeStorageService {
  /**
   * Fetch extension settings from chrome.storage.sync or fallback
   */
  static async getSettings(): Promise<ExtensionSettings> {
    return new Promise((resolve) => {
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.sync) {
        chrome.storage.sync.get(["cg_settings"], (result) => {
          if (chrome.runtime.lastError) {
            ExtensionLogger.error("Failed to read settings from storage:", chrome.runtime.lastError);
            resolve(DEFAULT_SETTINGS);
            return;
          }
          const stored = result.cg_settings as Partial<ExtensionSettings> | undefined;
          resolve({ ...DEFAULT_SETTINGS, ...stored });
        });
      } else {
        // Fallback for non-extension environment
        try {
          const raw = localStorage.getItem("cg_settings");
          if (raw) {
            resolve({ ...DEFAULT_SETTINGS, ...JSON.parse(raw) });
          } else {
            resolve(DEFAULT_SETTINGS);
          }
        } catch {
          resolve(DEFAULT_SETTINGS);
        }
      }
    });
  }

  /**
   * Save extension settings to chrome.storage.sync
   */
  static async saveSettings(settings: ExtensionSettings): Promise<boolean> {
    return new Promise((resolve) => {
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.sync) {
        chrome.storage.sync.set({ cg_settings: settings }, () => {
          if (chrome.runtime.lastError) {
            ExtensionLogger.error("Failed to save settings:", chrome.runtime.lastError);
            resolve(false);
            return;
          }
          ExtensionLogger.info("Extension settings saved to Chrome Sync Storage.");
          resolve(true);
        });
      } else {
        try {
          localStorage.setItem("cg_settings", JSON.stringify(settings));
          resolve(true);
        } catch {
          resolve(false);
        }
      }
    });
  }

  /**
   * Store recent analysis result in chrome.storage.local
   */
  static async setLastAnalysis(domain: string, result: SecurityAnalysisResult): Promise<void> {
    return new Promise((resolve) => {
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
        const key = `cg_analysis_${domain}`;
        chrome.storage.local.set({ [key]: result }, () => {
          resolve();
        });
      } else {
        try {
          localStorage.setItem(`cg_analysis_${domain}`, JSON.stringify(result));
        } catch {
          // ignore
        }
        resolve();
      }
    });
  }

  /**
   * Fetch recent analysis result for a domain
   */
  static async getLastAnalysis(domain: string): Promise<SecurityAnalysisResult | null> {
    return new Promise((resolve) => {
      if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
        const key = `cg_analysis_${domain}`;
        chrome.storage.local.get([key], (data) => {
          resolve((data[key] as SecurityAnalysisResult) || null);
        });
      } else {
        try {
          const raw = localStorage.getItem(`cg_analysis_${domain}`);
          resolve(raw ? JSON.parse(raw) : null);
        } catch {
          resolve(null);
        }
      }
    });
  }
}

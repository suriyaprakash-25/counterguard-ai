/**
 * history.service.ts — Chrome Storage Investigation History Management
 * Manages persistent investigation records, search filtering, deletion, and export.
 */

import { ExtensionLogger } from "./logger.service";

export interface InvestigationHistoryItem {
  id: string;
  investigationId: string;
  evidenceId: string;
  productTitle: string;
  sellerName: string;
  marketplace: string;
  riskScore: number;
  threatLevel: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE";
  recommendation: string;
  url: string;
  timestamp: string;
}

const HISTORY_STORAGE_KEY = "counterguard_investigation_history";
const MAX_HISTORY_ITEMS = 100;

export class HistoryService {
  private static inMemoryHistory: InvestigationHistoryItem[] = [];

  /**
   * Fetch all investigation history items from chrome.storage.local
   */
  static async getHistory(): Promise<InvestigationHistoryItem[]> {
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      try {
        const result = await chrome.storage.local.get([HISTORY_STORAGE_KEY]);
        this.inMemoryHistory = result[HISTORY_STORAGE_KEY] || [];
      } catch (err) {
        ExtensionLogger.error("Failed to load history from Chrome Storage:", err);
      }
    }
    return [...this.inMemoryHistory];
  }

  /**
   * Add a new investigation record to persistent storage
   */
  static async addRecord(item: Omit<InvestigationHistoryItem, "id" | "timestamp">): Promise<InvestigationHistoryItem> {
    const history = await this.getHistory();

    const newRecord: InvestigationHistoryItem = {
      ...item,
      id: `hist-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 6)}`,
      timestamp: new Date().toISOString(),
    };

    // Deduplicate identical active investigation IDs
    const filtered = history.filter((h) => h.investigationId !== newRecord.investigationId);
    const updatedHistory = [newRecord, ...filtered].slice(0, MAX_HISTORY_ITEMS);

    this.inMemoryHistory = updatedHistory;

    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      try {
        await chrome.storage.local.set({ [HISTORY_STORAGE_KEY]: updatedHistory });
        ExtensionLogger.info(`[HistoryService] Saved investigation record ${newRecord.investigationId}`);
      } catch (err) {
        ExtensionLogger.error("Failed to save record to Chrome Storage:", err);
      }
    }

    return newRecord;
  }

  /**
   * Delete an individual investigation record by ID
   */
  static async deleteRecord(id: string): Promise<boolean> {
    const history = await this.getHistory();
    const updatedHistory = history.filter((item) => item.id !== id && item.investigationId !== id);

    this.inMemoryHistory = updatedHistory;

    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      try {
        await chrome.storage.local.set({ [HISTORY_STORAGE_KEY]: updatedHistory });
        ExtensionLogger.info(`[HistoryService] Deleted record ${id}`);
        return true;
      } catch (err) {
        ExtensionLogger.error(`Failed to delete record ${id}:`, err);
        return false;
      }
    }
    return true;
  }

  /**
   * Clear all stored investigation history
   */
  static async clearHistory(): Promise<boolean> {
    this.inMemoryHistory = [];
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.local) {
      try {
        await chrome.storage.local.remove([HISTORY_STORAGE_KEY]);
        ExtensionLogger.info("[HistoryService] Cleared entire investigation history.");
        return true;
      } catch (err) {
        ExtensionLogger.error("Failed to clear history:", err);
        return false;
      }
    }
    return true;
  }

  /**
   * Format history items as JSON string for file export
   */
  static exportHistoryJson(items: InvestigationHistoryItem[]): string {
    return JSON.stringify(
      {
        exported_at: new Date().toISOString(),
        total_records: items.length,
        records: items,
      },
      null,
      2
    );
  }
}

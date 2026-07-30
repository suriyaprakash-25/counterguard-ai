/**
 * useChromeStorage.ts — Reactive Chrome Storage settings hook
 */

import { useState, useEffect, useCallback } from "react";
import { ExtensionSettings } from "../types/extension";
import { ChromeStorageService, DEFAULT_SETTINGS } from "../services/storage.service";

export function useChromeStorage() {
  const [settings, setSettings] = useState<ExtensionSettings>(DEFAULT_SETTINGS);
  const [loading, setLoading] = useState(true);

  const loadSettings = useCallback(async () => {
    setLoading(true);
    const loaded = await ChromeStorageService.getSettings();
    setSettings(loaded);
    setLoading(false);
  }, []);

  useEffect(() => {
    loadSettings();

    // Listen for storage changes in Chrome Extension runtime
    if (typeof chrome !== "undefined" && chrome.storage && chrome.storage.onChanged) {
      const handleStorageChange = (
        changes: { [key: string]: chrome.storage.StorageChange },
        areaName: string
      ) => {
        if (areaName === "sync" && changes.cg_settings) {
          const updated = changes.cg_settings.newValue as ExtensionSettings;
          if (updated) {
            setSettings(updated);
          }
        }
      };

      chrome.storage.onChanged.addListener(handleStorageChange);
      return () => {
        chrome.storage.onChanged.removeListener(handleStorageChange);
      };
    }
    return undefined;
  }, [loadSettings]);

  const updateSettings = async (newSettings: Partial<ExtensionSettings>): Promise<boolean> => {
    const merged = { ...settings, ...newSettings };
    setSettings(merged);
    return await ChromeStorageService.saveSettings(merged);
  };

  return { settings, updateSettings, loading, reloadSettings: loadSettings };
}

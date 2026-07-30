/**
 * useOfflineMode.ts — Reactive offline/online network state hook
 * Monitors navigator.onLine and window online/offline events.
 * Returns real-time connectivity status for the popup UI.
 */

import { useState, useEffect } from "react";

export interface OfflineModeState {
  isOffline: boolean;
  wasOffline: boolean; // True if went offline at least once this session
}

export function useOfflineMode(): OfflineModeState {
  const [isOffline, setIsOffline] = useState<boolean>(!navigator.onLine);
  const [wasOffline, setWasOffline] = useState<boolean>(!navigator.onLine);

  useEffect(() => {
    const handleOnline = () => {
      setIsOffline(false);
    };

    const handleOffline = () => {
      setIsOffline(true);
      setWasOffline(true);
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    // Re-check on mount in case state changed between render cycles
    if (!navigator.onLine) {
      setIsOffline(true);
      setWasOffline(true);
    }

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return { isOffline, wasOffline };
}

import { useState, useCallback } from "react";

export function usePolling(defaultInterval: number = 30000) {
  const [isPolling, setIsPolling] = useState(false);
  const [pollingInterval, setPollingInterval] = useState(defaultInterval);

  const startPolling = useCallback(() => setIsPolling(true), []);
  const stopPolling = useCallback(() => setIsPolling(false), []);
  const togglePolling = useCallback(() => setIsPolling(prev => !prev), []);

  return {
    isPolling,
    pollingInterval,
    setPollingInterval,
    startPolling,
    stopPolling,
    togglePolling
  };
}

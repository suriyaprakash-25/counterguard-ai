import { useQuery } from "@tanstack/react-query";
import { alertsService } from "../services/alerts.service";
import { usePolling } from "../../../hooks/usePolling";

export const useAlerts = () => {
  const { isPolling, pollingInterval } = usePolling(30000); // 30s polling

  return useQuery({
    queryKey: ["alerts", "list"],
    queryFn: alertsService.getAlerts,
    refetchInterval: isPolling ? pollingInterval : false
  });
};

export const useAlertDetails = (id: string | null) => {
  return useQuery({
    queryKey: ["alerts", "details", id],
    queryFn: () => alertsService.getAlertDetails(id!),
    enabled: !!id
  });
};

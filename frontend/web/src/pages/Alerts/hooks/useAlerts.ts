import { useQuery } from "@tanstack/react-query";
import { AlertsRepository } from "../services/alerts.repository";

export const useAlerts = () => {
  return useQuery({
    queryKey: ["alerts", "list"],
    queryFn: AlertsRepository.getAlerts
  });
};

export const useAlertDetails = (id: string) => {
  return useQuery({
    queryKey: ["alerts", "details", id],
    queryFn: () => AlertsRepository.getAlertDetails(id),
    enabled: !!id
  });
};

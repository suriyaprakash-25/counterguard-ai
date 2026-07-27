import { useQuery } from "@tanstack/react-query";
import { AnalyticsRepository } from "../services/analytics.repository";

export const useAnalytics = () => {
  return useQuery({
    queryKey: ["analytics", "dashboard"],
    queryFn: AnalyticsRepository.getAnalytics
  });
};

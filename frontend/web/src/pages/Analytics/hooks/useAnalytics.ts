import { useQuery } from "@tanstack/react-query";
import { analyticsService } from "../services/analytics.service";

export const useAnalytics = () => {
  return useQuery({
    queryKey: ["analytics", "dashboard"],
    queryFn: analyticsService.getAnalytics
  });
};

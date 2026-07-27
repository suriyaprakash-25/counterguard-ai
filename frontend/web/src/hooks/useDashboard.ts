import { useQuery } from "@tanstack/react-query";
import { dashboardService } from "../services/dashboard";

export const useDashboardSummary = () => {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: dashboardService.getSummary,
  });
};

export const useRecentInvestigations = () => {
  return useQuery({
    queryKey: ["dashboard", "recent-investigations"],
    queryFn: dashboardService.getRecentInvestigations,
  });
};

export const useRecentAlerts = () => {
  return useQuery({
    queryKey: ["dashboard", "recent-alerts"],
    queryFn: dashboardService.getRecentAlerts,
  });
};

export const useMarketplaceMetrics = () => {
  return useQuery({
    queryKey: ["dashboard", "marketplace-metrics"],
    queryFn: dashboardService.getMarketplaceMetrics,
  });
};

export const useRiskTrend = () => {
  return useQuery({
    queryKey: ["dashboard", "risk-trend"],
    queryFn: dashboardService.getRiskTrend,
  });
};

export const useSystemHealth = () => {
  return useQuery({
    queryKey: ["dashboard", "system-health"],
    queryFn: dashboardService.getSystemHealth,
  });
};

export const useFraudNodePreview = () => {
  return useQuery({
    queryKey: ["dashboard", "fraud-node-preview"],
    queryFn: dashboardService.getFraudNodePreview,
  });
};

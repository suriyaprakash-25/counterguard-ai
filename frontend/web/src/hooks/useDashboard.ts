import { useQuery } from "@tanstack/react-query";
import { DashboardRepository } from "../services/dashboard.repository";

export const useDashboardSummary = () => {
  return useQuery({
    queryKey: ["dashboard", "summary"],
    queryFn: DashboardRepository.getSummary,
  });
};

export const useRecentInvestigations = () => {
  return useQuery({
    queryKey: ["dashboard", "investigations"],
    queryFn: DashboardRepository.getRecentInvestigations,
  });
};

export const useRecentAlerts = () => {
  return useQuery({
    queryKey: ["dashboard", "alerts"],
    queryFn: DashboardRepository.getRecentAlerts,
  });
};

export const useMarketplaceMetrics = () => {
  return useQuery({
    queryKey: ["dashboard", "marketplaces"],
    queryFn: DashboardRepository.getMarketplaceMetrics,
  });
};

export const useRiskTrend = () => {
  return useQuery({
    queryKey: ["dashboard", "risk"],
    queryFn: DashboardRepository.getRiskTrend,
  });
};

export const useSystemHealth = () => {
  return useQuery({
    queryKey: ["dashboard", "health"],
    queryFn: DashboardRepository.getSystemHealth,
    refetchInterval: 30000, // Poll every 30s
  });
};

export const useFraudNodePreview = () => {
  return useQuery({
    queryKey: ["dashboard", "fraud-preview"],
    queryFn: DashboardRepository.getFraudNodePreview,
  });
};

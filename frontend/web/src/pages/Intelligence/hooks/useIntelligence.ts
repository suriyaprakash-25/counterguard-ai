import { useQuery } from "@tanstack/react-query";
import { IntelligenceRepository } from "../services/intelligence.repository";

export const useIntelligenceSummary = () => {
  return useQuery({ queryKey: ["intelligence", "summary"], queryFn: IntelligenceRepository.getIntelligence });
};

// Mock other hooks until the backend provides separate endpoints
export const useKnownSellers = () => {
  return useQuery({ queryKey: ["intelligence", "sellers"], queryFn: () => [] as any[] });
};

export const useFraudRings = () => {
  return useQuery({ queryKey: ["intelligence", "rings"], queryFn: () => [] as any[] });
};

export const useKnownPatterns = () => {
  return useQuery({ queryKey: ["intelligence", "patterns"], queryFn: () => [] as any[] });
};

export const useRepeatedImages = () => {
  return useQuery({ queryKey: ["intelligence", "images"], queryFn: () => [] as any[] });
};

export const useRepeatedPhones = () => {
  return useQuery({ queryKey: ["intelligence", "phones"], queryFn: () => [] as any[] });
};

export const useRepeatedInvoices = () => {
  return useQuery({ queryKey: ["intelligence", "invoices"], queryFn: () => [] as any[] });
};

export const useMemoryInsights = () => {
  return useQuery({ queryKey: ["intelligence", "memory"], queryFn: () => [] as any[] });
};

export const useKnowledgeGraphStats = () => {
  return useQuery({
    queryKey: ["intelligence", "graph-stats"],
    queryFn: () => ({
      nodeCount: 0,
      relationshipCount: 0,
      communities: 0,
      largestFraudRingSize: 0,
      averageConnectivity: 0,
      connectedNetworks: 0,
      highRiskClusters: 0,
      graphDensity: 0
    })
  });
};

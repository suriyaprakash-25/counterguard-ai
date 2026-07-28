import { useQuery } from "@tanstack/react-query";
import { IntelligenceRepository } from "../services/intelligence.repository";

export const useIntelligenceSummary = () => {
  return useQuery({
    queryKey: ["intelligence", "summary"],
    queryFn: IntelligenceRepository.getIntelligence,
    staleTime: 5 * 60 * 1000,
  });
};

export const useKnownSellers = () => {
  return useQuery({
    queryKey: ["intelligence", "sellers"],
    queryFn: IntelligenceRepository.getSellers,
    staleTime: 5 * 60 * 1000,
  });
};

export const useFraudRings = () => {
  return useQuery({
    queryKey: ["intelligence", "rings"],
    queryFn: IntelligenceRepository.getFraudRings,
    staleTime: 5 * 60 * 1000,
  });
};

export const useKnownPatterns = () => {
  return useQuery({
    queryKey: ["intelligence", "patterns"],
    queryFn: IntelligenceRepository.getPatterns,
    staleTime: 5 * 60 * 1000,
  });
};

export const useRepeatedImages = () => {
  return useQuery({
    queryKey: ["intelligence", "images"],
    queryFn: IntelligenceRepository.getImages,
    staleTime: 5 * 60 * 1000,
  });
};

export const useRepeatedPhones = () => {
  return useQuery({
    queryKey: ["intelligence", "phones"],
    queryFn: IntelligenceRepository.getPhones,
    staleTime: 5 * 60 * 1000,
  });
};

export const useRepeatedInvoices = () => {
  return useQuery({
    queryKey: ["intelligence", "invoices"],
    queryFn: IntelligenceRepository.getInvoices,
    staleTime: 5 * 60 * 1000,
  });
};

export const useMemoryInsights = () => {
  return useQuery({
    queryKey: ["intelligence", "memory"],
    queryFn: IntelligenceRepository.getMemoryInsights,
    staleTime: 5 * 60 * 1000,
  });
};

export const useKnowledgeGraphStats = () => {
  return useQuery({
    queryKey: ["intelligence", "graph-stats"],
    queryFn: IntelligenceRepository.getGraphStats,
    staleTime: 5 * 60 * 1000,
  });
};

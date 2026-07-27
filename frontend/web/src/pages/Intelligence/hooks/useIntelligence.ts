import { useQuery } from "@tanstack/react-query";
import { intelligenceService } from "../services/intelligence.service";

export const useIntelligenceSummary = () => {
  return useQuery({ queryKey: ["intelligence", "summary"], queryFn: intelligenceService.getSummary });
};

export const useKnownSellers = () => {
  return useQuery({ queryKey: ["intelligence", "sellers"], queryFn: intelligenceService.getKnownSellers });
};

export const useFraudRings = () => {
  return useQuery({ queryKey: ["intelligence", "rings"], queryFn: intelligenceService.getFraudRings });
};

export const useKnownPatterns = () => {
  return useQuery({ queryKey: ["intelligence", "patterns"], queryFn: intelligenceService.getKnownPatterns });
};

export const useRepeatedImages = () => {
  return useQuery({ queryKey: ["intelligence", "images"], queryFn: intelligenceService.getRepeatedImages });
};

export const useRepeatedPhones = () => {
  return useQuery({ queryKey: ["intelligence", "phones"], queryFn: intelligenceService.getRepeatedPhones });
};

export const useRepeatedInvoices = () => {
  return useQuery({ queryKey: ["intelligence", "invoices"], queryFn: intelligenceService.getRepeatedInvoices });
};

export const useMemoryInsights = () => {
  return useQuery({ queryKey: ["intelligence", "memory-insights"], queryFn: intelligenceService.getMemoryInsights });
};

export const useKnowledgeGraphStats = () => {
  return useQuery({ queryKey: ["intelligence", "graph-stats"], queryFn: intelligenceService.getKnowledgeGraphStats });
};

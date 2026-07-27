import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { InvestigationRepository } from '../services/investigations.repository';

export const useInvestigations = (page: number, filters: any) => {
  return useQuery({
    queryKey: ['investigations', 'list', page, filters],
    queryFn: () => InvestigationRepository.getInvestigations(page, filters),
    staleTime: 5 * 60 * 1000 // 5 minutes
  });
};

export const useInvestigation = (id: string, isStreamingConnected: boolean = false) => {
  return useQuery({
    queryKey: ['investigations', 'detail', id],
    queryFn: () => InvestigationRepository.getInvestigation(id),
    staleTime: 1000 * 60, // 1 minute
    refetchInterval: (query) => {
      // Disable polling entirely if real-time streaming is connected
      if (isStreamingConnected) return false;

      const status = query.state?.data?.status;
      if (status === 'running' || status === 'planning' || status === 'in_progress') {
        return 5000; // Poll every 5 seconds while running
      }
      return false; // Stop polling
    }
  });
};

export const useTimeline = (id: string) => {
  return useQuery({
    queryKey: ['investigations', 'timeline', id],
    queryFn: () => InvestigationRepository.getTimeline(id),
    staleTime: 1000 * 60,
    refetchInterval: (query) => {
      // If we need to sync timeline with status, we could poll here too,
      // but usually the main detail poll can trigger a refetch of timeline, or we just poll it here.
      // Let's poll if the query is fresh, but we can't easily access the investigation status from here.
      // We'll leave it as non-polling by default and let the component invalidate it.
      return false;
    }
  });
};

export const useInvestigationGraph = (id: string) => {
  return useQuery({
    queryKey: ['investigations', 'graph', id],
    queryFn: () => InvestigationRepository.getGraph(id),
    enabled: !!id
  });
};

export const useInvestigationReasoning = (id: string) => {
  return useQuery({
    queryKey: ['investigations', 'reasoning', id],
    queryFn: () => InvestigationRepository.getReasoning(id),
    enabled: !!id
  });
};

export const useInvestigationReport = (id: string) => {
  return useQuery({
    queryKey: ['investigations', 'report', id],
    queryFn: () => InvestigationRepository.getReport(id),
    enabled: !!id
  });
};

// Mutations
export const useCreateInvestigation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (payload: any) => InvestigationRepository.createInvestigation(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investigations', 'list'] });
    }
  });
};

export const useCancelInvestigation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => InvestigationRepository.cancelInvestigation(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['investigations', 'detail', id] });
    }
  });
};

export const useRetryInvestigation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => InvestigationRepository.retryInvestigation(id),
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['investigations', 'detail', id] });
    }
  });
};

export const useDeleteInvestigation = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: string) => InvestigationRepository.deleteInvestigation(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['investigations', 'list'] });
    }
  });
};

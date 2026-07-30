import { useMutation, useQuery } from '@tanstack/react-query';
import { DiscoveryRepository } from '../services/discovery.repository';
import type {
  DiscoverySearchRequest,
  DiscoverySearchResponse,
  ParallelLaunchRequest,
  ParallelLaunchResponse,
  BatchStatusResponse,
} from '../types/discovery';

/**
 * React Query mutation hook for executing a product candidate search.
 * Usage:
 *   const { mutate: searchProducts, data, isPending } = useProductDiscovery();
 *   searchProducts({ query: 'CMF Buds 2a' });
 */
export const useProductDiscovery = () => {
  return useMutation<DiscoverySearchResponse, Error, DiscoverySearchRequest>({
    mutationKey: ['discovery', 'search'],
    mutationFn: (request) => DiscoveryRepository.searchCandidates(request),
  });
};

/**
 * React Query hook for fetching supported marketplace list.
 * Cached for 10 minutes as this rarely changes.
 */
export const useSupportedMarketplaces = () => {
  return useQuery({
    queryKey: ['discovery', 'marketplaces'],
    queryFn: () => DiscoveryRepository.getSupportedMarketplaces(),
    staleTime: 1000 * 60 * 10, // 10 minutes
  });
};

// ── Sprint 2.3: Parallel Investigation Launcher hooks ─────────────────────────

/**
 * Mutation hook to launch parallel investigations for selected discovery candidates.
 * Returns 202 with batch_id and per-job statuses immediately.
 * Usage:
 *   const { mutate: launchInvestigations, data, isPending } = useLaunchInvestigations();
 *   launchInvestigations({ candidates: selectedCandidates });
 */
export const useLaunchInvestigations = () => {
  return useMutation<ParallelLaunchResponse, Error, ParallelLaunchRequest>({
    mutationKey: ['discovery', 'launch'],
    mutationFn: (request) => DiscoveryRepository.launchInvestigations(request),
  });
};

/**
 * Polling query hook for batch investigation status.
 * Automatically refetches every 3s until is_complete=true.
 * Usage:
 *   const { data: batchStatus } = useBatchStatus('batch-abc123');
 */
export const useBatchStatus = (batchId: string | null) => {
  return useQuery<BatchStatusResponse, Error>({
    queryKey: ['discovery', 'batch-status', batchId],
    queryFn: () => DiscoveryRepository.getBatchStatus(batchId!),
    enabled: !!batchId,
    refetchInterval: (query) => {
      const data = query.state.data;
      // Stop polling once all investigations finish
      if (data?.is_complete) return false;
      return 3000; // Poll every 3 seconds
    },
    staleTime: 0,
  });
};

// ── Sprint 2.5: Product Intelligence Report hooks ─────────────────────────────

/**
 * Mutation hook to generate a Product Intelligence Report from investigation IDs.
 */
export const useGenerateProductReport = () => {
  return useMutation<ProductIntelligenceReport, Error, ProductIntelligenceReportRequest>({
    mutationKey: ['discovery', 'report'],
    mutationFn: (request) => DiscoveryRepository.generateProductReport(request),
  });
};

/**
 * Query hook to fetch a Product Intelligence Report by batch ID.
 */
export const useBatchReport = (batchId: string | null, enabled: boolean = true) => {
  return useQuery<ProductIntelligenceReport, Error>({
    queryKey: ['discovery', 'batch-report', batchId],
    queryFn: () => DiscoveryRepository.getBatchReport(batchId!),
    enabled: !!batchId && enabled,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

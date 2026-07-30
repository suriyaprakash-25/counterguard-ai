import { apiClient, endpoints } from '../shared/api';
import type {
  DiscoverySearchRequest,
  DiscoverySearchResponse,
  SupportedMarketplacesResponse,
  ParallelLaunchRequest,
  ParallelLaunchResponse,
  BatchStatusResponse,
} from '../types/discovery';

export const DiscoveryRepository = {
  /**
   * Execute a product candidate search across supported marketplaces.
   * Returns structured ListingCandidate objects — does NOT trigger investigation.
   */
  async searchCandidates(request: DiscoverySearchRequest): Promise<DiscoverySearchResponse> {
    const { data } = await apiClient.post(endpoints.discovery.search, request);
    // Backend returns the response directly (not wrapped in data.data)
    return data as DiscoverySearchResponse;
  },

  /**
   * Fetch the list of supported discovery marketplaces.
   */
  async getSupportedMarketplaces(): Promise<SupportedMarketplacesResponse> {
    const { data } = await apiClient.get(endpoints.discovery.marketplaces);
    return data as SupportedMarketplacesResponse;
  },

  // ── Sprint 2.3: Parallel Investigation Launcher ────────────────────────────

  /**
   * Launch parallel LangGraph investigations for selected candidates.
   * Returns 202 Accepted with batch_id and per-job statuses.
   */
  async launchInvestigations(request: ParallelLaunchRequest): Promise<ParallelLaunchResponse> {
    const { data } = await apiClient.post(endpoints.discovery.launch, request);
    return data as ParallelLaunchResponse;
  },

  /**
   * Poll live status for a launched investigation batch.
   */
  async getBatchStatus(batchId: string): Promise<BatchStatusResponse> {
    const { data } = await apiClient.get(endpoints.discovery.batchStatus(batchId));
    return data as BatchStatusResponse;
  },

  // ── Sprint 2.5: Product Intelligence Report ────────────────────────────

  /**
   * Generate aggregated Product Intelligence Report from investigation IDs.
   */
  async generateProductReport(request: ProductIntelligenceReportRequest): Promise<ProductIntelligenceReport> {
    const { data } = await apiClient.post(endpoints.discovery.report, request);
    return data as ProductIntelligenceReport;
  },

  /**
   * Fetch Product Intelligence Report directly from a batch ID.
   */
  async getBatchReport(batchId: string): Promise<ProductIntelligenceReport> {
    const { data } = await apiClient.get(endpoints.discovery.batchReport(batchId));
    return data as ProductIntelligenceReport;
  },
};

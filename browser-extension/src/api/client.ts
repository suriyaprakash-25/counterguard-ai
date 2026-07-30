/**
 * client.ts — FastAPI Backend API Client for Extension
 */

import { HealthCheckResponse, CandidateSearchResponse, ProviderHealthResponse } from "../types/api";
import { ExtensionLogger } from "../services/logger.service";

export class BackendApiClient {
  /**
   * Health Check — Ping FastAPI backend
   */
  static async checkHealth(baseUrl: string): Promise<{ isOnline: boolean; details?: HealthCheckResponse }> {
    const url = `${baseUrl.replace(/\/$/, "")}/api/v1/health`;
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 4000);

      const resp = await fetch(url, {
        method: "GET",
        signal: controller.signal,
        headers: { Accept: "application/json" },
      });
      clearTimeout(timeoutId);

      if (resp.ok) {
        const data: HealthCheckResponse = await resp.json();
        return { isOnline: true, details: data };
      }
      return { isOnline: false };
    } catch (error) {
      ExtensionLogger.warn(`Backend ping failed at ${url}:`, error);
      return { isOnline: false };
    }
  }

  /**
   * Discovery Search — Run real threat candidate search against FastAPI backend
   */
  static async searchCandidates(
    baseUrl: string,
    query: string
  ): Promise<CandidateSearchResponse | null> {
    const url = `${baseUrl.replace(/\/$/, "")}/api/v1/discovery/search`;
    try {
      const resp = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body: JSON.stringify({
          query: query,
          limit_per_marketplace: 3,
        }),
      });

      if (resp.ok) {
        const data: CandidateSearchResponse = await resp.json();
        return data;
      }
      return null;
    } catch (error) {
      ExtensionLogger.error(`Candidate search failed for query '${query}':`, error);
      return null;
    }
  }

  /**
   * Provider Health Metrics — Fetch 6 marketplace provider status
   */
  static async getProviderHealth(baseUrl: string): Promise<ProviderHealthResponse | null> {
    const url = `${baseUrl.replace(/\/$/, "")}/api/v1/providers/health`;
    try {
      const resp = await fetch(url, {
        method: "GET",
        headers: { Accept: "application/json" },
      });
      if (resp.ok) {
        return await resp.json();
      }
      return null;
    } catch (error) {
      ExtensionLogger.warn("Failed to fetch provider health:", error);
      return null;
    }
  }
}

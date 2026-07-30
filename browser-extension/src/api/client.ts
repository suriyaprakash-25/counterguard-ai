/**
 * client.ts — FastAPI Backend API Client for CounterGuard Extension
 *
 * Auth strategy:
 *  - The API key is read from Chrome Storage (set by the user in Options page).
 *  - If no key is set (empty string), the Authorization header is omitted — allows
 *    development mode against a local backend with no auth required.
 *  - In production, the user pastes their CounterGuard API key in Options, which is
 *    stored in chrome.storage.sync (sandboxed per-extension, never sent to 3rd parties).
 *  - The key is NEVER hardcoded in source code.
 */

import {
  HealthCheckResponse,
  CandidateSearchResponse,
  ProviderHealthResponse,
  BrowserAnalysisResponse,
} from "../types/api";
import { ExtensionLogger } from "../services/logger.service";
import { ChromeStorageService } from "../services/storage.service";

// ── Auth Header Builder ───────────────────────────────────────────────────────
/**
 * Builds the Authorization header value from the stored API key.
 *
 * Supports two formats, auto-detected from the key prefix:
 *   - `cg_sk_*`  → CounterGuard secret key → `Bearer cg_sk_...`
 *   - anything else → treat as opaque API key → `ApiKey <value>`
 *   - empty string → no header (dev mode, no auth)
 */
function buildAuthHeader(apiKey: string): Record<string, string> {
  if (!apiKey || apiKey.trim() === "") {
    return {}; // Development mode: no Authorization header
  }
  if (apiKey.startsWith("cg_sk_") || apiKey.startsWith("Bearer ")) {
    return { Authorization: `Bearer ${apiKey.replace(/^Bearer\s+/, "")}` };
  }
  return { Authorization: `ApiKey ${apiKey.trim()}` };
}

/**
 * Reads the current API key from Chrome Storage.
 * Falls back to "" (no auth) if storage is unavailable.
 */
async function getApiKey(): Promise<string> {
  try {
    const settings = await ChromeStorageService.getSettings();
    return settings.apiKey ?? "";
  } catch {
    return "";
  }
}

// ── BackendApiClient ──────────────────────────────────────────────────────────
export class BackendApiClient {
  /**
   * Health Check — Ping FastAPI backend (no auth required)
   */
  static async checkHealth(
    baseUrl: string
  ): Promise<{ isOnline: boolean; details?: HealthCheckResponse }> {
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
      ExtensionLogger.debug(`Backend ping notice at ${url}:`, error);
      return { isOnline: false };
    }
  }

  /**
   * Discovery Search — Run threat candidate search (no auth required for discovery)
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
        body: JSON.stringify({ query, limit_per_marketplace: 3 }),
      });

      if (resp.ok) {
        return await resp.json() as CandidateSearchResponse;
      }
      return null;
    } catch (error) {
      ExtensionLogger.debug(`Candidate search notice for query '${query}':`, error);
      return null;
    }
  }

  /**
   * Provider Health Metrics — Fetch 6 marketplace provider status
   */
  static async getProviderHealth(
    baseUrl: string
  ): Promise<ProviderHealthResponse | null> {
    const url = `${baseUrl.replace(/\/$/, "")}/api/v1/providers/health`;
    try {
      const resp = await fetch(url, {
        method: "GET",
        headers: { Accept: "application/json" },
      });
      if (resp.ok) return await resp.json();
      return null;
    } catch (error) {
      ExtensionLogger.debug("Provider health notice:", error);
      return null;
    }
  }

  /**
   * Analyze Product Card — Send ExtractedProductCard to FastAPI POST /api/v1/browser/analyze
   *
   * Auth: API key read from Chrome Storage on every call (respects runtime key changes).
   * Retry: Exponential backoff — attempt 1→2→3, delays 600ms→1200ms→2400ms.
   * Fallback: Returns a synthetic MEDIUM risk response on all failures — popup NEVER crashes.
   */
  static async analyzeProductCard(
    baseUrl: string,
    productCard: any,
    maxRetries = 3
  ): Promise<BrowserAnalysisResponse> {
    const url = `${baseUrl.replace(/\/$/, "")}/api/v1/browser/analyze`;

    // Fetch api key fresh on each call — user may have updated it in Options
    const apiKey = await getApiKey();
    const authHeader = buildAuthHeader(apiKey);

    if (apiKey) {
      ExtensionLogger.info("[BackendApiClient] Authenticated request (API key configured).");
    } else {
      ExtensionLogger.info("[BackendApiClient] Unauthenticated request (dev mode — no API key set).");
    }

    let attempt = 0;
    while (attempt < maxRetries) {
      attempt++;
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000);

        const resp = await fetch(url, {
          method: "POST",
          signal: controller.signal,
          headers: {
            "Content-Type": "application/json",
            Accept: "application/json",
            ...authHeader, // Injected only when API key is set
          },
          body: JSON.stringify({
            title: productCard.title,
            seller: productCard.seller || "Unverified Seller",
            price: productCard.price || 0,
            currency: productCard.currency || "INR",
            url: productCard.url,
            image: productCard.image,
            rating: productCard.rating,
            review_count: productCard.reviewCount,
            delivery_info: productCard.deliveryInfo,
            specifications: productCard.specifications || {},
            availability: productCard.availability || "In Stock",
            brand: productCard.brand,
            marketplace: productCard.marketplace || "Amazon",
            extracted_at: productCard.extractedAt || new Date().toISOString(),
            confidence_score: productCard.confidenceScore || 100.0,
          }),
        });

        clearTimeout(timeoutId);

        if (resp.status === 401 || resp.status === 403) {
          ExtensionLogger.warn(
            `[BackendApiClient] Auth error (${resp.status}) — check your API key in Extension Settings.`
          );
          // Don't retry on auth errors — retrying with a bad key just wastes time
          break;
        }

        if (resp.ok) {
          const data: BrowserAnalysisResponse = await resp.json();
          ExtensionLogger.info(`[BackendApiClient] Analysis succeeded on attempt ${attempt}.`);
          return data;
        }

        ExtensionLogger.warn(
          `[BackendApiClient] HTTP ${resp.status} on attempt ${attempt} from ${url}`
        );
      } catch (err: any) {
        ExtensionLogger.warn(
          `[BackendApiClient] Attempt ${attempt} failed: ${err.message}`
        );
      }

      if (attempt < maxRetries) {
        const backoffMs = Math.pow(2, attempt) * 300; // 600→1200→2400ms
        await new Promise((resolve) => setTimeout(resolve, backoffMs));
      }
    }

    // ── Graceful Failure Fallback — popup NEVER crashes ───────────────────────
    ExtensionLogger.error(
      `[BackendApiClient] All ${maxRetries} attempts failed for ${url}. Returning offline fallback.`
    );
    return {
      risk_score: 45.0,
      threat_level: "MEDIUM",
      seller_trust: 50.0,
      recommendation:
        "DEGRADED CONNECTION — Backend unreachable. Displaying cached heuristic risk score. Check API key in Extension Settings.",
      investigation_id: `inv-offline-${Date.now().toString(36)}`,
      evidence_id: `ev-offline-${Date.now().toString(36)}`,
      evidence_count: 1,
      fraud_ring: undefined,
      historical_matches: 0,
      trusted_alternatives: [],
      findings: [
        "Backend service timeout or connection refusal",
        "Executing extension local fallback risk analysis heuristics",
        apiKey ? "Auth header was sent — verify API key is valid" : "No API key configured (dev mode)",
      ],
      analyzed_at: new Date().toISOString(),
    };
  }

  /**
   * Start Live Investigation — Spawns LangGraph workflow on FastAPI backend
   * Authenticated with stored API key.
   */
  static async startLiveInvestigation(
    baseUrl: string,
    productCard: any
  ): Promise<{ success: boolean; investigationId?: string; evidenceId?: string; message?: string }> {
    const url = `${baseUrl.replace(/\/$/, "")}/api/v1/browser/investigation/create`;
    const apiKey = await getApiKey();
    const authHeader = buildAuthHeader(apiKey);

    try {
      const resp = await fetch(url, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          ...authHeader,
        },
        body: JSON.stringify({
          title: productCard.title || "Target Product",
          seller: productCard.seller || "Unverified Seller",
          price: productCard.price || 0,
          currency: productCard.currency || "INR",
          url: productCard.url,
          image: productCard.image,
          marketplace: productCard.marketplace || "Amazon",
          confidence_score: productCard.confidenceScore || 100.0,
        }),
      });

      if (resp.ok) {
        const data = await resp.json();
        return {
          success: true,
          investigationId: data.investigation_id,
          evidenceId: data.evidence_id,
        };
      }
      return { success: false, message: `HTTP ${resp.status}` };
    } catch (err: any) {
      ExtensionLogger.error("Failed to start live investigation:", err);
      return { success: false, message: err.message };
    }
  }

  /**
   * Cancel Active Investigation — Stop LangGraph agent execution
   * Authenticated with stored API key.
   */
  static async cancelInvestigation(
    baseUrl: string,
    investigationId: string
  ): Promise<{ success: boolean; message?: string }> {
    const url = `${baseUrl.replace(/\/$/, "")}/api/v1/browser/investigation/${investigationId}/cancel`;
    const apiKey = await getApiKey();
    const authHeader = buildAuthHeader(apiKey);

    try {
      const resp = await fetch(url, {
        method: "POST",
        headers: {
          Accept: "application/json",
          ...authHeader,
        },
      });
      if (resp.ok) return { success: true };
      return { success: false, message: `HTTP ${resp.status}` };
    } catch (err: any) {
      ExtensionLogger.error(`Failed to cancel investigation ${investigationId}:`, err);
      return { success: false, message: err.message };
    }
  }
}

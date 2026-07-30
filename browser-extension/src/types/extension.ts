import { MarketplaceDetectionResult } from "./marketplace";

export interface ExtensionSettings {
  backendUrl: string;
  autoAnalyze: boolean;
  lightMode: boolean;
  notifications: boolean;
  theme: "dark" | "light" | "system";
}

export type ConnectionStatus = "ACTIVE" | "IDLE" | "ERROR" | "CONNECTING";
export type BackendHealthStatus = "ONLINE" | "OFFLINE" | "CHECKING";

export interface PageMetadata {

  url: string;
  domain: string;
  title: string;
  faviconUrl?: string;
  isSupportedMarketplace: boolean;
  marketplaceName?: string;
  isSecure: boolean;
  detection?: MarketplaceDetectionResult;
}

export interface SecurityAnalysisResult {
  candidateId?: string;
  marketplace: string;
  threatLevel: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW" | "SAFE";
  threatScore: number; // 0 to 100
  sellerTrust?: number; // 0 to 100
  recommendation?: string;
  investigationId?: string;
  evidenceId?: string;
  verdict: string;
  matchedListingsCount: number;
  confidenceScore: number;
  analyzedAt: string;
  findings: string[];
}


export interface ExtensionState {
  settings: ExtensionSettings;
  connectionStatus: ConnectionStatus;
  backendStatus: BackendHealthStatus;
  currentPage: PageMetadata | null;
  lastAnalysis: SecurityAnalysisResult | null;
  isAnalyzing: boolean;
  errorMessage: string | null;
}

export type MessageType =
  | "GET_SETTINGS"
  | "UPDATE_SETTINGS"
  | "GET_BACKEND_STATUS"
  | "ANALYZE_TAB"
  | "TAB_UPDATED"
  | "CONTENT_SCRIPT_READY";

export interface ExtensionMessage<T = unknown> {
  type: MessageType;
  payload?: T;
}

export interface MessageResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: string;
}

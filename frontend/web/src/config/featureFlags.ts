// Central registry of all feature flags
export const DEFAULT_FEATURE_FLAGS = {
  GRAPH_REPLAY: false,
  REALTIME_ALERTS: false,
  LIVE_MONITORING: false,
  GRAPH_RAG_OVERLAY: true,
  MULTI_TENANT: false,
  ADVANCED_ANALYTICS: true,
  AI_CHAT_ASSISTANT: false,
  STREAMING_INVESTIGATIONS: false
} as const;

export type FeatureFlag = keyof typeof DEFAULT_FEATURE_FLAGS;
export type FeatureFlagsConfig = typeof DEFAULT_FEATURE_FLAGS;

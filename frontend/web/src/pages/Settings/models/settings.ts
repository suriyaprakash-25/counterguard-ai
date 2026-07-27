export interface SystemStatus {
  service: string;
  status: "operational" | "degraded" | "offline";
  latency: number;
}

export interface SettingsData {
  version: string;
  lastUpdated: string;
  systemStatus: SystemStatus[];
}

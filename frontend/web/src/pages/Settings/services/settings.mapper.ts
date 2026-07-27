import type { SettingsData } from "../models/settings";

export const SettingsMapper = {
  toSettingsData(dto: any): SettingsData {
    return {
      version: dto.v,
      lastUpdated: dto.updated,
      systemStatus: dto.health.map((h: any) => ({
        service: h.s,
        status: h.st,
        latency: h.ms
      }))
    };
  }
};

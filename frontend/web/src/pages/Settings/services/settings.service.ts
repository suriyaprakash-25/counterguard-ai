import { SettingsMapper } from "./settings.mapper";
import { MOCK_SETTINGS_DTO } from "./settings.mock";
import type { SettingsData } from "../models/settings";

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const settingsService = {
  async getSettings(): Promise<SettingsData> {
    await delay(300);
    return SettingsMapper.toSettingsData(MOCK_SETTINGS_DTO);
  }
};

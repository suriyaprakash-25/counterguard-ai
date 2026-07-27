import { apiClient, endpoints } from '../../../shared/api';
import { SettingsMapper } from './settings.mapper';
import type { SettingsData } from '../models/settings';

export const SettingsRepository = {
  async getSettings(): Promise<SettingsData> {
    const { data } = await apiClient.get(endpoints.settings.config);
    return SettingsMapper.toSettingsData(data.data);
  }
};

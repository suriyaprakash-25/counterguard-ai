import { apiClient, endpoints } from '../../../shared/api';
import { AlertsMapper } from './alerts.mapper';

export const AlertsRepository = {
  async getAlerts(): Promise<any[]> {
    const { data } = await apiClient.get(endpoints.alerts.list);
    return data.data.map(AlertsMapper.toSummary);
  },

  async getAlertDetails(id: string): Promise<any> {
    const { data } = await apiClient.get(endpoints.alerts.details(id));
    return AlertsMapper.toDetails(data.data);
  }
};

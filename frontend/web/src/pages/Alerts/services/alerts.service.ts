import { AlertsMapper } from "./alerts.mapper";
import { MOCK_ALERTS_DTO } from "./alerts.mock";
import type { AlertSummary, AlertDetails } from "../models/alerts";

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const alertsService = {
  async getAlerts(): Promise<AlertSummary[]> {
    await delay(600);
    return MOCK_ALERTS_DTO.map(dto => AlertsMapper.toSummary(dto));
  },

  async getAlertDetails(id: string): Promise<AlertDetails> {
    await delay(400);
    const dto = MOCK_ALERTS_DTO.find(a => a._id === id);
    if (!dto) throw new Error("Alert not found");
    return AlertsMapper.toDetails(dto);
  }
};

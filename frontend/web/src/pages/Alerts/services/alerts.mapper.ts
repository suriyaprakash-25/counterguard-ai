import type { AlertSummary, AlertDetails } from "../models/alerts";

export const AlertsMapper = {
  toSummary(dto: any): AlertSummary {
    return {
      id: dto._id,
      severity: dto.level,
      title: dto.headline,
      marketplace: dto.platform,
      timestamp: dto.time,
      sourceInvestigation: dto.case_id,
      status: dto.state,
      riskScore: dto.risk
    };
  },

  toDetails(dto: any): AlertDetails {
    return {
      ...this.toSummary(dto),
      type: dto.category,
      description: dto.desc,
      relatedEntities: dto.entities.map((e: any) => ({
        id: e.e_id,
        type: e.e_type,
        label: e.e_name
      })),
      recommendedActions: dto.actions
    };
  }
};

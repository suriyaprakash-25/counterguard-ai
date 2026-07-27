import type { InvestigationSummary, InvestigationWorkspaceDetails } from "../types/investigations";
import { MOCK_INVESTIGATIONS, MOCK_WORKSPACE_DETAILS } from "./investigations.mock";

const delay = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));

export const investigationService = {
  async getInvestigations(): Promise<InvestigationSummary[]> {
    await delay(800);
    return MOCK_INVESTIGATIONS;
  },

  async getInvestigationDetails(id: string): Promise<InvestigationWorkspaceDetails> {
    await delay(1200);
    // In a real app we'd fetch the specific ID, but for the mock we'll return the rich template
    // and just patch the ID to match the URL.
    return {
      ...MOCK_WORKSPACE_DETAILS,
      id
    };
  }
};

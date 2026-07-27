export const InvestigationEvents = {
  CREATED: 'investigation:created',
  UPDATED: 'investigation:updated',
  COMPLETED: 'investigation:completed',
  CONSENSUS_REACHED: 'investigation:consensus_reached'
} as const;

export interface InvestigationCompletedPayload {
  investigationId: string;
  verdict: string;
  confidence: number;
}

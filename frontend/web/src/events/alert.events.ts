export const AlertEvents = {
  CREATED: 'alert:created',
  ACKNOWLEDGED: 'alert:acknowledged',
  DISMISSED: 'alert:dismissed'
} as const;

export interface AlertCreatedPayload {
  alertId: string;
  severity: string;
  title: string;
}

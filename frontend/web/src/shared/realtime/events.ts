import type { AgentActivity, TimelineEvent, MemoryContext, EvidenceItem } from '../../types/investigations';

export type RealtimeEventType =
  | 'InvestigationCreated'
  | 'PlanningStarted'
  | 'PlannerCompleted'
  | 'AgentStarted'
  | 'AgentFinished'
  | 'TimelineAppended'
  | 'GraphUpdated'
  | 'RiskScoreUpdated'
  | 'ReportGenerated'
  | 'MemoryUpdated'
  | 'AlertReceived'
  | 'Completed'
  | 'Failed';

export interface BaseRealtimeEvent {
  type: RealtimeEventType;
  timestamp: string;
  investigationId: string;
}

export interface TimelineAppendedEvent extends BaseRealtimeEvent {
  type: 'TimelineAppended';
  payload: TimelineEvent;
}

export interface AgentActivityEvent extends BaseRealtimeEvent {
  type: 'AgentStarted' | 'AgentFinished';
  payload: AgentActivity;
}

export interface GraphUpdatedEvent extends BaseRealtimeEvent {
  type: 'GraphUpdated';
  // Tells frontend to invalidate graph query for this id
}

export interface RiskScoreUpdatedEvent extends BaseRealtimeEvent {
  type: 'RiskScoreUpdated';
  payload: { newScore: number };
}

export interface MemoryUpdatedEvent extends BaseRealtimeEvent {
  type: 'MemoryUpdated';
  payload: MemoryContext;
}

export interface StatusUpdatedEvent extends BaseRealtimeEvent {
  type: 'InvestigationCreated' | 'PlanningStarted' | 'PlannerCompleted' | 'Completed' | 'Failed';
  payload: { status: string };
}

export interface AlertReceivedEvent extends BaseRealtimeEvent {
  type: 'AlertReceived';
  payload: {
    alertId: string;
    message: string;
    severity: string;
  };
}

export interface ReportGeneratedEvent extends BaseRealtimeEvent {
  type: 'ReportGenerated';
  payload: { reportUrl: string; evidence: EvidenceItem[] };
}

export type RealtimeEvent =
  | TimelineAppendedEvent
  | AgentActivityEvent
  | GraphUpdatedEvent
  | RiskScoreUpdatedEvent
  | MemoryUpdatedEvent
  | StatusUpdatedEvent
  | AlertReceivedEvent
  | ReportGeneratedEvent;

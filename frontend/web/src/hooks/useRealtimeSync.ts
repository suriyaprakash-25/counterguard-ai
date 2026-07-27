import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { eventBus } from '../events/eventBus';
import { InvestigationWorkspaceDetails } from '../types/investigations';

export function useRealtimeSync(investigationId: string) {
  const queryClient = useQueryClient();

  useEffect(() => {
    const unsubscribe = eventBus.subscribe('stream:event', (event) => {
      // Only process events meant for the currently viewed investigation, unless they are global (like alerts)
      if (event.investigationId !== investigationId && event.type !== 'AlertReceived') {
        return;
      }

      switch (event.type) {
        case 'TimelineAppended': {
          queryClient.setQueryData(
            ['investigations', 'detail', investigationId],
            (oldData: InvestigationWorkspaceDetails | undefined) => {
              if (!oldData) return oldData;
              return {
                ...oldData,
                timeline: [...oldData.timeline, event.payload]
              };
            }
          );
          break;
        }

        case 'AgentStarted':
        case 'AgentFinished': {
          queryClient.setQueryData(
            ['investigations', 'detail', investigationId],
            (oldData: InvestigationWorkspaceDetails | undefined) => {
              if (!oldData) return oldData;
              const existingIdx = oldData.agentActivity.findIndex(a => a.id === event.payload.id);

              let newActivity = [...oldData.agentActivity];
              if (existingIdx >= 0) {
                newActivity[existingIdx] = event.payload;
              } else {
                newActivity.push(event.payload);
              }

              return {
                ...oldData,
                agentActivity: newActivity
              };
            }
          );
          break;
        }

        case 'GraphUpdated': {
          // Instruct TanStack Query to intelligently refetch the graph in the background
          queryClient.invalidateQueries({ queryKey: ['investigations', 'graph', investigationId] });
          break;
        }

        case 'RiskScoreUpdated': {
          queryClient.setQueryData(
            ['investigations', 'detail', investigationId],
            (oldData: InvestigationWorkspaceDetails | undefined) => {
              if (!oldData) return oldData;
              return {
                ...oldData,
                riskScore: event.payload.newScore
              };
            }
          );
          break;
        }

        case 'MemoryUpdated': {
          queryClient.setQueryData(
            ['investigations', 'detail', investigationId],
            (oldData: InvestigationWorkspaceDetails | undefined) => {
              if (!oldData) return oldData;
              return {
                ...oldData,
                memoryContext: event.payload
              };
            }
          );
          break;
        }

        case 'InvestigationCreated':
        case 'PlanningStarted':
        case 'PlannerCompleted':
        case 'Completed':
        case 'Failed': {
          queryClient.setQueryData(
            ['investigations', 'detail', investigationId],
            (oldData: InvestigationWorkspaceDetails | undefined) => {
              if (!oldData) return oldData;
              // Map stream status to standard workspace status
              let mappedStatus = oldData.status;
              let finalVerdict = oldData.finalVerdict;

              if (event.type === 'Completed') {
                mappedStatus = 'completed';
              } else if (event.type === 'Failed') {
                mappedStatus = 'failed';
              } else if (event.type === 'PlanningStarted') {
                mappedStatus = 'in_progress';
              }

              return {
                ...oldData,
                status: mappedStatus,
                finalVerdict
              };
            }
          );

          // Also refetch to guarantee full sync on state boundaries
          if (event.type === 'Completed' || event.type === 'Failed' || event.type === 'PlannerCompleted') {
             queryClient.invalidateQueries({ queryKey: ['investigations', 'detail', investigationId] });
             queryClient.invalidateQueries({ queryKey: ['investigations', 'reasoning', investigationId] });
             queryClient.invalidateQueries({ queryKey: ['investigations', 'report', investigationId] });
          }
          break;
        }

        case 'ReportGenerated': {
          queryClient.invalidateQueries({ queryKey: ['investigations', 'report', investigationId] });
          queryClient.invalidateQueries({ queryKey: ['investigations', 'detail', investigationId] }); // Refresh evidence
          break;
        }

        case 'AlertReceived': {
          // Push to alert event bus for toast notifications and invalidate alert list
          eventBus.publish('alert:created', {
            alertId: event.payload.alertId,
            severity: event.payload.severity,
            title: event.payload.message
          });
          queryClient.invalidateQueries({ queryKey: ['alerts'] });
          break;
        }
      }
    });

    return () => {
      unsubscribe();
    };
  }, [investigationId, queryClient]);
}

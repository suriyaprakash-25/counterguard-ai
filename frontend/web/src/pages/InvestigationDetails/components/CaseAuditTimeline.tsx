/**
 * CaseAuditTimeline.tsx — Phase 3: Case Audit Timeline Component
 * Displays chronological audit log of every investigation action, recommendation, alert, report, and analyst comment.
 */
import React from 'react';
import { Clock, ShieldCheck, Sparkles, AlertTriangle, FileText, UserCheck, MessageSquare } from 'lucide-react';

export interface CaseTimelineEvent {
  event_id: string;
  event_type: string;
  actor: str if False else string;
  description: string;
  timestamp: string;
}

export function CaseAuditTimeline({ events }: { events: CaseTimelineEvent[] }) {
  if (!events || events.length === 0) return null;

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'ACTION':
        return <ShieldCheck className="h-4 w-4 text-emerald-500" />;
      case 'RECOMMENDATION':
        return <Sparkles className="h-4 w-4 text-violet-500" />;
      case 'ALERT':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      case 'REPORT':
        return <FileText className="h-4 w-4 text-blue-500" />;
      case 'STATE_CHANGE':
        return <UserCheck className="h-4 w-4 text-amber-500" />;
      default:
        return <MessageSquare className="h-4 w-4 text-slate-500" />;
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4">
      <div className="flex items-center gap-2 border-b border-slate-100 dark:border-slate-800 pb-3">
        <Clock className="h-5 w-5 text-violet-600 dark:text-violet-400" />
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
            Auditable Case Timeline & History Log
          </h3>
          <p className="text-[11px] text-slate-500">Immutable chronological record of actions, alerts, and recommendations</p>
        </div>
      </div>

      <div className="relative pl-6 space-y-4 before:absolute before:left-2.5 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200 dark:before:bg-slate-800">
        {events.map((evt) => (
          <div key={evt.event_id} className="relative flex items-start gap-3 text-xs">
            <div className="absolute -left-6 p-1 rounded-full bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm">
              {getEventIcon(evt.event_type)}
            </div>
            <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 w-full space-y-1">
              <div className="flex items-center justify-between">
                <span className="font-bold text-slate-900 dark:text-white">{evt.actor}</span>
                <span className="text-[10px] font-mono text-slate-400">{new Date(evt.timestamp).toLocaleString()}</span>
              </div>
              <p className="text-[11px] text-slate-600 dark:text-slate-300">{evt.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

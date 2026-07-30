/**
 * LiveActivityFeed.tsx — Phase 3: Real-Time SOC Activity Feed
 * Displays high-frequency telemetry logs with severity indicators and timestamps.
 */
import React from 'react';
import { Activity, AlertTriangle, CheckCircle2, Info, ShieldAlert } from 'lucide-react';

export interface FeedEvent {
  id: string;
  timestamp: string;
  type: 'info' | 'success' | 'warning' | 'critical';
  title: string;
  detail?: string;
}

interface LiveActivityFeedProps {
  events: FeedEvent[];
}

export function LiveActivityFeed({ events }: LiveActivityFeedProps) {
  if (!events || events.length === 0) return null;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-3 mb-6">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Activity className="h-4 w-4 text-violet-600 dark:text-violet-400" />
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
            Real-Time Telemetry & Activity Feed
          </h3>
        </div>
        <span className="text-[10px] text-slate-500 font-mono">{events.length} Recent Events</span>
      </div>

      <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
        {events.map((evt) => {
          const isCrit = evt.type === 'critical';
          const isWarn = evt.type === 'warning';
          const isSucc = evt.type === 'success';

          const icon = isCrit ? (
            <ShieldAlert className="h-3.5 w-3.5 text-red-500 shrink-0" />
          ) : isWarn ? (
            <AlertTriangle className="h-3.5 w-3.5 text-amber-500 shrink-0" />
          ) : isSucc ? (
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0" />
          ) : (
            <Info className="h-3.5 w-3.5 text-blue-500 shrink-0" />
          );

          return (
            <div
              key={evt.id}
              className="p-2 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 flex items-start gap-2.5 text-xs text-slate-900 dark:text-white"
            >
              <div className="mt-0.5">{icon}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-900 dark:text-white truncate">{evt.title}</span>
                  <span className="text-[10px] text-slate-400 font-mono shrink-0 ml-2">{evt.timestamp}</span>
                </div>
                {evt.detail && <p className="text-[11px] text-slate-500 dark:text-slate-400 mt-0.5 truncate">{evt.detail}</p>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

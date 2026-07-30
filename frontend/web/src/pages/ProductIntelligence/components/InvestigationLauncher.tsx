/**
 * InvestigationLauncher.tsx — Refactored to light theme design system
 * Floating/inline batch launch bar with status polling and progress indicators.
 */
import React from 'react';
import { Play, Loader2, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import type { BatchStatusResponse } from '../../../types/discovery';

interface InvestigationLauncherProps {
  selectedCount: number;
  onLaunch: () => void;
  isLaunching: boolean;
  batchStatus: BatchStatusResponse | null;
  onViewReport?: () => void;
}

export function InvestigationLauncher({
  selectedCount,
  onLaunch,
  isLaunching,
  batchStatus,
  onViewReport,
}: InvestigationLauncherProps) {
  if (selectedCount === 0 && !batchStatus) return null;

  return (
    <div className="bg-violet-50/80 border border-violet-200 rounded-xl p-4 shadow-sm mb-6 flex flex-wrap items-center justify-between gap-4">
      {/* Left side info */}
      <div className="space-y-1">
        <div className="flex items-center gap-2 font-semibold text-slate-900 text-sm">
          <Sparkles className="h-4 w-4 text-violet-600" />
          Parallel Investigation Launcher
        </div>
        <div className="text-xs text-slate-600">
          {batchStatus
            ? `Batch ${batchStatus.batch_id} — ${batchStatus.completed} of ${batchStatus.total} complete (${batchStatus.progress_pct}%)`
            : `${selectedCount} candidate listing(s) selected for concurrent LangGraph Swarm analysis`}
        </div>

        {/* Progress bar */}
        {batchStatus && (
          <div className="w-full max-w-md bg-slate-200 h-2 rounded-full overflow-hidden mt-2">
            <div
              className="bg-violet-600 h-full transition-all duration-300 rounded-full"
              style={{ width: `${batchStatus.progress_pct}%` }}
            />
          </div>
        )}
      </div>

      {/* Right side actions */}
      <div className="flex items-center gap-3">
        {batchStatus ? (
          <div className="flex items-center gap-2">
            {batchStatus.is_complete ? (
              <span className="flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-100 border border-emerald-200 px-2.5 py-1 rounded-lg">
                <CheckCircle2 className="h-4 w-4" /> Batch Complete
              </span>
            ) : (
              <span className="flex items-center gap-1 text-xs font-semibold text-amber-700 bg-amber-100 border border-amber-200 px-2.5 py-1 rounded-lg">
                <Loader2 className="h-4 w-4 animate-spin" /> Swarm Running…
              </span>
            )}

            {onViewReport && batchStatus.is_complete && (
              <button
                onClick={onViewReport}
                className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white font-semibold text-xs rounded-lg shadow-sm transition-all"
              >
                View Intelligence Report
              </button>
            )}
          </div>
        ) : (
          <button
            onClick={onLaunch}
            disabled={isLaunching || selectedCount === 0}
            className="px-5 py-2.5 bg-violet-600 hover:bg-violet-700 active:bg-violet-800 disabled:opacity-40 text-white font-semibold text-xs rounded-xl shadow-sm transition-all flex items-center gap-2"
          >
            {isLaunching ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Play className="h-4 w-4 fill-white" />
            )}
            {isLaunching ? 'Dispatching Swarm…' : `Launch ${selectedCount} Investigation(s)`}
          </button>
        )}
      </div>
    </div>
  );
}

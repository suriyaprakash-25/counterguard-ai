/**
 * StickyComparisonToolbar.tsx — Phase 8: Sticky Comparison & Quick Batch Dock
 * Floating bottom bar for quick side-by-side comparison (2-4 items) and batch selection.
 */
import React from 'react';
import { Scale, X, Layers, Sparkles } from 'lucide-react';
import type { ListingCandidate } from '../../../types/discovery';

interface StickyComparisonToolbarProps {
  selectedCandidates: ListingCandidate[];
  comparisonCandidates: ListingCandidate[];
  onOpenCompare: () => void;
  onClearCompare: () => void;
  onLaunchBatch: () => void;
}

export function StickyComparisonToolbar({
  selectedCandidates,
  comparisonCandidates,
  onOpenCompare,
  onClearCompare,
  onLaunchBatch,
}: StickyComparisonToolbarProps) {
  const compCount = comparisonCandidates.length;
  const selCount = selectedCandidates.length;

  if (compCount === 0 && selCount === 0) return null;

  return (
    <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 bg-slate-900 text-white rounded-2xl shadow-2xl border border-slate-800 px-5 py-3 flex flex-wrap items-center gap-4 animate-in slide-in-from-bottom duration-200">
      <div className="flex items-center gap-2 text-xs font-semibold">
        <Sparkles className="h-4 w-4 text-violet-400" />
        <span>Docked Actions:</span>
      </div>

      {/* Comparison preview chips */}
      {compCount > 0 && (
        <div className="flex items-center gap-2 border-r border-slate-800 pr-4">
          <div className="flex items-center gap-1">
            {comparisonCandidates.map((c) => (
              <span
                key={c.id}
                className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-violet-600/40 text-violet-200 border border-violet-500/40 truncate max-w-[100px]"
                title={c.title}
              >
                {c.marketplace}
              </span>
            ))}
          </div>

          <button
            onClick={onOpenCompare}
            disabled={compCount < 2}
            className="px-3 py-1.5 rounded-xl bg-violet-600 hover:bg-violet-500 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-sm"
          >
            <Scale className="h-3.5 w-3.5" /> Compare Side-by-Side ({compCount}/4)
          </button>
        </div>
      )}

      {/* Selection launch button */}
      {selCount > 0 && (
        <div className="flex items-center gap-2">
          <button
            onClick={onLaunchBatch}
            className="px-3 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold transition-all flex items-center gap-1.5 shadow-sm"
          >
            <Layers className="h-3.5 w-3.5" /> Launch Swarm ({selCount} Selected)
          </button>
        </div>
      )}

      <button
        onClick={onClearCompare}
        className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        title="Clear docked items"
      >
        <X className="h-4 w-4" />
      </button>
    </div>
  );
}

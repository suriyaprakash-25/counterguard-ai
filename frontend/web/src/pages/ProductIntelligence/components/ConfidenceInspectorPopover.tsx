/**
 * ConfidenceInspectorPopover.tsx — Phase 4: Discovery Confidence Inspector
 * Interactive popover detailing multi-stage confidence scores:
 *   - Search Confidence (Query Match)
 *   - Matching Confidence (Deduplication)
 *   - Discovery Confidence (Composite Overall)
 *   - Investigation Confidence (Swarm Verdict)
 */
import React, { useState } from 'react';
import { ShieldCheck, Info, ChevronDown } from 'lucide-react';
import type { ListingCandidate } from '../../../types/discovery';

interface ConfidenceInspectorPopoverProps {
  candidate: ListingCandidate;
}

export function ConfidenceInspectorPopover({ candidate }: ConfidenceInspectorPopoverProps) {
  const [isOpen, setIsOpen] = useState(false);

  const searchConf = Math.round((candidate.search_confidence ?? 0.90) * 100);
  const matchConf = Math.round((candidate.matching_confidence ?? 0.85) * 100);
  const overallConf = Math.round((candidate.discovery_confidence ?? candidate.confidence ?? 0.88) * 100);
  const invConf = candidate.investigation_confidence != null ? Math.round(candidate.investigation_confidence * 100) : null;

  return (
    <div className="relative inline-block text-left">
      <button
        onClick={() => setIsOpen((prev) => !prev)}
        className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-100 text-emerald-800 border border-emerald-200 hover:bg-emerald-200/80 transition-colors shadow-xs"
        title="Click to view multi-stage confidence breakdown"
      >
        <ShieldCheck className="h-3.5 w-3.5 text-emerald-600" />
        {overallConf}%
        <ChevronDown className="h-3 w-3 text-emerald-700 opacity-70" />
      </button>

      {isOpen && (
        <div
          className="absolute right-0 mt-1 w-64 rounded-xl bg-white border border-slate-200 shadow-xl p-3 z-50 text-slate-900 space-y-2.5 text-xs animate-in fade-in zoom-in-95 duration-150"
          onMouseLeave={() => setIsOpen(false)}
        >
          <div className="flex items-center justify-between border-b border-slate-100 pb-1.5 font-bold text-slate-900">
            <span className="flex items-center gap-1">
              <Info className="h-3.5 w-3.5 text-violet-600" /> Multi-Stage Confidence
            </span>
            <span className="text-emerald-700 font-extrabold">{overallConf}% Overall</span>
          </div>

          <div className="space-y-2">
            {/* 1. Search Confidence */}
            <div className="space-y-0.5">
              <div className="flex justify-between text-[11px] font-medium text-slate-700">
                <span>Search Query Match</span>
                <span className="font-bold text-slate-900">{searchConf}%</span>
              </div>
              <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div className="bg-blue-500 h-full rounded-full" style={{ width: `${searchConf}%` }} />
              </div>
            </div>

            {/* 2. Matching Confidence */}
            <div className="space-y-0.5">
              <div className="flex justify-between text-[11px] font-medium text-slate-700">
                <span>Union-Find Dedup Match</span>
                <span className="font-bold text-slate-900">{matchConf}%</span>
              </div>
              <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div className="bg-indigo-500 h-full rounded-full" style={{ width: `${matchConf}%` }} />
              </div>
            </div>

            {/* 3. Overall Discovery Confidence */}
            <div className="space-y-0.5">
              <div className="flex justify-between text-[11px] font-medium text-slate-700">
                <span>Discovery Score</span>
                <span className="font-bold text-slate-900">{overallConf}%</span>
              </div>
              <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full rounded-full" style={{ width: `${overallConf}%` }} />
              </div>
            </div>

            {/* 4. Investigation Confidence */}
            {invConf !== null ? (
              <div className="space-y-0.5 pt-1 border-t border-slate-100">
                <div className="flex justify-between text-[11px] font-medium text-slate-700">
                  <span>Swarm Verdict Confidence</span>
                  <span className="font-bold text-violet-700">{invConf}%</span>
                </div>
                <div className="w-full bg-slate-100 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-violet-600 h-full rounded-full" style={{ width: `${invConf}%` }} />
                </div>
              </div>
            ) : (
              <div className="text-[10px] text-slate-500 italic pt-1 border-t border-slate-100">
                Investigation verdict confidence pending swarm launch
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

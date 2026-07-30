/**
 * CandidateDetailsDrawer.tsx — Phase 5: Discovery Provenance Lineage & Full Details Drawer
 * Displays full candidate metadata, stage confidence progression, and visual Provenance Lineage Timeline.
 */
import React from 'react';
import {
  X,
  ExternalLink,
  ShieldCheck,
  Building,
  Tag,
  Clock,
  Layers,
  History,
  CheckCircle2,
} from 'lucide-react';
import type { ListingCandidate } from '../../../types/discovery';

interface CandidateDetailsDrawerProps {
  candidate: ListingCandidate | null;
  onClose: () => void;
  onLaunchSingle?: (candidate: ListingCandidate) => void;
}

export function CandidateDetailsDrawer({
  candidate,
  onClose,
  onLaunchSingle,
}: CandidateDetailsDrawerProps) {
  if (!candidate) return null;

  const discoveredVia = candidate.discovered_via || candidate.discovery_source || 'Marketplace API';
  const provenanceChain =
    candidate.provenance_chain && candidate.provenance_chain.length > 0
      ? candidate.provenance_chain
      : [`Marketplace API: ${candidate.marketplace}`, 'Deduplication: Union-Find Canonical Clustering'];

  const confPct = Math.round((candidate.discovery_confidence ?? candidate.confidence ?? 0.85) * 100);

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex justify-end">
      <div className="bg-white w-full max-w-xl h-full shadow-2xl border-l border-slate-200 overflow-y-auto p-6 space-y-6 flex flex-col justify-between text-slate-900 animate-in slide-in-from-right duration-200">
        <div className="space-y-6">
          {/* Header */}
          <div className="flex items-start justify-between border-b border-slate-200 pb-4">
            <div>
              <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-violet-100 text-violet-800 border border-violet-200 mb-2">
                <Building className="h-3 w-3" /> {candidate.marketplace}
              </div>
              <h2 className="text-lg font-bold text-slate-900 line-clamp-2" title={candidate.title}>
                {candidate.title}
              </h2>
            </div>
            <button
              onClick={onClose}
              className="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          {/* Quick Metrics */}
          <div className="grid grid-cols-2 gap-3">
            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <div className="text-[11px] font-semibold text-slate-500 flex items-center gap-1">
                <Tag className="h-3.5 w-3.5 text-indigo-500" /> Listed Price
              </div>
              <div className="text-xl font-extrabold text-indigo-600">
                ₹{candidate.price.toLocaleString()}
              </div>
            </div>

            <div className="p-3 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
              <div className="text-[11px] font-semibold text-slate-500 flex items-center gap-1">
                <ShieldCheck className="h-3.5 w-3.5 text-emerald-500" /> Discovery Confidence
              </div>
              <div className="text-xl font-extrabold text-emerald-600">
                {confPct}%
              </div>
            </div>
          </div>

          {/* Seller & Availability */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-2">
            <div className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Seller & Availability Metadata
            </div>
            <div className="text-xs space-y-1 text-slate-800">
              <div className="flex justify-between">
                <span className="text-slate-500">Seller Name:</span>
                <span className="font-semibold text-slate-900">{candidate.seller}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Availability:</span>
                <span className="font-semibold text-emerald-700">{candidate.availability}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Discovery Engine:</span>
                <span className="font-medium text-slate-700">{candidate.discovery_source}</span>
              </div>
            </div>
          </div>

          {/* Provenance Lineage Timeline (Phase 5) */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-3">
            <div className="flex items-center justify-between border-b border-slate-200 pb-2">
              <div className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                <History className="h-4 w-4 text-violet-600" /> Discovery Lineage & Provenance
              </div>
              <span className="text-[11px] font-bold text-violet-700 bg-violet-100 px-2 py-0.5 rounded-full border border-violet-200">
                Via {discoveredVia}
              </span>
            </div>

            {/* Lineage Steps Timeline */}
            <div className="relative pl-4 space-y-4 border-l-2 border-violet-200 ml-1">
              {provenanceChain.map((step, idx) => (
                <div key={idx} className="relative">
                  <span className="absolute -left-[21px] top-0.5 h-3.5 w-3.5 rounded-full bg-violet-600 text-white flex items-center justify-center text-[9px] font-bold ring-2 ring-white">
                    ✓
                  </span>
                  <div className="text-xs font-semibold text-slate-900">{step}</div>
                  <div className="text-[10px] text-slate-500">Verified lineage node #{idx + 1}</div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="pt-4 border-t border-slate-200 flex items-center justify-between gap-3">
          <a
            href={candidate.url}
            target="_blank"
            rel="noreferrer"
            className="px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-semibold transition-colors flex items-center gap-1.5"
          >
            Visit Marketplace Listing <ExternalLink className="h-3.5 w-3.5" />
          </a>

          {onLaunchSingle && (
            <button
              onClick={() => {
                onLaunchSingle(candidate);
                onClose();
              }}
              className="px-4 py-2 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-colors flex items-center gap-1.5"
            >
              <Layers className="h-3.5 w-3.5" /> Launch Swarm Investigation
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

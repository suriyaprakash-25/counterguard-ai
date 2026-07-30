/**
 * ListingComparisonView.tsx — Refactored to light theme design system
 * Side-by-side comparison matrix for 2-4 selected candidates.
 */
import React from 'react';
import { X, ExternalLink, ShieldCheck, Tag, Building, Package } from 'lucide-react';
import type { ListingCandidate } from '../../../types/discovery';

interface ListingComparisonViewProps {
  candidates: ListingCandidate[];
  onRemove: (id: string) => void;
  onClearAll: () => void;
}

export function ListingComparisonView({
  candidates,
  onRemove,
  onClearAll,
}: ListingComparisonViewProps) {
  if (candidates.length === 0) return null;

  const prices = candidates.map((c) => c.price);
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden mb-6">
      {/* Header toolbar */}
      <div className="p-4 bg-slate-50 border-b border-slate-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="font-semibold text-slate-900 text-sm">
            Side-by-Side Comparison ({candidates.length} of 4)
          </span>
          <span className="text-xs text-slate-500 font-medium">
            Comparing price, seller trust, and availability
          </span>
        </div>
        <button
          onClick={onClearAll}
          className="text-xs text-slate-500 hover:text-slate-800 transition-colors flex items-center gap-1 font-medium"
        >
          <X className="h-3.5 w-3.5" /> Clear comparison
        </button>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 divide-y sm:divide-y-0 sm:divide-x divide-slate-200">
        {candidates.map((c) => {
          const isMin = c.price === minPrice && candidates.length > 1;
          const isMax = c.price === maxPrice && candidates.length > 1;
          const confPct = Math.round((c.confidence ?? 0.85) * 100);

          return (
            <div key={c.id} className="p-4 bg-white space-y-4 relative flex flex-col justify-between">
              {/* Top remove button */}
              <button
                onClick={() => onRemove(c.id)}
                className="absolute top-3 right-3 text-slate-400 hover:text-slate-700 transition-colors p-1"
                title="Remove from comparison"
              >
                <X className="h-4 w-4" />
              </button>

              <div className="space-y-3">
                {/* Marketplace tag */}
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-slate-100 text-slate-800 text-xs font-semibold border border-slate-200">
                  <Package className="h-3 w-3 text-violet-600" />
                  {c.marketplace}
                </div>

                {/* Title */}
                <h4 className="font-semibold text-slate-900 text-sm line-clamp-2" title={c.title}>
                  {c.title}
                </h4>

                {/* Price tag */}
                <div className="space-y-1">
                  <div className="text-xs text-slate-500 font-medium flex items-center gap-1">
                    <Tag className="h-3.5 w-3.5 text-slate-400" /> Listed Price
                  </div>
                  <div className="text-xl font-bold text-indigo-600 flex items-center gap-2">
                    ₹{c.price.toLocaleString()}
                    {isMin && (
                      <span className="text-[10px] bg-red-100 text-red-800 border border-red-200 font-semibold px-1.5 py-0.5 rounded">
                        Lowest
                      </span>
                    )}
                    {isMax && (
                      <span className="text-[10px] bg-emerald-100 text-emerald-800 border border-emerald-200 font-semibold px-1.5 py-0.5 rounded">
                        Highest
                      </span>
                    )}
                  </div>
                </div>

                {/* Seller */}
                <div className="space-y-1">
                  <div className="text-xs text-slate-500 font-medium flex items-center gap-1">
                    <Building className="h-3.5 w-3.5 text-slate-400" /> Seller Name
                  </div>
                  <div className="text-xs font-medium text-slate-800 truncate" title={c.seller}>
                    {c.seller}
                  </div>
                </div>

                {/* Confidence */}
                <div className="space-y-1">
                  <div className="text-xs text-slate-500 font-medium flex items-center gap-1">
                    <ShieldCheck className="h-3.5 w-3.5 text-slate-400" /> Match Quality
                  </div>
                  <div className="text-xs font-semibold text-emerald-700 flex items-center gap-1">
                    {confPct}% Confidence
                  </div>
                </div>
              </div>

              {/* View URL link */}
              <div className="pt-2 border-t border-slate-100">
                <a
                  href={c.url}
                  target="_blank"
                  rel="noreferrer"
                  className="w-full py-1.5 px-3 rounded-lg border border-slate-200 bg-slate-50 hover:bg-slate-100 text-slate-700 text-xs font-medium transition-colors flex items-center justify-center gap-1"
                >
                  Visit Listing <ExternalLink className="h-3 w-3" />
                </a>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}

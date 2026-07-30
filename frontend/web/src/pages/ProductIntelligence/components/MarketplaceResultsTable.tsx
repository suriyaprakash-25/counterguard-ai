/**
 * MarketplaceResultsTable.tsx — Phases 4, 6, 7 & 9: Enterprise Data Table
 * Includes Priority Badges (CRITICAL, HIGH, MEDIUM, LOW), Priority Sorting,
 * Marketplace Brand Chips, Confidence Inspector Popover, and Enterprise Quick Actions.
 */
import React, { useState, useMemo } from 'react';
import {
  ExternalLink,
  TrendingDown,
  Scale,
  ArrowUpDown,
  CheckSquare,
  Square,
  Building,
  AlertTriangle,
  Layers,
  Eye,
  MoreHorizontal,
} from 'lucide-react';

import type { ListingCandidate, InvestigationPriority } from '../../../types/discovery';
import { ConfidenceInspectorPopover } from './ConfidenceInspectorPopover';

const MARKETPLACE_BRANDING: Record<
  string,
  { dot: string; bg: string; text: string; border: string }
> = {
  Amazon:     { dot: 'bg-amber-500', bg: 'bg-amber-50', text: 'text-amber-900', border: 'border-amber-200' },
  Flipkart:   { dot: 'bg-blue-500', bg: 'bg-blue-50', text: 'text-blue-900', border: 'border-blue-200' },
  Meesho:     { dot: 'bg-pink-500', bg: 'bg-pink-50', text: 'text-pink-900', border: 'border-pink-200' },
  TradeIndia: { dot: 'bg-emerald-500', bg: 'bg-emerald-50', text: 'text-emerald-900', border: 'border-emerald-200' },
  AJIO:       { dot: 'bg-purple-500', bg: 'bg-purple-50', text: 'text-purple-900', border: 'border-purple-200' },
  Myntra:     { dot: 'bg-rose-500', bg: 'bg-rose-50', text: 'text-rose-900', border: 'border-rose-200' },
};

function computeCandidatePriority(candidate: ListingCandidate, avgPrice: number | null): InvestigationPriority {
  const isAnomaly = Boolean(candidate.metadata?.price_anomaly) || (avgPrice && candidate.price < 0.5 * avgPrice);
  const isMeeshoOrTradeIndia = candidate.marketplace === 'Meesho' || candidate.marketplace === 'TradeIndia';

  if (isAnomaly && isMeeshoOrTradeIndia) return 'critical';
  if (isAnomaly || isMeeshoOrTradeIndia) return 'high';
  if (candidate.price < 1000) return 'normal';
  return 'low';
}

interface MarketplaceResultsTableProps {
  candidates: ListingCandidate[];
  selectedIds: Set<string>;
  onToggleSelect: (id: string) => void;
  onSelectAll: () => void;
  onClearSelection: () => void;
  comparisonSet: Set<string>;
  onToggleCompare: (candidate: ListingCandidate) => void;
  onViewDetails: (candidate: ListingCandidate) => void;
  onLaunchSingle: (candidate: ListingCandidate) => void;
  groupPriceAvg?: number | null;
}

type SortField = 'priority' | 'marketplace' | 'price' | 'confidence' | 'seller';

export function MarketplaceResultsTable({
  candidates,
  selectedIds,
  onToggleSelect,
  onSelectAll,
  onClearSelection,
  comparisonSet,
  onToggleCompare,
  onViewDetails,
  onLaunchSingle,
  groupPriceAvg = null,
}: MarketplaceResultsTableProps) {
  const [sortField, setSortField] = useState<SortField>('priority');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('asc');

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDir(field === 'priority' ? 'asc' : 'desc');
    }
  };

  const PRIORITY_RANK: Record<InvestigationPriority, number> = {
    critical: 0,
    high: 1,
    normal: 2,
    low: 3,
  };

  const sortedCandidates = useMemo(() => {
    return [...candidates].sort((a, b) => {
      const pA = computeCandidatePriority(a, groupPriceAvg);
      const pB = computeCandidatePriority(b, groupPriceAvg);

      const mult = sortDir === 'asc' ? 1 : -1;

      if (sortField === 'priority') return (PRIORITY_RANK[pA] - PRIORITY_RANK[pB]) * mult;
      if (sortField === 'price') return (a.price - b.price) * mult;
      if (sortField === 'confidence') return ((a.confidence ?? 0.85) - (b.confidence ?? 0.85)) * mult;
      if (sortField === 'marketplace') return a.marketplace.localeCompare(b.marketplace) * mult;
      if (sortField === 'seller') return a.seller.localeCompare(b.seller) * mult;
      return 0;
    });
  }, [candidates, sortField, sortDir, groupPriceAvg]);

  const allSelected = candidates.length > 0 && selectedIds.size === candidates.length;

  return (
    <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden">
      {/* Table toolbar */}
      <div className="p-3.5 bg-slate-50 border-b border-slate-200 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <button
            onClick={allSelected ? onClearSelection : onSelectAll}
            className="flex items-center gap-2 text-xs font-semibold text-slate-700 hover:text-slate-900 transition-colors"
          >
            {allSelected ? (
              <CheckSquare className="h-4 w-4 text-violet-600" />
            ) : (
              <Square className="h-4 w-4 text-slate-400" />
            )}
            {selectedIds.size > 0
              ? `${selectedIds.size} of ${candidates.length} selected`
              : 'Select all'}
          </button>
          {selectedIds.size > 0 && (
            <button
              onClick={onClearSelection}
              className="text-xs text-slate-500 hover:text-slate-800 transition-colors font-medium"
            >
              Clear selection
            </button>
          )}
        </div>
        <div className="text-xs text-slate-500 flex items-center gap-1 font-medium">
          <Scale className="h-3.5 w-3.5 text-violet-600" /> Click compare icon to build side-by-side view (max 4)
        </div>
      </div>

      {/* Main data table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-900" role="table" aria-label="Discovered Candidates Table">
          <thead className="bg-slate-100/90 border-b border-slate-200 text-slate-700 font-semibold uppercase tracking-wider">
            <tr>
              <th className="p-3 w-10 text-center">#</th>
              <th className="p-3 cursor-pointer hover:bg-slate-200/60 transition-colors" onClick={() => handleSort('priority')}>
                <div className="flex items-center gap-1">
                  Priority <ArrowUpDown className="h-3 w-3 text-slate-400" />
                </div>
              </th>
              <th className="p-3 cursor-pointer hover:bg-slate-200/60 transition-colors" onClick={() => handleSort('marketplace')}>
                <div className="flex items-center gap-1">
                  Marketplace <ArrowUpDown className="h-3 w-3 text-slate-400" />
                </div>
              </th>
              <th className="p-3">Product Title</th>
              <th className="p-3 cursor-pointer hover:bg-slate-200/60 transition-colors" onClick={() => handleSort('price')}>
                <div className="flex items-center gap-1">
                  Price <ArrowUpDown className="h-3 w-3 text-slate-400" />
                </div>
              </th>
              <th className="p-3 cursor-pointer hover:bg-slate-200/60 transition-colors" onClick={() => handleSort('seller')}>
                <div className="flex items-center gap-1">
                  Seller <ArrowUpDown className="h-3 w-3 text-slate-400" />
                </div>
              </th>
              <th className="p-3 cursor-pointer hover:bg-slate-200/60 transition-colors" onClick={() => handleSort('confidence')}>
                <div className="flex items-center gap-1">
                  Confidence Breakdown <ArrowUpDown className="h-3 w-3 text-slate-400" />
                </div>
              </th>
              <th className="p-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {sortedCandidates.map((c) => {
              const isSelected = selectedIds.has(c.id);
              const isCompared = comparisonSet.has(c.id);

              const brand = MARKETPLACE_BRANDING[c.marketplace] ?? {
                dot: 'bg-slate-500',
                bg: 'bg-slate-100',
                text: 'text-slate-800',
                border: 'border-slate-200',
              };

              const priority = computeCandidatePriority(c, groupPriceAvg);
              const isCritical = priority === 'critical';
              const isHigh = priority === 'high';

              const priorityBadge =
                isCritical
                  ? 'bg-red-100 text-red-900 border-red-300 font-extrabold'
                  : isHigh
                  ? 'bg-orange-100 text-orange-900 border-orange-300 font-bold'
                  : priority === 'normal'
                  ? 'bg-blue-100 text-blue-900 border-blue-200 font-semibold'
                  : 'bg-slate-100 text-slate-700 border-slate-200 font-medium';

              const isAnomaly = Boolean(c.metadata?.price_anomaly);

              return (
                <tr
                  key={c.id}
                  id={`listing-row-${c.id}`}
                  className={`transition-colors ${
                    isCritical
                      ? 'bg-red-50/40 hover:bg-red-50/70 border-l-4 border-l-red-500'
                      : isSelected
                      ? 'bg-violet-50/70'
                      : 'hover:bg-slate-50/80'
                  }`}
                >
                  {/* Select Checkbox */}
                  <td className="p-3 text-center">
                    <button
                      onClick={() => onToggleSelect(c.id)}
                      className="text-slate-400 hover:text-violet-600 transition-colors"
                      aria-label={`Select ${c.title}`}
                    >
                      {isSelected ? (
                        <CheckSquare className="h-4 w-4 text-violet-600" />
                      ) : (
                        <Square className="h-4 w-4" />
                      )}
                    </button>
                  </td>

                  {/* Priority Badge */}
                  <td className="p-3 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded-full text-[10px] uppercase border ${priorityBadge}`}>
                      {priority}
                    </span>
                  </td>

                  {/* Marketplace Branding */}
                  <td className="p-3 font-semibold whitespace-nowrap">
                    <div className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs border ${brand.bg} ${brand.text} ${brand.border}`}>
                      <span className={`h-2 w-2 rounded-full ${brand.dot}`} />
                      {c.marketplace}
                    </div>
                  </td>

                  {/* Product Title */}
                  <td className="p-3 max-w-xs">
                    <button
                      onClick={() => onViewDetails(c)}
                      className="font-medium text-slate-900 hover:text-violet-700 hover:underline text-left line-clamp-1"
                      title={c.title}
                    >
                      {c.title}
                    </button>
                    {c.discovery_source && (
                      <div className="text-[10px] text-slate-500 truncate">
                        {c.discovery_source}
                      </div>
                    )}
                  </td>

                  {/* Price */}
                  <td className="p-3 whitespace-nowrap">
                    <div className="font-bold text-indigo-600">
                      ₹{c.price.toLocaleString()}
                    </div>
                    {isAnomaly && (
                      <span className="inline-flex items-center gap-1 text-[10px] font-semibold text-red-600 bg-red-50 border border-red-200 px-1.5 py-0.5 rounded">
                        <TrendingDown className="h-3 w-3" /> Price anomaly
                      </span>
                    )}
                  </td>

                  {/* Seller */}
                  <td className="p-3 text-slate-700 max-w-[150px] truncate">
                    <div className="flex items-center gap-1">
                      <Building className="h-3 w-3 text-slate-400 shrink-0" />
                      <span className="truncate">{c.seller}</span>
                    </div>
                  </td>

                  {/* Multi-Stage Confidence Inspector (Phase 4) */}
                  <td className="p-3 whitespace-nowrap">
                    <ConfidenceInspectorPopover candidate={c} />
                  </td>

                  {/* Enterprise Quick Actions (Phase 9) */}
                  <td className="p-3 text-right whitespace-nowrap">
                    <div className="flex items-center justify-end gap-1.5">
                      {/* View Details */}
                      <button
                        onClick={() => onViewDetails(c)}
                        title="View Full Provenance Details & Lineage"
                        className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors"
                      >
                        <Eye className="h-3.5 w-3.5" />
                      </button>

                      {/* Compare */}
                      <button
                        onClick={() => onToggleCompare(c)}
                        title={isCompared ? 'Remove from compare' : 'Add to side-by-side comparison'}
                        className={`p-1.5 rounded-lg border transition-colors ${
                          isCompared
                            ? 'bg-violet-100 border-violet-300 text-violet-700 font-semibold'
                            : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                        }`}
                      >
                        <Scale className="h-3.5 w-3.5" />
                      </button>

                      {/* Launch Single */}
                      <button
                        onClick={() => onLaunchSingle(c)}
                        title="Launch Swarm Investigation"
                        className="p-1.5 rounded-lg border border-violet-200 bg-violet-50 text-violet-700 hover:bg-violet-100 transition-colors"
                      >
                        <Layers className="h-3.5 w-3.5" />
                      </button>

                      {/* Open Marketplace URL */}
                      <a
                        href={c.url}
                        target="_blank"
                        rel="noreferrer"
                        className="p-1.5 rounded-lg border border-slate-200 bg-white text-slate-600 hover:bg-slate-100 hover:text-slate-900 transition-colors inline-flex items-center"
                        title="Open external URL"
                      >
                        <ExternalLink className="h-3.5 w-3.5" />
                      </a>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}

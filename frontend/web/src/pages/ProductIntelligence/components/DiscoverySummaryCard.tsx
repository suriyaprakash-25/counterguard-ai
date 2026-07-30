/**
 * DiscoverySummaryCard.tsx — Refactored to light theme design system
 * Displays high-level stats: candidate counts, deduplication metrics, top target count.
 */
import React from 'react';
import { Package, GitMerge, ShieldAlert, Layers } from 'lucide-react';

interface DiscoverySummaryCardProps {
  totalCandidates: number;
  totalGroups: number;
  dedupReduction: number;
  topTargetsCount: number;
  isMemoryHit?: boolean;
}

export function DiscoverySummaryCard({
  totalCandidates,
  totalGroups,
  dedupReduction,
  topTargetsCount,
  isMemoryHit = false,
}: DiscoverySummaryCardProps) {
  const cards = [
    {
      id: 'stat-total-candidates',
      label: 'Discovered Listings',
      value: totalCandidates,
      icon: Package,
      iconBg: 'bg-violet-100 text-violet-700',
      borderAccent: 'border-l-4 border-l-violet-500',
    },
    {
      id: 'stat-product-groups',
      label: 'Unique Product Groups',
      value: totalGroups,
      icon: Layers,
      iconBg: 'bg-blue-100 text-blue-700',
      borderAccent: 'border-l-4 border-l-blue-500',
    },
    {
      id: 'stat-dedup-removed',
      label: 'Duplicates Merged',
      value: dedupReduction,
      icon: GitMerge,
      iconBg: 'bg-emerald-100 text-emerald-700',
      borderAccent: 'border-l-4 border-l-emerald-500',
    },
    {
      id: 'stat-top-targets',
      label: 'High Priority Targets',
      value: topTargetsCount,
      icon: ShieldAlert,
      iconBg: 'bg-amber-100 text-amber-700',
      borderAccent: 'border-l-4 border-l-amber-500',
    },
  ];

  return (
    <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
      {cards.map((c) => {
        const Icon = c.icon;
        return (
          <div
            key={c.id}
            id={c.id}
            className={`bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center gap-3 transition-all hover:shadow-md ${c.borderAccent}`}
          >
            <div className={`p-2.5 rounded-lg shrink-0 ${c.iconBg}`}>
              <Icon className="h-5 w-5" />
            </div>
            <div>
              <div className="text-2xl font-bold text-slate-900 leading-tight">
                {c.value}
              </div>
              <div className="text-xs font-medium text-slate-600">
                {c.label}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

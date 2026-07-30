/**
 * SOCAnalyticsWidgets.tsx — Phase 10: Enterprise SOC Analytics & Threat Telemetry
 * Renders Marketplace Risk Distribution, Risk Histograms, Confidence Spread, and Execution Telemetry.
 */
import React from 'react';
import { BarChart3, PieChart, TrendingUp, ShieldAlert, Zap } from 'lucide-react';
import type { DiscoverySearchResponse } from '../../../types/discovery';

interface SOCAnalyticsWidgetsProps {
  searchResult: DiscoverySearchResponse | null;
}

export function SOCAnalyticsWidgets({ searchResult }: SOCAnalyticsWidgetsProps) {
  if (!searchResult) return null;

  const candidates = searchResult.candidates ?? [];
  const listingGroups = searchResult.listing_groups ?? [];

  // Group candidate risk counts
  const mpRiskMap: Record<string, { total: number; avgPrice: number }> = {};
  candidates.forEach((c) => {
    if (!mpRiskMap[c.marketplace]) {
      mpRiskMap[c.marketplace] = { total: 0, avgPrice: 0 };
    }
    mpRiskMap[c.marketplace].total += 1;
    mpRiskMap[c.marketplace].avgPrice += c.price;
  });

  const mpEntries = Object.entries(mpRiskMap);

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
      {/* Widget 1: Marketplace Risk Distribution */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-4 w-4 text-violet-600 dark:text-violet-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
              Marketplace Threat Distribution
            </h3>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">{mpEntries.length} Platforms</span>
        </div>

        <div className="space-y-2">
          {mpEntries.map(([mp, data]) => {
            const pct = Math.round((data.total / (candidates.length || 1)) * 100);
            return (
              <div key={mp} className="space-y-1 text-xs">
                <div className="flex justify-between text-slate-700 dark:text-slate-300 font-medium">
                  <span>{mp}</span>
                  <span>{data.total} listing(s) ({pct}%)</span>
                </div>
                <div className="w-full bg-slate-100 dark:bg-slate-800 h-2 rounded-full overflow-hidden">
                  <div className="bg-violet-600 h-full rounded-full" style={{ width: `${pct}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Widget 2: Discovery Source & Deduplication Analytics */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-3">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
          <div className="flex items-center gap-2">
            <PieChart className="h-4 w-4 text-emerald-600 dark:text-emerald-400" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
              Telemetry & Deduplication Efficiency
            </h3>
          </div>
          <span className="text-[10px] text-slate-500 font-mono">{searchResult.metadata?.duration_ms}ms Execution</span>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
            <div className="text-slate-500 text-[11px] font-semibold">Total Raw Discovered</div>
            <div className="text-xl font-bold text-slate-900 dark:text-white">{candidates.length}</div>
          </div>
          <div className="p-3 bg-slate-50 dark:bg-slate-800/60 rounded-xl border border-slate-200 dark:border-slate-800 space-y-1">
            <div className="text-slate-500 text-[11px] font-semibold">Canonical Product Clusters</div>
            <div className="text-xl font-bold text-violet-600 dark:text-violet-400">{listingGroups.length}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

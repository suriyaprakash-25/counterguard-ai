/**
 * ThreatOverviewHeader.tsx — Executive Threat Overview KPI Banner
 * Renders high-level threat metrics, active fraud ring counts, seller risk index, and enforcement orders.
 */
import React from 'react';
import { ShieldAlert, Users, Network, FileCheck, TrendingUp, AlertTriangle } from 'lucide-react';

interface ThreatOverviewHeaderProps {
  threatIndex?: number;
  activeRingsCount?: number;
  highRiskSellersCount?: number;
  takedownsCount?: number;
}

export function ThreatOverviewHeader({
  threatIndex = 78,
  activeRingsCount = 2,
  highRiskSellersCount = 8,
  takedownsCount = 14,
}: ThreatOverviewHeaderProps) {
  const isHigh = threatIndex >= 70;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {/* Metric 1: Global Threat Index */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500">Global Threat Index</span>
          <div className="p-1.5 rounded-lg bg-red-100 dark:bg-red-950 text-red-600 dark:text-red-400">
            <ShieldAlert className="h-4 w-4" />
          </div>
        </div>
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-slate-900 dark:text-white">{threatIndex}/100</span>
          <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${isHigh ? 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300' : 'bg-amber-100 text-amber-700'}`}>
            {isHigh ? 'HIGH RISK' : 'MEDIUM'}
          </span>
        </div>
        <div className="w-full bg-slate-100 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
          <div className="bg-red-600 h-full rounded-full" style={{ width: `${threatIndex}%` }} />
        </div>
      </div>

      {/* Metric 2: Active Fraud Rings */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500">Active Fraud Rings</span>
          <div className="p-1.5 rounded-lg bg-violet-100 dark:bg-violet-950 text-violet-600 dark:text-violet-400">
            <Network className="h-4 w-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-slate-900 dark:text-white">{activeRingsCount} Syndicates</div>
        <div className="text-[11px] text-slate-500 font-medium flex items-center gap-1">
          <TrendingUp className="h-3 w-3 text-red-500" />
          <span>Surat & Delhi Clusters Active</span>
        </div>
      </div>

      {/* Metric 3: High Risk Sellers */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500">High Risk Merchants</span>
          <div className="p-1.5 rounded-lg bg-amber-100 dark:bg-amber-950 text-amber-600 dark:text-amber-400">
            <Users className="h-4 w-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-slate-900 dark:text-white">{highRiskSellersCount} Merchants</div>
        <div className="text-[11px] text-slate-500 font-medium">Cross-Marketplace Accounts</div>
      </div>

      {/* Metric 4: Verified Takedowns */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-xs font-semibold text-slate-500">Enforcement Actions</span>
          <div className="p-1.5 rounded-lg bg-emerald-100 dark:bg-emerald-950 text-emerald-600 dark:text-emerald-400">
            <FileCheck className="h-4 w-4" />
          </div>
        </div>
        <div className="text-2xl font-bold text-slate-900 dark:text-white">{takedownsCount} Takedowns</div>
        <div className="text-[11px] text-slate-500 font-medium text-emerald-600 dark:text-emerald-400">Legal Evidence Bundles</div>
      </div>
    </div>
  );
}

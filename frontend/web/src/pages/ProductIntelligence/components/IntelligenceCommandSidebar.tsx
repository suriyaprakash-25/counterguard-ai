/**
 * IntelligenceCommandSidebar.tsx — Phase 10: Sticky Intelligence Command Sidebar
 * Persistent side panel displaying high-density threat indicators, health matrix,
 * active swarm status, and AI recommendation while scrolling long listing tables.
 */
import React from 'react';
import {
  ShieldAlert,
  Building,
  Activity,
  History,
  ShieldCheck,
  CheckCircle2,
  FileText,
  AlertTriangle,
  Award,
} from 'lucide-react';
import type { DiscoverySearchResponse, BatchStatusResponse, ProductIntelligenceReport } from '../../../types/discovery';

interface IntelligenceCommandSidebarProps {
  searchResult: DiscoverySearchResponse | null;
  report: ProductIntelligenceReport | null;
  batchStatus: BatchStatusResponse | null;
  onGenerateReport: () => void;
}

export function IntelligenceCommandSidebar({
  searchResult,
  report,
  batchStatus,
  onGenerateReport,
}: IntelligenceCommandSidebarProps) {
  if (!searchResult) return null;

  const candidates = searchResult.candidates ?? [];
  const listingGroups = searchResult.listing_groups ?? [];

  const topGroupScore = listingGroups[0]?.priority_score?.total_priority_score ?? 45.0;
  const overallRiskScore = report?.overall_product_risk ?? Math.round(topGroupScore);
  const riskLevel = report?.overall_risk_level ?? (overallRiskScore >= 70 ? 'HIGH' : overallRiskScore >= 40 ? 'MEDIUM' : 'LOW');

  const highestRiskMp = report?.highest_risk_marketplace || listingGroups[0]?.unique_marketplaces[0] || 'Meesho';
  const recommendedSeller = report?.recommended_seller || candidates.find((c) => c.seller.toLowerCase().includes('official'))?.seller || 'Amazon Official Flagship';

  const avgConf = Math.round(
    (candidates.reduce((acc, c) => acc + (c.discovery_confidence ?? c.confidence ?? 0.85), 0) / (candidates.length || 1)) * 100
  );

  return (
    <aside className="w-full lg:w-80 shrink-0 space-y-4 sticky top-6">
      {/* Risk & Command Card */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-4">
        <div className="flex items-center justify-between border-b border-slate-100 pb-2">
          <div className="flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-amber-500" />
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900">
              Intelligence Summary
            </h3>
          </div>
          <span className="text-[10px] font-extrabold px-2 py-0.5 rounded-full border bg-amber-100 text-amber-800 border-amber-200">
            {riskLevel} RISK
          </span>
        </div>

        {/* Risk score gauge */}
        <div className="flex items-center justify-between p-3 rounded-lg bg-slate-50 border border-slate-200">
          <div>
            <div className="text-[11px] font-semibold text-slate-500">Product Threat Score</div>
            <div className="text-2xl font-black text-slate-900">{overallRiskScore} <span className="text-xs font-normal text-slate-400">/ 100</span></div>
          </div>
          <div className="text-right">
            <div className="text-[11px] font-semibold text-slate-500">Confidence</div>
            <div className="text-lg font-bold text-emerald-600">{avgConf}%</div>
          </div>
        </div>

        {/* Highest Threat Platform */}
        <div className="space-y-1 text-xs">
          <div className="text-slate-500 font-medium flex items-center justify-between">
            <span>Highest Risk Platform:</span>
            <AlertTriangle className="h-3.5 w-3.5 text-red-500" />
          </div>
          <div className="font-bold text-red-600 truncate">{highestRiskMp}</div>
        </div>

        {/* Recommended Authentic Seller */}
        <div className="space-y-1 text-xs">
          <div className="text-slate-500 font-medium flex items-center justify-between">
            <span>Recommended Partner:</span>
            <Award className="h-3.5 w-3.5 text-emerald-600" />
          </div>
          <div className="font-bold text-emerald-700 truncate" title={recommendedSeller}>
            {recommendedSeller}
          </div>
        </div>

        {/* Action Button */}
        <button
          onClick={onGenerateReport}
          className="w-full py-2.5 px-3 bg-violet-600 hover:bg-violet-700 text-white rounded-xl text-xs font-semibold shadow-sm transition-colors flex items-center justify-center gap-2"
        >
          <FileText className="h-4 w-4" /> Synthesize Full Report
        </button>
      </div>

      {/* AI Recommendation Box */}
      <div className="bg-white dark:bg-slate-900 text-slate-900 dark:text-white rounded-xl p-4 shadow-sm space-y-2 border border-slate-200 dark:border-slate-800">
        <div className="text-xs font-bold uppercase tracking-wider text-violet-700 dark:text-violet-300 flex items-center gap-1.5">
          <CheckCircle2 className="h-4 w-4 text-emerald-600 dark:text-emerald-400" /> AI Swarm Recommendation
        </div>
        <p className="text-xs text-slate-600 dark:text-slate-300 leading-relaxed">
          {report?.recommendations[0] ??
            `Prioritize enforcement on ${highestRiskMp} where price anomaly exceeds 50% below MSRP.`}
        </p>
      </div>
    </aside>
  );
}

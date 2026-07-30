/**
 * ProductIntelligenceReportView.tsx — Refactored to light theme design system
 * Executive modal / full report view showing risk score gauge, safe vs suspicious breakdown,
 * highest risk marketplace, recommended seller, key evidence, and investigation case drill-downs.
 */
import React from 'react';
import {
  X,
  ShieldAlert,
  ShieldCheck,
  Building,
  ExternalLink,
  Award,
  AlertTriangle,
  FileText,
  CheckCircle,
} from 'lucide-react';
import type { ProductIntelligenceReport } from '../../../types/discovery';

interface ProductIntelligenceReportViewProps {
  report: ProductIntelligenceReport;
  onClose: () => void;
  onNavigateToCase?: (invId: str) => void;
}

export function ProductIntelligenceReportView({
  report,
  onClose,
  onNavigateToCase,
}: ProductIntelligenceReportViewProps) {
  const isHighRisk = report.overall_risk_level === 'HIGH' || report.overall_risk_level === 'CRITICAL';
  const isMediumRisk = report.overall_risk_level === 'MEDIUM';

  const riskBadgeClass = isHighRisk
    ? 'bg-red-100 text-red-900 border-red-300'
    : isMediumRisk
    ? 'bg-amber-100 text-amber-900 border-amber-300'
    : 'bg-emerald-100 text-emerald-900 border-emerald-300';

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
      <div className="bg-white border border-slate-200 rounded-2xl shadow-2xl w-full max-w-4xl max-h-[90vh] overflow-y-auto text-slate-900 flex flex-col">
        {/* Header */}
        <div className="p-6 bg-slate-900 text-white flex items-start justify-between border-b border-slate-800">
          <div>
            <div className="flex items-center gap-3">
              <span className="p-2 rounded-xl bg-violet-600/30 text-violet-300 border border-violet-500/40">
                <FileText className="h-6 w-6" />
              </span>
              <div>
                <h2 className="text-xl font-bold tracking-tight">
                  Product Intelligence Report
                </h2>
                <div className="text-xs text-slate-400 mt-0.5">
                  Target Product: <span className="font-semibold text-violet-300">{report.product_name}</span> • Generated {new Date(report.generated_at).toLocaleString()}
                </div>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Body content */}
        <div className="p-6 space-y-6 bg-slate-50/50 flex-1">
          {/* Executive Summary Callout */}
          <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm space-y-2">
            <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Executive Coordinator Summary
            </div>
            <p className="text-sm text-slate-800 leading-relaxed">
              {report.coordinator_summary}
            </p>
          </div>

          {/* Core Metric Cards Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-4 gap-4">
            {/* Overall Risk Score */}
            <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm space-y-2">
              <div className="text-xs font-medium text-slate-500">Overall Product Risk</div>
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-extrabold text-slate-900">
                  {report.overall_product_risk}
                </span>
                <span className="text-xs text-slate-400">/ 100</span>
              </div>
              <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-bold border ${riskBadgeClass}`}>
                {report.overall_risk_level} RISK
              </span>
            </div>

            {/* Total Audited */}
            <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm space-y-2">
              <div className="text-xs font-medium text-slate-500">Audited Listings</div>
              <div className="text-3xl font-bold text-slate-900">{report.total_listings}</div>
              <div className="text-xs text-slate-600 flex items-center gap-1.5">
                <span className="text-emerald-600 font-semibold">{report.safe_listings}</span>
                <span>Safe</span>
                <span>•</span>
                <span className="text-red-600 font-semibold">{report.suspicious_listings}</span>
                <span>Suspicious</span>
              </div>
            </div>

            {/* Highest Risk Marketplace */}
            <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm space-y-2">
              <div className="text-xs font-medium text-slate-500">Highest Risk Platform</div>
              <div className="text-lg font-bold text-red-600 flex items-center gap-1.5 truncate">
                <AlertTriangle className="h-4 w-4 shrink-0 text-red-500" />
                {report.highest_risk_marketplace || 'N/A'}
              </div>
              <div className="text-xs text-slate-500">Highest threat concentration</div>
            </div>

            {/* Recommended Seller */}
            <div className="p-4 bg-white border border-slate-200 rounded-xl shadow-sm space-y-2">
              <div className="text-xs font-medium text-slate-500">Recommended Seller</div>
              <div className="text-sm font-bold text-emerald-700 flex items-center gap-1.5 truncate" title={report.recommended_seller}>
                <Award className="h-4 w-4 shrink-0 text-emerald-600" />
                {report.recommended_seller || 'Verified Brand Outlet'}
              </div>
              <div className="text-xs text-slate-500">Official authentic partner</div>
            </div>
          </div>

          {/* Key Evidence & Recommendations Section */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Key Evidence Summary */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 uppercase tracking-wider border-b border-slate-100 pb-2">
                <ShieldAlert className="h-4 w-4 text-amber-500" /> Primary Risk Factors Identified
              </div>
              <ul className="space-y-2">
                {report.evidence_summary.map((item, idx) => (
                  <li key={idx} className="text-xs text-slate-700 flex items-start gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Enforcement Recommendations */}
            <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-700 uppercase tracking-wider border-b border-slate-100 pb-2">
                <CheckCircle className="h-4 w-4 text-emerald-500" /> Enforcement Action Plan
              </div>
              <ul className="space-y-2">
                {report.recommendations.map((item, idx) => (
                  <li key={idx} className="text-xs text-slate-700 flex items-start gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 mt-1.5 shrink-0" />
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Individual Investigations Breakdown Table */}
          <div className="bg-white border border-slate-200 rounded-xl shadow-sm overflow-hidden space-y-3 p-4">
            <div className="text-xs font-semibold text-slate-700 uppercase tracking-wider">
              Investigated Cases Breakdown ({report.investigations.length})
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs text-slate-900">
                <thead className="bg-slate-100 text-slate-700 font-semibold uppercase tracking-wider">
                  <tr>
                    <th className="p-2.5">Platform</th>
                    <th className="p-2.5">Title</th>
                    <th className="p-2.5">Seller</th>
                    <th className="p-2.5">Price</th>
                    <th className="p-2.5">Verdict Risk</th>
                    <th className="p-2.5 text-right">Drill-Down</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100">
                  {report.investigations.map((inv) => {
                    const isCaseHigh = inv.verdict === 'HIGH' || inv.verdict === 'CRITICAL';
                    return (
                      <tr key={inv.investigation_id} className="hover:bg-slate-50 transition-colors">
                        <td className="p-2.5 font-semibold text-slate-900">{inv.marketplace}</td>
                        <td className="p-2.5 max-w-xs truncate font-medium" title={inv.title}>{inv.title}</td>
                        <td className="p-2.5 text-slate-600 max-w-[120px] truncate">{inv.seller}</td>
                        <td className="p-2.5 font-bold text-indigo-600">₹{inv.price.toLocaleString()}</td>
                        <td className="p-2.5">
                          <span
                            className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${
                              isCaseHigh
                                ? 'bg-red-100 text-red-800 border-red-200'
                                : 'bg-emerald-100 text-emerald-800 border-emerald-200'
                            }`}
                          >
                            {inv.risk_score}/100 ({inv.verdict})
                          </span>
                        </td>
                        <td className="p-2.5 text-right">
                          <button
                            onClick={() => onNavigateToCase?.(inv.investigation_id)}
                            className="px-2.5 py-1 bg-violet-50 hover:bg-violet-100 text-violet-700 border border-violet-200 rounded-lg text-xs font-semibold transition-colors inline-flex items-center gap-1"
                          >
                            View Case <ExternalLink className="h-3 w-3" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-100 border-t border-slate-200 flex items-center justify-between text-xs text-slate-600">
          <div>CounterGuard Intelligence Engine • v2.5</div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-900 text-white font-semibold rounded-xl text-xs transition-colors"
          >
            Close Report
          </button>
        </div>
      </div>
    </div>
  );
}

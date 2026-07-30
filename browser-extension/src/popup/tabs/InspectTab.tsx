/**
 * InspectTab.tsx — Threat Inspection Tab (lazy-loaded)
 * Contains: active target card, analyze button, live investigation workflow,
 * SOC telemetry grid, trusted alternatives panel, and action buttons.
 * Optimized with React.memo to prevent unnecessary re-renders.
 */

import { memo } from "react";
import {
  Globe,
  Lock,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Search,
  Database,
  FileDown,
  PlusCircle,
  ExternalLink,
  ShieldCheck,
  Zap,
  XCircle,
  Clock,
  Check,
  Star,
  ArrowUpDown,
  Filter,
  RefreshCw,
} from "lucide-react";
import { InspectTabProps } from "../PopupPage";

export const InspectTab = memo(function InspectTab({
  page,
  tabLoading,
  analysis,
  analyzing,
  creatingInv,
  liveInv,
  errorMsg,
  altFilter,
  altSort,
  processedAlternatives,
  onAnalyze,
  onCreateInvestigation,
  onCancelInvestigation,
  onOpenDashboardReport,
  onExportReport,
  onSetAltFilter,
  onSetAltSort,
}: InspectTabProps) {
  return (
    <div className="p-3.5 space-y-3 animate-fadeInScale">
      {/* ── Active Target Site Card ── */}
      <section
        className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2"
        aria-label="Target website information"
      >
        <div className="flex items-center justify-between text-[9px] text-slate-400 uppercase tracking-wider font-mono">
          <span className="flex items-center gap-1">
            <Globe className="h-3 w-3 text-purple-400" aria-hidden="true" />
            Target Website &amp; Product
          </span>
          {page?.isSecure && (
            <span className="flex items-center gap-1 text-emerald-400 font-semibold" aria-label="SSL Secure connection">
              <Lock className="h-3 w-3" aria-hidden="true" />
              SSL SECURE
            </span>
          )}
        </div>

        {tabLoading ? (
          <div className="h-10 animate-pulse bg-slate-800/60 rounded" aria-label="Loading page information" />
        ) : page ? (
          <div className="space-y-1.5">
            <div className="flex items-center gap-2">
              {page.faviconUrl && (
                <img src={page.faviconUrl} alt="" className="h-4 w-4 rounded shrink-0" aria-hidden="true" />
              )}
              <h2 className="text-xs font-bold text-white truncate max-w-[320px]" title={page.title}>
                {page.title}
              </h2>
            </div>
            <p className="text-[10px] font-mono text-purple-300 truncate" title={page.domain}>
              {page.domain}
            </p>

            {page.isSupportedMarketplace && page.detection && (
              <div className="flex flex-wrap gap-1.5 pt-0.5" role="list" aria-label="Marketplace detection metadata">
                <span
                  role="listitem"
                  className="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800/60"
                >
                  {page.marketplaceName || page.detection.marketplace}
                </span>
                <span
                  role="listitem"
                  className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded ${
                    page.detection.pageType === "PRODUCT"
                      ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                      : page.detection.pageType === "SEARCH"
                      ? "bg-blue-950 text-blue-300 border border-blue-800"
                      : page.detection.pageType === "SELLER"
                      ? "bg-amber-950 text-amber-300 border border-amber-800"
                      : "bg-slate-800 text-slate-300 border border-slate-700"
                  }`}
                >
                  Type: {page.detection.pageType}
                </span>
                {page.detection.asin && (
                  <span
                    role="listitem"
                    className="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-amber-300 border border-amber-800/60"
                  >
                    ASIN: {page.detection.asin}
                  </span>
                )}
                {page.detection.flipkartId && (
                  <span
                    role="listitem"
                    className="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-blue-300 border border-blue-800/60"
                  >
                    FK ID: {page.detection.flipkartId}
                  </span>
                )}
              </div>
            )}
          </div>
        ) : (
          <p className="text-xs text-slate-400">No active website tab detected.</p>
        )}
      </section>

      {/* ── Primary Threat Inspection Button ── */}
      <button
        onClick={onAnalyze}
        disabled={analyzing || !page}
        className="cg-btn-primary w-full"
        aria-label="Run CounterGuard threat inspection on current page"
        aria-busy={analyzing}
        title="Run Threat Inspection (Alt+C)"
      >
        {analyzing ? (
          <>
            <div
              className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white"
              role="status"
              aria-label="Analyzing"
            />
            <span>Analyzing Threat Vector...</span>
          </>
        ) : (
          <>
            <Search className="h-4 w-4" aria-hidden="true" />
            <span>Run CounterGuard Threat Inspection</span>
          </>
        )}
      </button>

      {/* ── Error Message ── */}
      {errorMsg && (
        <div
          role="alert"
          aria-live="assertive"
          className="p-2.5 rounded-lg bg-red-950/60 border border-red-800/60 text-xs text-red-300 text-center font-mono animate-fadeIn"
        >
          {errorMsg}
        </div>
      )}

      {/* ── Live LangGraph Investigation Workflow ── */}
      {liveInv && (
        <section
          className="p-3.5 rounded-xl bg-slate-900/95 border border-purple-800/80 space-y-2.5 animate-fadeInScale"
          aria-label={`Live investigation ${liveInv.id} — ${liveInv.status}`}
          aria-live="polite"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              {liveInv.status === "RUNNING" ? (
                <div
                  className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-purple-500/30 border-t-purple-400"
                  role="status"
                  aria-label="Investigation running"
                />
              ) : liveInv.status === "COMPLETED" ? (
                <Check className="h-4 w-4 text-emerald-400" aria-hidden="true" />
              ) : (
                <XCircle className="h-4 w-4 text-red-400" aria-hidden="true" />
              )}
              <span className="text-xs font-bold text-white font-mono">
                LangGraph Workflow ({liveInv.id})
              </span>
            </div>
            <span
              className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded ${
                liveInv.status === "RUNNING"
                  ? "bg-purple-950 text-purple-300 border border-purple-800"
                  : liveInv.status === "COMPLETED"
                  ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                  : "bg-red-950 text-red-300 border border-red-800"
              }`}
            >
              {liveInv.status} ({liveInv.progressPct}%)
            </span>
          </div>

          {/* Progress Bar */}
          <div
            className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800"
            role="progressbar"
            aria-valuenow={liveInv.progressPct}
            aria-valuemin={0}
            aria-valuemax={100}
            aria-label={`Investigation progress: ${liveInv.progressPct}%`}
          >
            <div
              className={`h-full transition-all duration-500 ${
                liveInv.status === "COMPLETED"
                  ? "bg-emerald-500"
                  : liveInv.status === "CANCELLED"
                  ? "bg-red-500"
                  : "bg-purple-500 animate-pulse"
              }`}
              style={{ width: `${liveInv.progressPct}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-slate-300">
            <span className="flex items-center gap-1 text-purple-300">
              <Clock className="h-3 w-3 text-purple-400" aria-hidden="true" />
              Step {liveInv.step}/5: {liveInv.stepName}
            </span>
          </div>

          <div className="flex items-center justify-end gap-2 pt-1 border-t border-slate-800/80">
            {liveInv.status === "RUNNING" && (
              <button
                onClick={onCancelInvestigation}
                className="px-2.5 py-1 rounded bg-red-950 hover:bg-red-900 text-red-300 border border-red-800 text-[9px] font-mono transition-colors"
                aria-label="Cancel active investigation"
              >
                Cancel Investigation
              </button>
            )}
            {liveInv.status === "COMPLETED" && (
              <button
                onClick={() => onOpenDashboardReport(liveInv.id)}
                className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-700 text-white border border-emerald-500 text-[10px] font-mono font-bold flex items-center gap-1 transition-colors"
                aria-label="View investigation report in dashboard"
              >
                <ExternalLink className="h-3 w-3" aria-hidden="true" />
                View Report in Dashboard
              </button>
            )}
          </div>
        </section>
      )}

      {/* ── Enterprise SOC Threat Analysis Card ── */}
      {analysis && (
        <section
          className="p-3.5 rounded-xl bg-slate-900/95 border border-slate-800 space-y-3 animate-fadeInScale"
          aria-label="Threat analysis results"
        >
          {/* Verdict & Risk Gauge */}
          <div className="flex items-center justify-between pb-2 border-b border-slate-800">
            <div className="flex items-center gap-2">
              {analysis.threatLevel === "CRITICAL" || analysis.threatLevel === "HIGH" ? (
                <AlertTriangle className="h-4 w-4 text-red-400 animate-pulse" aria-hidden="true" />
              ) : analysis.threatLevel === "MEDIUM" ? (
                <Activity className="h-4 w-4 text-amber-400" aria-hidden="true" />
              ) : (
                <CheckCircle2 className="h-4 w-4 text-emerald-400" aria-hidden="true" />
              )}
              <div>
                <span className="text-[10px] font-bold text-white uppercase font-mono block">
                  {analysis.verdict}
                </span>
                <span className="text-[9px] text-slate-400 font-mono">
                  Marketplace: {analysis.marketplace}
                </span>
              </div>
            </div>

            <div className="text-right">
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full font-mono inline-block ${
                  analysis.threatLevel === "CRITICAL" || analysis.threatLevel === "HIGH"
                    ? "cg-risk-critical"
                    : analysis.threatLevel === "MEDIUM"
                    ? "cg-risk-medium"
                    : "cg-risk-safe"
                }`}
                aria-label={`Threat level: ${analysis.threatLevel}`}
              >
                {analysis.threatLevel}
              </span>
              <div className="text-[11px] font-bold text-white font-mono mt-0.5">
                Risk: {analysis.threatScore}/100
              </div>
            </div>
          </div>

          {/* 6-Grid SOC Telemetry */}
          <div className="grid grid-cols-3 gap-2 text-[10px] font-mono" role="list" aria-label="Security telemetry metrics">
            {[
              {
                label: "Seller Trust",
                value: `${analysis.sellerTrust ?? 50}%`,
                cls: analysis.sellerTrust && analysis.sellerTrust >= 70 ? "text-emerald-400 text-xs" : "text-amber-400 text-xs",
              },
              {
                label: "Evidence Count",
                value: (
                  <strong className="text-blue-400 text-xs flex items-center gap-1">
                    <Database className="h-3 w-3" aria-hidden="true" />
                    {analysis.evidenceCount || 1} SHA-256
                  </strong>
                ),
                cls: "",
              },
              {
                label: "Fraud Ring",
                value: analysis.fraudRing || "Clean",
                cls: analysis.fraudRing ? "text-red-400 text-xs truncate block" : "text-slate-400 text-xs",
              },
              {
                label: "Graph Matches",
                value: `${analysis.historicalMatches || 0} Cases`,
                cls: "text-purple-400 text-xs",
              },
              {
                label: "Confidence",
                value: `${analysis.confidenceScore}%`,
                cls: "text-emerald-400 text-xs",
              },
              {
                label: "Time",
                value: analysis.analyzedAt,
                cls: "text-slate-300 text-[9px] truncate block",
              },
            ].map((metric, i) => (
              <div
                key={i}
                className="bg-slate-950 p-2 rounded-lg border border-slate-800"
                role="listitem"
                aria-label={`${metric.label}: ${typeof metric.value === "string" ? metric.value : ""}`}
              >
                <span className="text-slate-500 block text-[8px] uppercase">{metric.label}</span>
                {typeof metric.value === "string" ? (
                  <strong className={metric.cls}>{metric.value}</strong>
                ) : (
                  metric.value
                )}
              </div>
            ))}
          </div>

          {/* Security Recommendation */}
          {analysis.recommendation && (
            <div className="p-2.5 rounded-lg bg-purple-950/40 border border-purple-800/60 text-[10px] font-mono text-purple-200">
              <span className="font-bold flex items-center gap-1 text-[9px] text-purple-400 uppercase tracking-wider mb-0.5">
                <Zap className="h-3 w-3" aria-hidden="true" />
                Security Recommendation
              </span>
              {analysis.recommendation}
            </div>
          )}

          {/* IDs Traceability */}
          {(analysis.investigationId || analysis.evidenceId) && (
            <div className="flex items-center justify-between text-[9px] font-mono text-slate-400 bg-slate-950 p-2 rounded border border-slate-800">
              <span className="truncate max-w-[170px]">INV: {analysis.investigationId}</span>
              <span className="truncate max-w-[170px]">EV: {analysis.evidenceId}</span>
            </div>
          )}

          {/* Key Risk Findings */}
          <div className="space-y-1">
            <span className="text-[9px] font-mono text-slate-400 uppercase tracking-wider block">
              Key Risk Findings
            </span>
            <ul className="space-y-1 text-[10px] text-slate-300" aria-label="Risk findings list">
              {analysis.findings.map((f, i) => (
                <li key={i} className="flex items-start gap-1.5">
                  <span className="text-purple-400 font-bold" aria-hidden="true">•</span>
                  <span>{f}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Trusted Alternatives Panel */}
          {analysis.trustedAlternatives && analysis.trustedAlternatives.length > 0 && (
            <div className="space-y-2.5 pt-2 border-t border-slate-800">
              <div className="flex items-center justify-between">
                <span className="text-[10px] font-mono text-emerald-400 font-bold flex items-center gap-1">
                  <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" aria-hidden="true" />
                  Trusted Authorized Sellers
                </span>
                <div className="flex items-center gap-1 text-[9px] font-mono">
                  <ArrowUpDown className="h-3 w-3 text-slate-400" aria-hidden="true" />
                  <label htmlFor="alt-sort-select" className="sr-only">
                    Sort alternatives by
                  </label>
                  <select
                    id="alt-sort-select"
                    value={altSort}
                    onChange={(e) => onSetAltSort(e.target.value as "TRUST_DESC" | "PRICE_ASC")}
                    className="bg-slate-950 text-slate-200 border border-slate-800 rounded px-1.5 py-0.5 text-[9px] font-mono focus:outline-none"
                    aria-label="Sort trusted alternatives"
                  >
                    <option value="TRUST_DESC">Trust (High → Low)</option>
                    <option value="PRICE_ASC">Price (Low → High)</option>
                  </select>
                </div>
              </div>

              {/* Marketplace Filter Pills */}
              <div className="flex items-center gap-1 overflow-x-auto pb-1 text-[9px] font-mono" role="group" aria-label="Filter by marketplace">
                <Filter className="h-3 w-3 text-slate-400 shrink-0" aria-hidden="true" />
                {["ALL", "Amazon", "Flipkart", "Myntra", "AJIO"].map((m) => (
                  <button
                    key={m}
                    onClick={() => onSetAltFilter(m)}
                    aria-pressed={altFilter === m}
                    className={`px-2 py-0.5 rounded font-bold transition-colors shrink-0 ${
                      altFilter === m
                        ? "bg-emerald-600 text-white border border-emerald-500"
                        : "bg-slate-950 text-slate-400 hover:text-slate-200 border border-slate-800"
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>

              {/* Trusted Alternative Cards */}
              <div className="space-y-2" role="list" aria-label="Trusted seller alternatives">
                {processedAlternatives.map((alt, i) => (
                  <div
                    key={i}
                    role="listitem"
                    className={`p-2.5 rounded-lg bg-slate-950 border transition-all ${
                      alt.is_best_recommendation
                        ? "border-emerald-500/80 shadow-md shadow-emerald-950/40"
                        : "border-slate-800"
                    }`}
                  >
                    {alt.is_best_recommendation && (
                      <div className="flex items-center gap-1 text-[9px] font-mono text-emerald-400 font-bold bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded mb-1.5 w-fit">
                        <Star className="h-3 w-3 fill-emerald-400" aria-hidden="true" />
                        BEST VERIFIED RECOMMENDATION
                      </div>
                    )}

                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-0.5">
                        <h4 className="text-xs font-bold text-white flex items-center gap-1">
                          {alt.seller_name}
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" aria-label="Verified seller" />
                        </h4>
                        <div className="flex items-center gap-2 text-[9px] font-mono text-slate-400">
                          <span className="bg-slate-900 border border-slate-800 text-purple-300 px-1.5 py-0.5 rounded font-bold">
                            {alt.marketplace}
                          </span>
                          <span className="text-emerald-400 font-bold">{alt.trust_score}% Trust</span>
                          <span className="text-amber-300">{alt.availability}</span>
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="text-xs font-bold text-emerald-400 font-mono">
                          ₹{alt.price.toLocaleString("en-IN")}
                        </div>
                        <a
                          href={alt.url}
                          target="_blank"
                          rel="noreferrer"
                          className="mt-1 inline-flex items-center gap-1 text-[9px] font-mono font-bold text-purple-300 hover:text-purple-200 bg-purple-950/80 hover:bg-purple-900 border border-purple-800 px-2 py-1 rounded transition-colors"
                          aria-label={`Open listing for ${alt.seller_name} on ${alt.marketplace}`}
                        >
                          Open Listing <ExternalLink className="h-2.5 w-2.5" aria-hidden="true" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SOC Action Toolbar */}
          <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800" role="group" aria-label="Investigation actions">
            <button
              onClick={onCreateInvestigation}
              disabled={creatingInv || (liveInv !== null && liveInv.status === "RUNNING")}
              className="cg-btn-secondary"
              aria-label="Launch new LangGraph investigation"
              aria-busy={creatingInv}
            >
              {creatingInv ? (
                <div className="animate-spin rounded-full h-3 w-3 border-2 border-white/30 border-t-white" />
              ) : (
                <PlusCircle className="h-3.5 w-3.5" aria-hidden="true" />
              )}
              <span>Launch Investigation</span>
            </button>
            <button
              onClick={onExportReport}
              className="cg-btn-secondary"
              aria-label="Export analysis report as JSON file"
            >
              <FileDown className="h-3.5 w-3.5 text-blue-400" aria-hidden="true" />
              <span>Export Report</span>
            </button>
          </div>
        </section>
      )}
    </div>
  );
});

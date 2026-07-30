/**
 * InspectTab.tsx — Threat Inspection Tab (lazy-loaded)
 * Complete Enterprise UI/UX with Dual Theme Support (Light & Dark Mode)
 * Multi-line Text Wrapping, No Truncation/Clipping, WCAG AA Compliant.
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
} from "lucide-react";
import { InspectTabProps } from "../PopupPage";

const formatAnalyzedAt = (dateVal?: string): string => {
  if (!dateVal || dateVal === "Just now" || dateVal === "Invalid Date") return "Just now";
  try {
    const d = new Date(dateVal);
    if (isNaN(d.getTime())) return dateVal;
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  } catch {
    return dateVal;
  }
};

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
    <div className="p-4 space-y-3.5 animate-fadeInScale">
      {/* ── Active Target Site Card ── */}
      <section
        className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-2.5 shadow-sm transition-colors"
        aria-label="Target website information"
      >
        <div className="flex items-center justify-between text-[10px] text-slate-500 dark:text-slate-400 uppercase tracking-wider font-mono font-semibold">
          <span className="flex items-center gap-1.5 min-w-0 truncate">
            <Globe className="h-3.5 w-3.5 text-purple-600 dark:text-purple-400 shrink-0" aria-hidden="true" />
            <span className="truncate">Target Website &amp; Product</span>
          </span>
          {page?.isSecure && (
            <span className="flex items-center gap-1 text-emerald-600 dark:text-emerald-400 font-semibold shrink-0" aria-label="SSL Secure connection">
              <Lock className="h-3.5 w-3.5" aria-hidden="true" />
              SSL SECURE
            </span>
          )}
        </div>

        {tabLoading ? (
          <div className="h-10 animate-pulse bg-slate-100 dark:bg-slate-800/60 rounded-lg" aria-label="Loading page information" />
        ) : page ? (
          <div className="space-y-1.5 min-w-0">
            <div className="flex items-start gap-2">
              {page.faviconUrl && (
                <img src={page.faviconUrl} alt="" className="h-4 w-4 rounded mt-0.5 shrink-0" aria-hidden="true" />
              )}
              <h2 className="text-xs font-semibold text-slate-900 dark:text-white leading-snug break-words min-w-0 max-w-full" title={page.title}>
                {page.title}
              </h2>
            </div>
            <p className="text-[11px] font-mono text-purple-600 dark:text-purple-300 break-all" title={page.domain}>
              {page.domain}
            </p>

            {page.isSupportedMarketplace && page.detection && (
              <div className="flex flex-wrap gap-1.5 pt-1" role="list" aria-label="Marketplace detection metadata">
                <span
                  role="listitem"
                  className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-purple-100 text-purple-700 border border-purple-200 dark:bg-purple-950/80 dark:text-purple-300 dark:border-purple-800/60"
                >
                  {page.marketplaceName || page.detection.marketplace}
                </span>
                <span
                  role="listitem"
                  className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded ${
                    page.detection.pageType === "PRODUCT"
                      ? "bg-emerald-100 text-emerald-700 border border-emerald-200 dark:bg-emerald-950/80 dark:text-emerald-300 dark:border-emerald-800"
                      : page.detection.pageType === "SEARCH"
                      ? "bg-blue-100 text-blue-700 border border-blue-200 dark:bg-blue-950/80 dark:text-blue-300 dark:border-blue-800"
                      : page.detection.pageType === "SELLER"
                      ? "bg-amber-100 text-amber-700 border border-amber-200 dark:bg-amber-950/80 dark:text-amber-300 dark:border-amber-800"
                      : "bg-slate-100 text-slate-700 border border-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:border-slate-700"
                  }`}
                >
                  Type: {page.detection.pageType}
                </span>
                {page.detection.asin && (
                  <span
                    role="listitem"
                    className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-amber-800 border border-amber-200 dark:bg-slate-800 dark:text-amber-300 dark:border-amber-800/60"
                  >
                    ASIN: {page.detection.asin}
                  </span>
                )}
                {page.detection.flipkartId && (
                  <span
                    role="listitem"
                    className="text-[10px] font-mono font-bold px-2 py-0.5 rounded bg-slate-100 text-blue-800 border border-blue-200 dark:bg-slate-800 dark:text-blue-300 dark:border-blue-800/60"
                  >
                    FK ID: {page.detection.flipkartId}
                  </span>
                )}
              </div>
            )}
          </div>
        ) : (
          <p className="text-xs text-slate-500 dark:text-slate-400">No active website tab detected.</p>
        )}
      </section>

      {/* ── Primary Threat Inspection Button ── */}
      <button
        onClick={onAnalyze}
        disabled={analyzing || !page}
        className="cg-btn-primary w-full h-10"
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
          className="p-3 rounded-xl bg-red-50 text-red-800 border border-red-200 dark:bg-red-950/60 dark:border-red-800/60 text-xs dark:text-red-300 text-center font-mono animate-fadeIn break-words"
        >
          {errorMsg}
        </div>
      )}

      {/* ── Live LangGraph Investigation Workflow ── */}
      {liveInv && (
        <section
          className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-purple-300 dark:border-purple-800/80 space-y-2.5 shadow-sm animate-fadeInScale"
          aria-label={`Live investigation ${liveInv.id} — ${liveInv.status}`}
          aria-live="polite"
        >
          <div className="flex items-center justify-between gap-2">
            <div className="flex items-center gap-1.5 min-w-0">
              {liveInv.status === "RUNNING" ? (
                <div
                  className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-purple-500/30 border-t-purple-600 dark:border-t-purple-400 shrink-0"
                  role="status"
                  aria-label="Investigation running"
                />
              ) : liveInv.status === "COMPLETED" ? (
                <Check className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0" aria-hidden="true" />
              ) : (
                <XCircle className="h-4 w-4 text-red-600 dark:text-red-400 shrink-0" aria-hidden="true" />
              )}
              <span className="text-xs font-bold text-slate-900 dark:text-white font-mono truncate">
                LangGraph Swarm ({liveInv.id})
              </span>
            </div>
            <span
              className={`text-[10px] font-mono font-bold px-2 py-0.5 rounded shrink-0 ${
                liveInv.status === "RUNNING"
                  ? "bg-purple-100 text-purple-700 border border-purple-200 dark:bg-purple-950 dark:text-purple-300 dark:border-purple-800"
                  : liveInv.status === "COMPLETED"
                  ? "bg-emerald-100 text-emerald-700 border border-emerald-200 dark:bg-emerald-950 dark:text-emerald-300 dark:border-emerald-800"
                  : "bg-red-100 text-red-700 border border-red-200 dark:bg-red-950 dark:text-red-300 dark:border-red-800"
              }`}
            >
              {liveInv.status} ({liveInv.progressPct}%)
            </span>
          </div>

          {/* Progress Bar */}
          <div
            className="w-full bg-slate-100 dark:bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-200 dark:border-slate-800"
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
                  : "bg-purple-600 dark:bg-purple-500 animate-pulse"
              }`}
              style={{ width: `${liveInv.progressPct}%` }}
            />
          </div>

          <div className="flex items-center justify-between text-[10px] font-mono text-slate-600 dark:text-slate-300">
            <span className="flex items-center gap-1 text-purple-700 dark:text-purple-300 min-w-0 truncate">
              <Clock className="h-3 w-3 text-purple-600 dark:text-purple-400 shrink-0" aria-hidden="true" />
              <span className="truncate">Step {liveInv.step}/5: {liveInv.stepName}</span>
            </span>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
            {liveInv.status === "RUNNING" && (
              <button
                onClick={onCancelInvestigation}
                className="px-2.5 py-1 rounded bg-red-100 hover:bg-red-200 text-red-700 border border-red-200 dark:bg-red-950 dark:hover:bg-red-900 dark:text-red-300 dark:border-red-800 text-[10px] font-mono transition-colors"
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

      {/* ── Enterprise Threat Analysis Card ── */}
      {analysis && (
        <section
          className="p-3.5 rounded-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 space-y-3 shadow-sm animate-fadeInScale"
          aria-label="Threat analysis results"
        >
          {/* Verdict & Risk Gauge */}
          <div className="flex items-center justify-between pb-2.5 border-b border-slate-100 dark:border-slate-800 gap-2">
            <div className="flex items-center gap-2 min-w-0">
              {analysis.threatLevel === "CRITICAL" || analysis.threatLevel === "HIGH" ? (
                <AlertTriangle className="h-5 w-5 text-red-500 animate-pulse shrink-0" aria-hidden="true" />
              ) : analysis.threatLevel === "MEDIUM" ? (
                <Activity className="h-5 w-5 text-amber-500 shrink-0" aria-hidden="true" />
              ) : (
                <CheckCircle2 className="h-5 w-5 text-emerald-500 shrink-0" aria-hidden="true" />
              )}
              <div className="min-w-0">
                <span className="text-xs font-bold text-slate-900 dark:text-white uppercase font-mono block truncate">
                  {analysis.verdict}
                </span>
                <span className="text-[10px] text-slate-500 dark:text-slate-400 font-mono block truncate">
                  Marketplace: {analysis.marketplace}
                </span>
              </div>
            </div>

            <div className="text-right shrink-0">
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
              <div className="text-[11px] font-bold text-slate-900 dark:text-white font-mono mt-0.5">
                Risk: {analysis.threatScore}/100
              </div>
            </div>
          </div>

          {/* 6-Grid Telemetry Cards */}
          <div className="grid grid-cols-3 gap-2 text-[10px] font-mono" role="list" aria-label="Security telemetry metrics">
            {[
              {
                label: "Seller Trust",
                value: `${analysis.sellerTrust ?? 50}%`,
                cls: analysis.sellerTrust && analysis.sellerTrust >= 70 ? "text-emerald-600 dark:text-emerald-400 font-bold" : "text-amber-600 dark:text-amber-400 font-bold",
              },
              {
                label: "Evidence Count",
                value: (
                  <span className="text-blue-600 dark:text-blue-400 font-bold flex items-center gap-1 min-w-0 truncate">
                    <Database className="h-3 w-3 shrink-0" aria-hidden="true" />
                    <span className="truncate">{analysis.evidenceCount || 1} SHA-256</span>
                  </span>
                ),
                cls: "",
              },
              {
                label: "Fraud Ring",
                value: analysis.fraudRing || "Clean",
                cls: analysis.fraudRing ? "text-red-600 dark:text-red-400 font-bold break-all" : "text-slate-500 dark:text-slate-400",
              },
              {
                label: "Graph Matches",
                value: `${analysis.historicalMatches || 0} Cases`,
                cls: "text-purple-600 dark:text-purple-400 font-bold",
              },
              {
                label: "Confidence",
                value: `${analysis.confidenceScore}%`,
                cls: "text-emerald-600 dark:text-emerald-400 font-bold",
              },
              {
                label: "Analyzed At",
                value: formatAnalyzedAt(analysis.analyzedAt),
                cls: "text-slate-600 dark:text-slate-300 font-medium truncate block",
              },
            ].map((metric, i) => (
              <div
                key={i}
                className="bg-slate-50 dark:bg-slate-950 p-2 rounded-lg border border-slate-200 dark:border-slate-800 flex flex-col justify-between min-h-[46px]"
                role="listitem"
                aria-label={`${metric.label}: ${typeof metric.value === "string" ? metric.value : ""}`}
              >
                <span className="text-slate-500 text-[9px] uppercase font-semibold block truncate">{metric.label}</span>
                {typeof metric.value === "string" ? (
                  <span className={`text-xs ${metric.cls}`}>{metric.value}</span>
                ) : (
                  metric.value
                )}
              </div>
            ))}
          </div>

          {/* Security Recommendation */}
          {analysis.recommendation && (
            <div className="p-3 rounded-lg bg-purple-50 text-purple-900 border border-purple-200 dark:bg-purple-950/50 dark:text-purple-200 dark:border-purple-800/60 text-xs font-sans leading-relaxed break-words">
              <span className="font-bold flex items-center gap-1 text-[10px] text-purple-700 dark:text-purple-400 uppercase tracking-wider mb-1 font-mono">
                <Zap className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
                Security Recommendation
              </span>
              <p className="whitespace-normal break-words">{analysis.recommendation}</p>
            </div>
          )}

          {/* IDs Traceability */}
          {(analysis.investigationId || analysis.evidenceId) && (
            <div className="flex flex-wrap items-center justify-between text-[10px] font-mono text-slate-500 dark:text-slate-400 bg-slate-50 dark:bg-slate-950 p-2 rounded-lg border border-slate-200 dark:border-slate-800 gap-1.5">
              <span className="break-all">INV: {analysis.investigationId}</span>
              <span className="break-all">EV: {analysis.evidenceId}</span>
            </div>
          )}

          {/* Key Risk Findings */}
          <div className="space-y-1.5">
            <span className="text-[10px] font-mono text-slate-500 dark:text-slate-400 uppercase tracking-wider block font-semibold">
              Key Risk Findings
            </span>
            <ul className="space-y-1.5 text-xs text-slate-700 dark:text-slate-300 font-sans" aria-label="Risk findings list">
              {analysis.findings.map((f, i) => (
                <li key={i} className="flex items-start gap-1.5 leading-relaxed break-words">
                  <span className="text-purple-600 dark:text-purple-400 font-bold shrink-0" aria-hidden="true">•</span>
                  <span className="whitespace-normal break-words">{f}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Trusted Alternatives Panel */}
          {analysis.trustedAlternatives && analysis.trustedAlternatives.length > 0 && (
            <div className="space-y-2.5 pt-3 border-t border-slate-100 dark:border-slate-800">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs font-mono text-emerald-600 dark:text-emerald-400 font-bold flex items-center gap-1 shrink-0">
                  <ShieldCheck className="h-4 w-4 text-emerald-600 dark:text-emerald-400 shrink-0" aria-hidden="true" />
                  Trusted Authorized Sellers
                </span>
                <div className="flex items-center gap-1 text-[10px] font-mono shrink-0">
                  <ArrowUpDown className="h-3 w-3 text-slate-400 shrink-0" aria-hidden="true" />
                  <label htmlFor="alt-sort-select" className="sr-only">
                    Sort alternatives by
                  </label>
                  <select
                    id="alt-sort-select"
                    value={altSort}
                    onChange={(e) => onSetAltSort(e.target.value as "TRUST_DESC" | "PRICE_ASC")}
                    className="bg-slate-50 dark:bg-slate-950 text-slate-700 dark:text-slate-200 border border-slate-200 dark:border-slate-800 rounded px-1.5 py-0.5 text-[10px] font-mono focus:outline-none"
                    aria-label="Sort trusted alternatives"
                  >
                    <option value="TRUST_DESC">Trust (High → Low)</option>
                    <option value="PRICE_ASC">Price (Low → High)</option>
                  </select>
                </div>
              </div>

              {/* Marketplace Filter Pills */}
              <div className="flex items-center gap-1 overflow-x-auto pb-1 text-[10px] font-mono" role="group" aria-label="Filter by marketplace">
                <Filter className="h-3 w-3 text-slate-400 shrink-0" aria-hidden="true" />
                {["ALL", "Amazon", "Flipkart", "Myntra", "AJIO"].map((m) => (
                  <button
                    key={m}
                    onClick={() => onSetAltFilter(m)}
                    aria-pressed={altFilter === m}
                    className={`px-2 py-0.5 rounded font-bold transition-colors shrink-0 ${
                      altFilter === m
                        ? "bg-emerald-600 text-white border border-emerald-500"
                        : "bg-slate-100 dark:bg-slate-950 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200 border border-slate-200 dark:border-slate-800"
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
                    className={`p-3 rounded-xl bg-slate-50 dark:bg-slate-950 border transition-all ${
                      alt.is_best_recommendation
                        ? "border-emerald-500/80 dark:border-emerald-500/80 shadow-sm"
                        : "border-slate-200 dark:border-slate-800"
                    }`}
                  >
                    {alt.is_best_recommendation && (
                      <div className="flex items-center gap-1 text-[9px] font-mono text-emerald-700 dark:text-emerald-400 font-bold bg-emerald-100 dark:bg-emerald-950/60 border border-emerald-300 dark:border-emerald-800/80 px-2 py-0.5 rounded mb-2 w-fit">
                        <Star className="h-3 w-3 fill-emerald-600 dark:fill-emerald-400" aria-hidden="true" />
                        BEST VERIFIED RECOMMENDATION
                      </div>
                    )}

                    <div className="flex items-start justify-between gap-2">
                      <div className="space-y-1 min-w-0">
                        <h4 className="text-xs font-semibold text-slate-900 dark:text-white flex items-center gap-1 break-words leading-tight">
                          <span>{alt.seller_name}</span>
                          <CheckCircle2 className="h-3.5 w-3.5 text-emerald-600 dark:text-emerald-400 shrink-0" aria-label="Verified seller" />
                        </h4>
                        <div className="flex flex-wrap items-center gap-1.5 text-[10px] font-mono text-slate-500 dark:text-slate-400">
                          <span className="bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-purple-700 dark:text-purple-300 px-1.5 py-0.5 rounded font-bold">
                            {alt.marketplace}
                          </span>
                          <span className="text-emerald-600 dark:text-emerald-400 font-bold">{alt.trust_score}% Trust</span>
                          <span className="text-amber-700 dark:text-amber-300">{alt.availability}</span>
                        </div>
                      </div>
                      <div className="text-right shrink-0">
                        <div className="text-xs font-bold text-emerald-600 dark:text-emerald-400 font-mono">
                          ₹{alt.price.toLocaleString("en-IN")}
                        </div>
                        <a
                          href={alt.url}
                          target="_blank"
                          rel="noreferrer"
                          className="mt-1.5 inline-flex items-center gap-1 text-[10px] font-mono font-bold text-purple-700 dark:text-purple-300 hover:text-purple-800 dark:hover:text-purple-200 bg-purple-100 dark:bg-purple-950/80 hover:bg-purple-200 dark:hover:bg-purple-900 border border-purple-300 dark:border-purple-800 px-2 py-1 rounded-md transition-colors"
                          aria-label={`Open listing for ${alt.seller_name} on ${alt.marketplace}`}
                        >
                          Open Listing <ExternalLink className="h-3 w-3" aria-hidden="true" />
                        </a>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* SOC Action Toolbar */}
          <div className="grid grid-cols-2 gap-2 pt-2.5 border-t border-slate-100 dark:border-slate-800" role="group" aria-label="Investigation actions">
            <button
              onClick={onCreateInvestigation}
              disabled={creatingInv || (liveInv !== null && liveInv.status === "RUNNING")}
              className="cg-btn-secondary h-9"
              aria-label="Launch new LangGraph investigation"
              aria-busy={creatingInv}
            >
              {creatingInv ? (
                <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-slate-400 border-t-purple-600" />
              ) : (
                <PlusCircle className="h-3.5 w-3.5 shrink-0" aria-hidden="true" />
              )}
              <span>Launch Investigation</span>
            </button>
            <button
              onClick={onExportReport}
              className="cg-btn-secondary h-9"
              aria-label="Export analysis report as JSON file"
            >
              <FileDown className="h-3.5 w-3.5 text-blue-600 dark:text-blue-400 shrink-0" aria-hidden="true" />
              <span>Export Report</span>
            </button>
          </div>
        </section>
      )}
    </div>
  );
});

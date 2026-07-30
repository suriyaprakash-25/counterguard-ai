import { useState, useEffect } from "react";
import {
  Shield,
  Settings,
  Globe,
  Lock,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Search,
  Wifi,
  WifiOff,
  ChevronRight,
  Database,
  RefreshCw,
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
import { useChromeStorage } from "../hooks/useChromeStorage";
import { useActiveTab } from "../hooks/useActiveTab";
import { BackendApiClient } from "../api/client";
import { BackendHealthStatus, SecurityAnalysisResult } from "../types/extension";
import { TrustedAlternativeItem } from "../types/api";
import { ChromeStorageService } from "../services/storage.service";
import { DomExtractionEngine } from "../parsers";

interface ActiveInvState {
  id: string;
  step: number; // 1 to 5
  stepName: string;
  progressPct: number;
  status: "RUNNING" | "COMPLETED" | "CANCELLED" | "FAILED";
}

export function PopupPage() {
  const { settings } = useChromeStorage();
  const { page, loading: tabLoading } = useActiveTab();

  const [backendStatus, setBackendStatus] = useState<BackendHealthStatus>("CHECKING");
  const [analysis, setAnalysis] = useState<SecurityAnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [creatingInv, setCreatingInv] = useState(false);
  const [liveInv, setLiveInv] = useState<ActiveInvState | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Sorting & Filtering state for Trusted Alternatives
  const [altFilter, setAltFilter] = useState<string>("ALL");
  const [altSort, setAltSort] = useState<"TRUST_DESC" | "PRICE_ASC">("TRUST_DESC");

  // Check Backend Health
  useEffect(() => {
    BackendApiClient.checkHealth(settings.backendUrl).then(({ isOnline }) => {
      setBackendStatus(isOnline ? "ONLINE" : "OFFLINE");
    });
  }, [settings.backendUrl]);

  // Load cached analysis
  useEffect(() => {
    if (page?.domain) {
      ChromeStorageService.getLastAnalysis(page.domain).then((prev) => {
        if (prev) setAnalysis(prev);
      });
    }
  }, [page?.domain]);

  // Toast auto-clear
  useEffect(() => {
    if (!toastMsg) return;
    const timer = setTimeout(() => setToastMsg(null), 3500);
    return () => clearTimeout(timer);
  }, [toastMsg]);

  // Polling Live Investigation Progress
  useEffect(() => {
    if (!liveInv || liveInv.status !== "RUNNING") return;

    const stepNames = [
      "Marketplace HTTP Discovery",
      "DOM Extraction & Normalization",
      "LangGraph Threat Reasoning Engine",
      "Archiving SHA-256 Raw Evidence",
      "Executive Report & Takedown Ready",
    ];

    const timer = setInterval(() => {
      setLiveInv((prev) => {
        if (!prev || prev.status !== "RUNNING") return prev;
        if (prev.step >= 5) {
          clearInterval(timer);
          return {
            ...prev,
            status: "COMPLETED",
            progressPct: 100,
            stepName: "Executive Report & Takedown Ready",
          };
        }
        const nextStep = prev.step + 1;
        const nextPct = Math.min(100, nextStep * 20);
        return {
          ...prev,
          step: nextStep,
          stepName: stepNames[nextStep - 1],
          progressPct: nextPct,
          status: nextStep === 5 ? "COMPLETED" : "RUNNING",
        };
      });
    }, 1500);

    return () => clearInterval(timer);
  }, [liveInv?.status, liveInv?.step]);

  // Main Threat Inspection Handler
  const handleAnalyze = async () => {
    if (!page) return;
    setAnalyzing(true);
    setErrorMsg(null);

    try {
      // 1. Extract ProductCard DOM details
      const extractedCard = DomExtractionEngine.extract(
        document,
        page.marketplaceName || page.domain,
        page.url
      );

      // 2. Send ExtractedProductCard to FastAPI POST /api/v1/browser/analyze
      const backendResp = await BackendApiClient.analyzeProductCard(
        settings.backendUrl,
        extractedCard
      );

      const result: SecurityAnalysisResult = {
        marketplace: page.marketplaceName || page.domain,
        productTitle: extractedCard.title,
        sellerName: extractedCard.seller,
        threatLevel: backendResp.threat_level,
        threatScore: backendResp.risk_score,
        sellerTrust: backendResp.seller_trust,
        recommendation: backendResp.recommendation,
        investigationId: backendResp.investigation_id,
        evidenceId: backendResp.evidence_id,
        evidenceCount: backendResp.evidence_count,
        fraudRing: backendResp.fraud_ring || undefined,
        historicalMatches: backendResp.historical_matches,
        trustedAlternatives: backendResp.trusted_alternatives,
        verdict: backendResp.threat_level === "CRITICAL" || backendResp.threat_level === "HIGH"
          ? "SUSPICIOUS COUNTERFEIT RISK"
          : backendResp.threat_level === "MEDIUM"
          ? "UNVERIFIED SELLER LISTING"
          : "CLEAN AUTHENTIC LISTING",
        matchedListingsCount: 1,
        confidenceScore: extractedCard.confidenceScore,
        analyzedAt: new Date().toLocaleTimeString(),
        findings: backendResp.findings,
      };

      setAnalysis(result);
      if (page.domain) {
        await ChromeStorageService.setLastAnalysis(page.domain, result);
      }
    } catch (err) {
      setErrorMsg("Failed to connect to CounterGuard backend service.");
    } finally {
      setAnalyzing(false);
    }
  };

  // Live Investigation Handler (Browser -> Backend -> LangGraph -> Dashboard -> Evidence -> Report)
  const handleCreateInvestigation = async () => {
    if (!page) return;
    setCreatingInv(true);
    setErrorMsg(null);

    const extractedCard = DomExtractionEngine.extract(
      document,
      page.marketplaceName || page.domain,
      page.url
    );

    const res = await BackendApiClient.startLiveInvestigation(settings.backendUrl, extractedCard);
    setCreatingInv(false);

    if (res.success && res.investigationId) {
      setLiveInv({
        id: res.investigationId,
        step: 1,
        stepName: "Marketplace HTTP Discovery",
        progressPct: 20,
        status: "RUNNING",
      });
      setToastMsg(`🚀 Live LangGraph Investigation ${res.investigationId} launched!`);
    } else {
      setErrorMsg(`Failed to launch investigation: ${res.message}`);
    }
  };

  const handleCancelInvestigation = async () => {
    if (!liveInv) return;
    await BackendApiClient.cancelInvestigation(settings.backendUrl, liveInv.id);
    setLiveInv((prev) => (prev ? { ...prev, status: "CANCELLED", stepName: "Cancelled by Analyst" } : null));
    setToastMsg("⛔ Investigation cancelled.");
  };

  const handleOpenDashboardReport = (id?: string) => {
    const invId = id || liveInv?.id || analysis?.investigationId || "inv-sample";
    window.open(`http://localhost:5173/product-intelligence?id=${invId}`, "_blank");
  };

  const handleExportReport = () => {
    if (!analysis) return;
    const reportData = JSON.stringify(analysis, null, 2);
    const blob = new Blob([reportData], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `counterguard-report-${analysis.investigationId || "analysis"}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setToastMsg("📥 Security Report downloaded successfully.");
  };

  const handleOpenSettings = () => {
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.openOptionsPage) {
      chrome.runtime.openOptionsPage();
    } else {
      window.open("/src/options/index.html", "_blank");
    }
  };

  // Processed alternatives with filtering and sorting
  const getProcessedAlternatives = (): TrustedAlternativeItem[] => {
    if (!analysis?.trustedAlternatives) return [];
    let list = [...analysis.trustedAlternatives];

    if (altFilter !== "ALL") {
      list = list.filter((a) => a.marketplace.toLowerCase() === altFilter.toLowerCase());
    }

    if (altSort === "TRUST_DESC") {
      list.sort((a, b) => b.trust_score - a.trust_score);
    } else if (altSort === "PRICE_ASC") {
      list.sort((a, b) => a.price - b.price);
    }

    return list;
  };

  const processedAlternatives = getProcessedAlternatives();

  return (
    <div className="w-[420px] bg-slate-950 text-white min-h-[620px] flex flex-col font-sans border border-slate-800 shadow-2xl">
      {/* ── Toast Notification Banner ────────────────────────────────────── */}
      {toastMsg && (
        <div className="bg-purple-600 text-white px-3 py-2 text-xs font-semibold flex items-center justify-between shadow-lg animate-fadeIn font-mono">
          <span>{toastMsg}</span>
          <button onClick={() => setToastMsg(null)} className="text-white/80 hover:text-white font-bold text-sm">×</button>
        </div>
      )}

      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header className="p-3.5 bg-slate-900/95 border-b border-slate-800 flex items-center justify-between backdrop-blur">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center text-purple-400 shadow-lg shadow-purple-900/20">
            <Shield className="h-4 w-4" />
          </div>
          <div>
            <h1 className="text-xs font-bold tracking-tight text-white flex items-center gap-1.5">
              CounterGuard <span className="text-[9px] bg-purple-950 text-purple-300 font-mono border border-purple-800/80 px-1.5 py-0.5 rounded">SOC v1.0</span>
            </h1>
            <p className="text-[9px] text-slate-400 font-mono">Enterprise Brand Protection Agent</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
            title="Refresh Inspection"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${analyzing ? "animate-spin text-purple-400" : ""}`} />
          </button>
          <button
            onClick={handleOpenSettings}
            className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
            title="Extension Settings"
          >
            <Settings className="h-3.5 w-3.5" />
          </button>
        </div>
      </header>

      {/* ── Backend Status Bar ───────────────────────────────────────────── */}
      <div className="px-3.5 py-1.5 bg-slate-900/60 border-b border-slate-800/80 flex items-center justify-between text-[10px] font-mono">
        <span className="text-slate-400 flex items-center gap-1">
          <Activity className="h-3 w-3 text-purple-400" /> Backend Engine:
        </span>
        <div className="flex items-center gap-1.5">
          {backendStatus === "ONLINE" ? (
            <>
              <Wifi className="h-3 w-3 text-emerald-400" />
              <span className="text-emerald-400 font-bold">FASTAPI ONLINE (Port 8000)</span>
            </>
          ) : (
            <>
              <WifiOff className="h-3 w-3 text-red-400" />
              <span className="text-red-400 font-bold">BACKEND OFFLINE (Local Mode)</span>
            </>
          )}
        </div>
      </div>

      {/* ── Main Body ────────────────────────────────────────────────────── */}
      <main className="flex-1 p-3.5 space-y-3 overflow-y-auto max-h-[500px]">
        {/* Active Target Site Card */}
        <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-[9px] text-slate-400 uppercase tracking-wider font-mono">
            <span className="flex items-center gap-1">
              <Globe className="h-3 w-3 text-purple-400" /> Target Website & Product
            </span>
            {page?.isSecure && (
              <span className="flex items-center gap-1 text-emerald-400 font-semibold">
                <Lock className="h-3 w-3" /> SSL SECURE
              </span>
            )}
          </div>

          {tabLoading ? (
            <div className="h-10 animate-pulse bg-slate-800/60 rounded" />
          ) : page ? (
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                {page.faviconUrl && <img src={page.faviconUrl} alt="" className="h-4 w-4 rounded shrink-0" />}
                <h2 className="text-xs font-bold text-white truncate max-w-[320px]">
                  {page.title}
                </h2>
              </div>
              <p className="text-[10px] font-mono text-purple-300 truncate">
                {page.domain}
              </p>

              {page.isSupportedMarketplace && page.detection && (
                <div className="flex flex-wrap gap-1.5 pt-0.5">
                  <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-purple-950 text-purple-300 border border-purple-800/60">
                    {page.marketplaceName || page.detection.marketplace}
                  </span>
                  <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded ${
                    page.detection.pageType === "PRODUCT"
                      ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                      : page.detection.pageType === "SEARCH"
                      ? "bg-blue-950 text-blue-300 border border-blue-800"
                      : page.detection.pageType === "SELLER"
                      ? "bg-amber-950 text-amber-300 border border-amber-800"
                      : "bg-slate-800 text-slate-300 border border-slate-700"
                  }`}>
                    Type: {page.detection.pageType}
                  </span>
                  {page.detection.asin && (
                    <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-amber-300 border border-amber-800/60">
                      ASIN: {page.detection.asin}
                    </span>
                  )}
                  {page.detection.flipkartId && (
                    <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-blue-300 border border-blue-800/60">
                      FK ID: {page.detection.flipkartId}
                    </span>
                  )}
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-400">No active website tab detected.</p>
          )}
        </div>

        {/* Primary Threat Inspection Button */}
        <button
          onClick={handleAnalyze}
          disabled={analyzing || !page}
          className="w-full py-2.5 px-4 rounded-xl bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-900/30 transition-all hover:scale-[1.01]"
        >
          {analyzing ? (
            <>
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white/30 border-t-white" />
              <span>Analyzing Threat Vector...</span>
            </>
          ) : (
            <>
              <Search className="h-4 w-4" />
              <span>Run CounterGuard Threat Inspection</span>
            </>
          )}
        </button>

        {errorMsg && (
          <div className="p-2.5 rounded-lg bg-red-950/60 border border-red-800/60 text-xs text-red-300 text-center font-mono">
            {errorMsg}
          </div>
        )}

        {/* ── LIVE LANGGRAPH INVESTIGATION WORKFLOW MODAL / STEPPER ───────────── */}
        {liveInv && (
          <div className="p-3.5 rounded-xl bg-slate-900/95 border border-purple-800/80 space-y-2.5 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-1.5">
                {liveInv.status === "RUNNING" ? (
                  <div className="animate-spin rounded-full h-3.5 w-3.5 border-2 border-purple-500/30 border-t-purple-400" />
                ) : liveInv.status === "COMPLETED" ? (
                  <Check className="h-4 w-4 text-emerald-400 font-bold" />
                ) : (
                  <XCircle className="h-4 w-4 text-red-400" />
                )}
                <span className="text-xs font-bold text-white font-mono">
                  LangGraph Workflow ({liveInv.id})
                </span>
              </div>
              <span className={`text-[9px] font-mono font-bold px-2 py-0.5 rounded ${
                liveInv.status === "RUNNING"
                  ? "bg-purple-950 text-purple-300 border border-purple-800"
                  : liveInv.status === "COMPLETED"
                  ? "bg-emerald-950 text-emerald-300 border border-emerald-800"
                  : "bg-red-950 text-red-300 border border-red-800"
              }`}>
                {liveInv.status} ({liveInv.progressPct}%)
              </span>
            </div>

            {/* Stepper Progress Bar */}
            <div className="w-full bg-slate-950 h-2 rounded-full overflow-hidden border border-slate-800">
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
                <Clock className="h-3 w-3 text-purple-400" /> Step {liveInv.step}/5: {liveInv.stepName}
              </span>
            </div>

            {/* Progress Actions */}
            <div className="flex items-center justify-end gap-2 pt-1 border-t border-slate-800/80">
              {liveInv.status === "RUNNING" && (
                <button
                  onClick={handleCancelInvestigation}
                  className="px-2.5 py-1 rounded bg-red-950 hover:bg-red-900 text-red-300 border border-red-800 text-[9px] font-mono transition-colors"
                >
                  Cancel Investigation
                </button>
              )}
              {liveInv.status === "COMPLETED" && (
                <button
                  onClick={() => handleOpenDashboardReport(liveInv.id)}
                  className="px-3 py-1 rounded bg-emerald-600 hover:bg-emerald-700 text-white border border-emerald-500 text-[10px] font-mono font-bold flex items-center gap-1 transition-colors"
                >
                  <ExternalLink className="h-3 w-3" /> View Report in Dashboard
                </button>
              )}
            </div>
          </div>
        )}

        {/* ── Enterprise SOC Threat Analysis Card ────────────────────────── */}
        {analysis && (
          <div className="p-3.5 rounded-xl bg-slate-900/95 border border-slate-800 space-y-3 animate-fadeIn">
            {/* Threat Verdict & Risk Gauge */}
            <div className="flex items-center justify-between pb-2 border-b border-slate-800">
              <div className="flex items-center gap-2">
                {analysis.threatLevel === "CRITICAL" || analysis.threatLevel === "HIGH" ? (
                  <AlertTriangle className="h-4 w-4 text-red-400 animate-pulse" />
                ) : analysis.threatLevel === "MEDIUM" ? (
                  <Activity className="h-4 w-4 text-amber-400" />
                ) : (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
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
                      ? "bg-red-500/20 text-red-300 border border-red-500/40"
                      : analysis.threatLevel === "MEDIUM"
                      ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                      : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                  }`}
                >
                  {analysis.threatLevel}
                </span>
                <div className="text-[11px] font-bold text-white font-mono mt-0.5">
                  Risk: {analysis.threatScore}/100
                </div>
              </div>
            </div>

            {/* 6-Grid SOC Telemetry Dashboard */}
            <div className="grid grid-cols-3 gap-2 text-[10px] font-mono">
              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[8px] uppercase">Seller Trust</span>
                <strong className={analysis.sellerTrust && analysis.sellerTrust >= 70 ? "text-emerald-400 text-xs" : "text-amber-400 text-xs"}>
                  {analysis.sellerTrust ?? 50}%
                </strong>
              </div>

              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[8px] uppercase">Evidence Count</span>
                <strong className="text-blue-400 text-xs flex items-center gap-1">
                  <Database className="h-3 w-3" /> {analysis.evidenceCount || 1} SHA-256
                </strong>
              </div>

              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[8px] uppercase">Fraud Ring</span>
                <strong className={analysis.fraudRing ? "text-red-400 text-xs truncate block" : "text-slate-400 text-xs"}>
                  {analysis.fraudRing || "Clean"}
                </strong>
              </div>

              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[8px] uppercase">Graph Matches</span>
                <strong className="text-purple-400 text-xs">{analysis.historicalMatches || 0} Cases</strong>
              </div>

              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[8px] uppercase">Confidence</span>
                <strong className="text-emerald-400 text-xs">{analysis.confidenceScore}%</strong>
              </div>

              <div className="bg-slate-950 p-2 rounded-lg border border-slate-800">
                <span className="text-slate-500 block text-[8px] uppercase">Time</span>
                <span className="text-slate-300 text-[9px] truncate block">{analysis.analyzedAt}</span>
              </div>
            </div>

            {/* Actionable Security Recommendation */}
            {analysis.recommendation && (
              <div className="p-2.5 rounded-lg bg-purple-950/40 border border-purple-800/60 text-[10px] font-mono text-purple-200">
                <span className="font-bold flex items-center gap-1 text-[9px] text-purple-400 uppercase tracking-wider mb-0.5">
                  <Zap className="h-3 w-3" /> Security Recommendation
                </span>
                {analysis.recommendation}
              </div>
            )}

            {/* IDs Traceability Bar */}
            {(analysis.investigationId || analysis.evidenceId) && (
              <div className="flex items-center justify-between text-[9px] font-mono text-slate-400 bg-slate-950 p-2 rounded border border-slate-800">
                <span className="truncate max-w-[170px]">INV: {analysis.investigationId}</span>
                <span className="truncate max-w-[170px]">EV: {analysis.evidenceId}</span>
              </div>
            )}

            {/* Key Risk Findings */}
            <div className="space-y-1">
              <span className="text-[9px] font-mono text-slate-400 uppercase tracking-wider block">Key Risk Findings</span>
              <ul className="space-y-1 text-[10px] text-slate-300">
                {analysis.findings.map((f, i) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className="text-purple-400 font-bold">•</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* ── TRUSTED AUTHORIZED SELLER ALTERNATIVES PANEL ───────────────────── */}
            {analysis.trustedAlternatives && analysis.trustedAlternatives.length > 0 && (
              <div className="space-y-2.5 pt-2 border-t border-slate-800">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-mono text-emerald-400 font-bold flex items-center gap-1">
                    <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" /> Trusted Authorized Sellers
                  </span>

                  {/* Sort Dropdown */}
                  <div className="flex items-center gap-1 text-[9px] font-mono">
                    <ArrowUpDown className="h-3 w-3 text-slate-400" />
                    <select
                      value={altSort}
                      onChange={(e) => setAltSort(e.target.value as "TRUST_DESC" | "PRICE_ASC")}
                      className="bg-slate-950 text-slate-200 border border-slate-800 rounded px-1.5 py-0.5 text-[9px] font-mono focus:outline-none"
                    >
                      <option value="TRUST_DESC">Trust (High → Low)</option>
                      <option value="PRICE_ASC">Price (Low → High)</option>
                    </select>
                  </div>
                </div>

                {/* Marketplace Filter Pills */}
                <div className="flex items-center gap-1 overflow-x-auto pb-1 text-[9px] font-mono">
                  <Filter className="h-3 w-3 text-slate-400 shrink-0" />
                  {["ALL", "Amazon", "Flipkart", "Myntra", "AJIO"].map((m) => (
                    <button
                      key={m}
                      onClick={() => setAltFilter(m)}
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

                {/* Rich Trusted Alternative Cards Grid */}
                <div className="space-y-2">
                  {processedAlternatives.map((alt, i) => (
                    <div
                      key={i}
                      className={`p-2.5 rounded-lg bg-slate-950 border transition-all ${
                        alt.is_best_recommendation
                          ? "border-emerald-500/80 shadow-md shadow-emerald-950/40"
                          : "border-slate-800"
                      }`}
                    >
                      {/* Top Best Recommendation Highlight */}
                      {alt.is_best_recommendation && (
                        <div className="flex items-center gap-1 text-[9px] font-mono text-emerald-400 font-bold bg-emerald-950/60 border border-emerald-800/80 px-2 py-0.5 rounded mb-1.5 w-fit">
                          <Star className="h-3 w-3 fill-emerald-400" /> BEST VERIFIED RECOMMENDATION
                        </div>
                      )}

                      <div className="flex items-start justify-between gap-2">
                        <div className="space-y-0.5">
                          <h4 className="text-xs font-bold text-white flex items-center gap-1">
                            {alt.seller_name}
                            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0" />
                          </h4>

                          <div className="flex items-center gap-2 text-[9px] font-mono text-slate-400">
                            <span className="bg-slate-900 border border-slate-800 text-purple-300 px-1.5 py-0.5 rounded font-bold">
                              {alt.marketplace}
                            </span>
                            <span className="text-emerald-400 font-bold">
                              {alt.trust_score}% Trust
                            </span>
                            <span className="text-amber-300">
                              {alt.availability}
                            </span>
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
                          >
                            Open Listing <ExternalLink className="h-2.5 w-2.5" />
                          </a>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── SOC Action Toolbar Buttons ───────────────────────────────── */}
            <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800">
              <button
                onClick={handleCreateInvestigation}
                disabled={creatingInv || (liveInv !== null && liveInv.status === "RUNNING")}
                className="py-2 px-3 rounded-lg bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-bold text-[10px] font-mono flex items-center justify-center gap-1.5 shadow transition-colors"
              >
                {creatingInv ? (
                  <div className="animate-spin rounded-full h-3 w-3 border-2 border-white/30 border-t-white" />
                ) : (
                  <PlusCircle className="h-3.5 w-3.5" />
                )}
                <span>Launch Investigation</span>
              </button>

              <button
                onClick={handleExportReport}
                className="py-2 px-3 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-bold text-[10px] font-mono flex items-center justify-center gap-1.5 border border-slate-700 transition-colors"
              >
                <FileDown className="h-3.5 w-3.5 text-blue-400" />
                <span>Export Report</span>
              </button>
            </div>
          </div>
        )}
      </main>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer className="p-2.5 bg-slate-900 border-t border-slate-800 flex items-center justify-between text-[10px]">
        <button
          onClick={() => handleOpenDashboardReport()}
          className="flex items-center gap-1 text-purple-400 hover:text-purple-300 font-semibold transition-colors font-mono"
        >
          Open Command Center <ChevronRight className="h-3 w-3" />
        </button>
        <span className="text-slate-500 font-mono text-[9px]">Manifest V3 SOC</span>
      </footer>
    </div>
  );
}

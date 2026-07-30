import { useState, useEffect } from "react";
import {
  Shield,
  Settings,
  Globe,
  ExternalLink,
  Lock,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Search,
  Wifi,
  WifiOff,
  ChevronRight,
  Database,
  Cpu,
  Layers
} from "lucide-react";
import { useChromeStorage } from "../hooks/useChromeStorage";
import { useActiveTab } from "../hooks/useActiveTab";
import { BackendApiClient } from "../api/client";
import { BackendHealthStatus, SecurityAnalysisResult } from "../types/extension";
import { ChromeStorageService } from "../services/storage.service";
import { DomExtractionEngine } from "../parsers";


export function PopupPage() {
  const { settings } = useChromeStorage();
  const { page, loading: tabLoading } = useActiveTab();

  const [backendStatus, setBackendStatus] = useState<BackendHealthStatus>("CHECKING");
  const [analysis, setAnalysis] = useState<SecurityAnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Check backend health status on load
  useEffect(() => {
    async function checkBackend() {
      setBackendStatus("CHECKING");
      const health = await BackendApiClient.checkHealth(settings.backendUrl);
      setBackendStatus(health.isOnline ? "ONLINE" : "OFFLINE");
    }
    checkBackend();
  }, [settings.backendUrl]);

  // Load existing analysis for active domain if available
  useEffect(() => {
    if (page?.domain) {
      ChromeStorageService.getLastAnalysis(page.domain).then((prev) => {
        if (prev) setAnalysis(prev);
      });
    }
  }, [page?.domain]);

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
        threatLevel: backendResp.threat_level,
        threatScore: backendResp.risk_score,
        sellerTrust: backendResp.seller_trust,
        recommendation: backendResp.recommendation,
        investigationId: backendResp.investigation_id,
        evidenceId: backendResp.evidence_id,
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


  const handleOpenSettings = () => {
    if (typeof chrome !== "undefined" && chrome.runtime && chrome.runtime.openOptionsPage) {
      chrome.runtime.openOptionsPage();
    } else {
      window.open("/src/options/index.html", "_blank");
    }
  };

  const handleOpenDashboard = () => {
    window.open("http://localhost:5173", "_blank");
  };

  return (
    <div className="w-[380px] bg-slate-950 text-white min-h-[500px] flex flex-col font-sans border border-slate-800 shadow-2xl">
      {/* ── Header ──────────────────────────────────────────────────────── */}
      <header className="p-4 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-xl bg-purple-600/20 border border-purple-500/40 flex items-center justify-center text-purple-400 shadow-lg shadow-purple-900/20">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-1.5">
              CounterGuard <span className="text-[10px] bg-purple-950 text-purple-300 font-mono border border-purple-800 px-1.5 py-0.5 rounded">v1.0.0</span>
            </h1>
            <p className="text-[10px] text-slate-400 font-mono">Enterprise Brand Intelligence</p>
          </div>
        </div>

        <button
          onClick={handleOpenSettings}
          className="p-2 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-slate-300 hover:text-white transition-colors"
          title="Open Extension Settings"
        >
          <Settings className="h-4 w-4" />
        </button>
      </header>

      {/* ── Status Bar ─────────────────────────────────────────────────── */}
      <div className="px-4 py-2 bg-slate-900/40 border-b border-slate-800/60 flex items-center justify-between text-[11px] font-mono">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-slate-400">Extension:</span>
          <span className="text-emerald-400 font-bold">ACTIVE</span>
        </div>

        <div className="flex items-center gap-1.5">
          {backendStatus === "ONLINE" ? (
            <>
              <Wifi className="h-3 w-3 text-emerald-400" />
              <span className="text-emerald-400 font-bold">BACKEND ONLINE</span>
            </>
          ) : backendStatus === "OFFLINE" ? (
            <>
              <WifiOff className="h-3 w-3 text-red-400" />
              <span className="text-red-400 font-bold">BACKEND OFFLINE</span>
            </>
          ) : (
            <span className="text-slate-400">Pinging backend...</span>
          )}
        </div>
      </div>

      {/* ── Body ────────────────────────────────────────────────────────── */}
      <main className="flex-1 p-4 space-y-4">
        {/* Active Tab Info Card */}
        <div className="p-3.5 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-[10px] text-slate-400 uppercase tracking-wider font-mono">
            <span className="flex items-center gap-1">
              <Globe className="h-3 w-3 text-purple-400" /> Active Target Site
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
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                {page.faviconUrl && (
                  <img src={page.faviconUrl} alt="" className="h-4 w-4 rounded shrink-0" />
                )}
                <h2 className="text-xs font-bold text-white truncate max-w-[280px]">
                  {page.title}
                </h2>
              </div>
              <p className="text-[11px] font-mono text-purple-300 truncate">
                {page.domain}
              </p>
              {page.isSupportedMarketplace && page.detection && (
                <div className="flex flex-wrap gap-1.5 pt-1">
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
                  {page.detection.productId && !page.detection.asin && !page.detection.flipkartId && (
                    <span className="text-[9px] font-mono font-bold px-2 py-0.5 rounded bg-slate-800 text-indigo-300 border border-indigo-800/60">
                      ID: {page.detection.productId}
                    </span>
                  )}
                </div>
              )}

            </div>
          ) : (
            <p className="text-xs text-slate-400">No active website tab detected.</p>
          )}
        </div>

        {/* Action Button */}
        <button
          onClick={handleAnalyze}
          disabled={analyzing || !page}
          className="w-full py-3 px-4 rounded-xl bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white font-bold text-xs flex items-center justify-center gap-2 shadow-lg shadow-purple-900/30 transition-all hover:scale-[1.01]"
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
          <div className="p-2.5 rounded-lg bg-red-950/60 border border-red-800/60 text-xs text-red-300 text-center">
            {errorMsg}
          </div>
        )}

        {/* Analysis Results Card */}
        {analysis && (
          <div className="p-4 rounded-xl bg-slate-900/90 border border-slate-800 space-y-3 animate-fadeIn">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                {analysis.threatLevel === "HIGH" || analysis.threatLevel === "CRITICAL" ? (
                  <AlertTriangle className="h-4 w-4 text-red-400" />
                ) : analysis.threatLevel === "MEDIUM" ? (
                  <Activity className="h-4 w-4 text-amber-400" />
                ) : (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                )}
                <span className="text-xs font-bold text-white uppercase font-mono">
                  {analysis.verdict}
                </span>
              </div>
              <span
                className={`text-[10px] font-bold px-2 py-0.5 rounded-full font-mono ${
                  analysis.threatLevel === "HIGH"
                    ? "bg-red-500/20 text-red-300 border border-red-500/40"
                    : analysis.threatLevel === "MEDIUM"
                    ? "bg-amber-500/20 text-amber-300 border border-amber-500/40"
                    : "bg-emerald-500/20 text-emerald-300 border border-emerald-500/40"
                }`}
              >
                Score: {analysis.threatScore}/100
              </span>
            </div>

            <div className="grid grid-cols-2 gap-2 text-[10px] font-mono bg-slate-950 p-2.5 rounded-lg border border-slate-800 text-slate-300">
              <div>
                <span className="text-slate-500 block text-[9px]">Seller Trust</span>
                <strong className={analysis.sellerTrust && analysis.sellerTrust >= 70 ? "text-emerald-400 text-xs" : "text-amber-400 text-xs"}>
                  {analysis.sellerTrust ?? 50}%
                </strong>
              </div>
              <div>
                <span className="text-slate-500 block text-[9px]">Confidence</span>
                <strong className="text-emerald-400 text-xs">{analysis.confidenceScore}%</strong>
              </div>
            </div>

            {analysis.recommendation && (
              <div className="p-2 rounded bg-purple-950/40 border border-purple-800/60 text-[10px] font-mono text-purple-200">
                <span className="font-bold block text-[9px] text-purple-400 uppercase">Recommendation</span>
                {analysis.recommendation}
              </div>
            )}

            {(analysis.investigationId || analysis.evidenceId) && (
              <div className="flex items-center gap-1.5 text-[9px] font-mono text-slate-400">
                {analysis.investigationId && (
                  <span className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700">
                    ID: {analysis.investigationId}
                  </span>
                )}
                {analysis.evidenceId && (
                  <span className="bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded border border-slate-700 truncate max-w-[170px]">
                    EV: {analysis.evidenceId}
                  </span>
                )}
              </div>
            )}

            <div className="space-y-1">
              <span className="text-[10px] font-mono text-slate-400 uppercase">Key Security Findings</span>
              <ul className="space-y-1 text-[11px] text-slate-300">
                {analysis.findings.map((f, i) => (
                  <li key={i} className="flex items-start gap-1.5">
                    <span className="text-purple-400 font-bold">•</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>

          </div>
        )}
      </main>

      {/* ── Footer ──────────────────────────────────────────────────────── */}
      <footer className="p-3 bg-slate-900 border-t border-slate-800 flex items-center justify-between text-[11px]">
        <button
          onClick={handleOpenDashboard}
          className="flex items-center gap-1 text-purple-400 hover:text-purple-300 font-semibold transition-colors"
        >
          Open Enterprise Command Center <ChevronRight className="h-3 w-3" />
        </button>
        <span className="text-slate-500 font-mono text-[9px]">Manifest V3</span>
      </footer>
    </div>
  );
}

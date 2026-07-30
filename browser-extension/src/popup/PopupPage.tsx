/**
 * PopupPage.tsx — CounterGuard SOC Extension Popup
 * Optimized with:
 *  - React.lazy + Suspense for tab-level code splitting
 *  - useMemo / useCallback for zero unnecessary re-renders
 *  - Keyboard shortcuts: Alt+C = analyze, Alt+H = history tab
 *  - ARIA live regions, roles, labels for full accessibility
 *  - useOfflineMode hook for graceful offline degradation
 *  - PerformanceService timing around analysis calls
 *  - Loading skeleton fallbacks
 *  - ErrorBoundary wrapping each lazy tab
 */

import { useState, useEffect, useMemo, useCallback, lazy, Suspense, useRef } from "react";
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
  History as HistoryIcon,
  Trash2,
  RotateCcw,
  WifiOff as OfflineIcon,
  Sun,
  Moon,
} from "lucide-react";
import { useChromeStorage } from "../hooks/useChromeStorage";
import { useActiveTab } from "../hooks/useActiveTab";
import { useOfflineMode } from "../hooks/useOfflineMode";
import { BackendApiClient } from "../api/client";
import { BackendHealthStatus, SecurityAnalysisResult } from "../types/extension";
import { TrustedAlternativeItem } from "../types/api";
import { ChromeStorageService } from "../services/storage.service";
import { DomExtractionEngine } from "../parsers";
import { HistoryService, InvestigationHistoryItem } from "../services/history.service";
import { PerformanceService } from "../services/performance.service";
import { SkeletonCard, SkeletonGrid, SkeletonList } from "./components/SkeletonLoader";
import { ErrorBoundary } from "./components/ErrorBoundary";

// ── Lazy-loaded tab content components ─────────────────────────────────────
// Each tab is a separate chunk: only loaded when first activated.
const InspectTab = lazy(() => import("./tabs/InspectTab").then(m => ({ default: m.InspectTab })));
const HistoryTab = lazy(() => import("./tabs/HistoryTab").then(m => ({ default: m.HistoryTab })));

interface ActiveInvState {
  id: string;
  step: number; // 1 to 5
  stepName: string;
  progressPct: number;
  status: "RUNNING" | "COMPLETED" | "CANCELLED" | "FAILED";
}

// ── Shared props types for lazy tab components ──────────────────────────────
export interface InspectTabProps {
  page: ReturnType<typeof useActiveTab>["page"];
  tabLoading: boolean;
  analysis: SecurityAnalysisResult | null;
  analyzing: boolean;
  creatingInv: boolean;
  liveInv: ActiveInvState | null;
  errorMsg: string | null;
  altFilter: string;
  altSort: "TRUST_DESC" | "PRICE_ASC";
  processedAlternatives: TrustedAlternativeItem[];
  onAnalyze: () => void;
  onCreateInvestigation: () => void;
  onCancelInvestigation: () => void;
  onOpenDashboardReport: (id?: string) => void;
  onExportReport: () => void;
  onSetAltFilter: (f: string) => void;
  onSetAltSort: (s: "TRUST_DESC" | "PRICE_ASC") => void;
}

export interface HistoryTabProps {
  historyList: InvestigationHistoryItem[];
  historySearch: string;
  historyFilter: "ALL" | "HIGH" | "MEDIUM" | "SAFE";
  filteredHistory: InvestigationHistoryItem[];
  onSearchChange: (q: string) => void;
  onFilterChange: (f: "ALL" | "HIGH" | "MEDIUM" | "SAFE") => void;
  onExportHistory: () => void;
  onClearAllHistory: () => void;
  onDeleteRecord: (id: string) => void;
  onOpenDashboardReport: (id: string) => void;
}

// ── Skeleton fallback for Suspense ──────────────────────────────────────────
function TabSkeleton({ isHistory }: { isHistory?: boolean }) {
  return (
    <div className="flex-1 p-3.5 space-y-3">
      <SkeletonCard rows={2} />
      {isHistory ? <SkeletonList count={3} /> : <SkeletonGrid />}
    </div>
  );
}

// ════════════════════════════════════════════════════════════════════════════
//  MAIN POPUP PAGE
// ════════════════════════════════════════════════════════════════════════════
export function PopupPage() {
  const { settings, updateSettings } = useChromeStorage();
  const { page, loading: tabLoading } = useActiveTab();
  const { isOffline } = useOfflineMode();

  const [activeTabNav, setActiveTabNav] = useState<"INSPECT" | "HISTORY">("INSPECT");
  const [backendStatus, setBackendStatus] = useState<BackendHealthStatus>("CHECKING");
  const [analysis, setAnalysis] = useState<SecurityAnalysisResult | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [creatingInv, setCreatingInv] = useState(false);
  const [liveInv, setLiveInv] = useState<ActiveInvState | null>(null);
  const [toastMsg, setToastMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [altFilter, setAltFilter] = useState<string>("ALL");
  const [altSort, setAltSort] = useState<"TRUST_DESC" | "PRICE_ASC">("TRUST_DESC");

  const [historyList, setHistoryList] = useState<InvestigationHistoryItem[]>([]);
  const [historySearch, setHistorySearch] = useState<string>("");
  const [historyFilter, setHistoryFilter] = useState<"ALL" | "HIGH" | "MEDIUM" | "SAFE">("ALL");

  // Ref for keyboard shortcut handler deregistration
  const keyHandlerRef = useRef<((e: KeyboardEvent) => void) | null>(null);

  // ── Backend Health Check ─────────────────────────────────────────────────
  useEffect(() => {
    PerformanceService.mark("health-check:start");
    BackendApiClient.checkHealth(settings.backendUrl).then(({ isOnline }) => {
      setBackendStatus(isOnline ? "ONLINE" : "OFFLINE");
      PerformanceService.mark("health-check:end");
      PerformanceService.measure("health-check", "health-check:start", "health-check:end");
    });
  }, [settings.backendUrl]);

  // ── Load cached analysis & history ──────────────────────────────────────
  useEffect(() => {
    if (page?.domain) {
      ChromeStorageService.getLastAnalysis(page.domain).then((prev) => {
        if (prev) setAnalysis(prev);
      });
    }
    HistoryService.getHistory().then(setHistoryList);
  }, [page?.domain]);

  // ── Sync Light / Dark Theme ──────────────────────────────────────────────
  useEffect(() => {
    if (settings.darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [settings.darkMode]);

  // ── Toast auto-clear ─────────────────────────────────────────────────────
  useEffect(() => {
    if (!toastMsg) return;
    const timer = setTimeout(() => setToastMsg(null), 3500);
    return () => clearTimeout(timer);
  }, [toastMsg]);

  // ── Live Investigation Polling ───────────────────────────────────────────
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

  // ── Keyboard Shortcuts ───────────────────────────────────────────────────
  // Alt+C → Run analysis (only on supported product pages)
  // Alt+H → Switch to History tab
  // Escape → Close toast / clear error
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if (e.altKey && e.key === "c") {
        e.preventDefault();
        if (page && !analyzing) handleAnalyze();
      }
      if (e.altKey && e.key === "h") {
        e.preventDefault();
        setActiveTabNav("HISTORY");
      }
      if (e.key === "Escape") {
        setToastMsg(null);
        setErrorMsg(null);
      }
    };
    keyHandlerRef.current = handler;
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, analyzing]);

  // ── Main Threat Inspection Handler ──────────────────────────────────────
  const handleAnalyze = useCallback(async () => {
    if (!page) return;
    setAnalyzing(true);
    setErrorMsg(null);

    try {
      const result = await PerformanceService.time("analyze-product", async () => {
        const extractedCard = DomExtractionEngine.extract(
          document,
          page.marketplaceName || page.domain,
          page.url
        );

        const backendResp = await BackendApiClient.analyzeProductCard(
          settings.backendUrl,
          extractedCard
        );

        const res: SecurityAnalysisResult = {
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
          verdict:
            backendResp.threat_level === "CRITICAL" || backendResp.threat_level === "HIGH"
              ? "SUSPICIOUS COUNTERFEIT RISK"
              : backendResp.threat_level === "MEDIUM"
              ? "UNVERIFIED SELLER LISTING"
              : "CLEAN AUTHENTIC LISTING",
          matchedListingsCount: 1,
          confidenceScore: extractedCard.confidenceScore,
          analyzedAt: new Date().toLocaleTimeString(),
          findings: backendResp.findings,
        };

        if (page.domain) {
          await ChromeStorageService.setLastAnalysis(page.domain, res);
        }

        const newHistoryItem = await HistoryService.addRecord({
          investigationId: backendResp.investigation_id,
          evidenceId: backendResp.evidence_id,
          productTitle: extractedCard.title || page.title || "Target Product",
          sellerName: extractedCard.seller || "Unverified Seller",
          marketplace: page.marketplaceName || page.domain,
          riskScore: backendResp.risk_score,
          threatLevel: backendResp.threat_level,
          recommendation: backendResp.recommendation,
          url: page.url,
        });

        setHistoryList((prev) => [
          newHistoryItem,
          ...prev.filter((h) => h.investigationId !== newHistoryItem.investigationId),
        ]);

        return res;
      });

      setAnalysis(result);
      PerformanceService.logReport();
    } catch (err) {
      setErrorMsg("Failed to connect to CounterGuard backend service.");
    } finally {
      setAnalyzing(false);
    }
  }, [page, settings.backendUrl]);

  // ── Live Investigation ───────────────────────────────────────────────────
  const handleCreateInvestigation = useCallback(async () => {
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

      const newHist = await HistoryService.addRecord({
        investigationId: res.investigationId,
        evidenceId: res.evidenceId || "ev-live",
        productTitle: extractedCard.title || page.title || "Target Product",
        sellerName: extractedCard.seller || "Unverified Seller",
        marketplace: page.marketplaceName || page.domain,
        riskScore: analysis?.threatScore || 85.0,
        threatLevel: analysis?.threatLevel || "HIGH",
        recommendation: "LIVE LANGGRAPH TAKEDOWN IN PROGRESS",
        url: page.url,
      });
      setHistoryList((prev) => [newHist, ...prev.filter((h) => h.investigationId !== newHist.investigationId)]);
    } else {
      setErrorMsg(`Failed to launch investigation: ${res.message}`);
    }
  }, [page, settings.backendUrl, analysis]);

  const handleCancelInvestigation = useCallback(async () => {
    if (!liveInv) return;
    await BackendApiClient.cancelInvestigation(settings.backendUrl, liveInv.id);
    setLiveInv((prev) => (prev ? { ...prev, status: "CANCELLED", stepName: "Cancelled by Analyst" } : null));
    setToastMsg("⛔ Investigation cancelled.");
  }, [liveInv, settings.backendUrl]);

  const handleOpenDashboardReport = useCallback((id?: string) => {
    const invId = id || liveInv?.id || analysis?.investigationId || "inv-sample";
    window.open(`http://localhost:5173/product-intelligence?id=${invId}`, "_blank");
  }, [liveInv, analysis]);

  const handleExportReport = useCallback(() => {
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
  }, [analysis]);

  const handleExportHistory = useCallback(() => {
    const jsonStr = HistoryService.exportHistoryJson(historyList);
    const blob = new Blob([jsonStr], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `counterguard-investigation-history-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
    setToastMsg("📥 Investigation History exported successfully.");
  }, [historyList]);

  const handleDeleteHistoryRecord = useCallback(async (id: string) => {
    await HistoryService.deleteRecord(id);
    setHistoryList((prev) => prev.filter((h) => h.id !== id && h.investigationId !== id));
    setToastMsg("Deleted history record.");
  }, []);

  const handleClearAllHistory = useCallback(async () => {
    await HistoryService.clearHistory();
    setHistoryList([]);
    setToastMsg("Cleared all investigation history.");
  }, []);

  const handleOpenSettings = useCallback(() => {
    if (typeof chrome !== "undefined" && chrome.runtime?.openOptionsPage) {
      chrome.runtime.openOptionsPage();
    } else {
      window.open("/src/options/index.html", "_blank");
    }
  }, []);

  // ── Memoized Derived Data ────────────────────────────────────────────────
  const processedAlternatives = useMemo((): TrustedAlternativeItem[] => {
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
  }, [analysis?.trustedAlternatives, altFilter, altSort]);

  const filteredHistory = useMemo((): InvestigationHistoryItem[] => {
    let list = [...historyList];
    if (historySearch.trim()) {
      const q = historySearch.toLowerCase();
      list = list.filter(
        (h) =>
          h.productTitle.toLowerCase().includes(q) ||
          h.sellerName.toLowerCase().includes(q) ||
          h.marketplace.toLowerCase().includes(q) ||
          h.investigationId.toLowerCase().includes(q)
      );
    }
    if (historyFilter !== "ALL") {
      if (historyFilter === "HIGH") {
        list = list.filter((h) => h.threatLevel === "CRITICAL" || h.threatLevel === "HIGH");
      } else {
        list = list.filter((h) => h.threatLevel === historyFilter);
      }
    }
    return list;
  }, [historyList, historySearch, historyFilter]);

  // ── Inspect tab props object (stable ref avoids prop drilling churn) ─────
  const inspectTabProps: InspectTabProps = useMemo(() => ({
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
    onAnalyze: handleAnalyze,
    onCreateInvestigation: handleCreateInvestigation,
    onCancelInvestigation: handleCancelInvestigation,
    onOpenDashboardReport: handleOpenDashboardReport,
    onExportReport: handleExportReport,
    onSetAltFilter: setAltFilter,
    onSetAltSort: setAltSort,
  }), [
    page, tabLoading, analysis, analyzing, creatingInv, liveInv, errorMsg,
    altFilter, altSort, processedAlternatives,
    handleAnalyze, handleCreateInvestigation, handleCancelInvestigation,
    handleOpenDashboardReport, handleExportReport,
  ]);

  const historyTabProps: HistoryTabProps = useMemo(() => ({
    historyList,
    historySearch,
    historyFilter,
    filteredHistory,
    onSearchChange: setHistorySearch,
    onFilterChange: setHistoryFilter,
    onExportHistory: handleExportHistory,
    onClearAllHistory: handleClearAllHistory,
    onDeleteRecord: handleDeleteHistoryRecord,
    onOpenDashboardReport: handleOpenDashboardReport,
  }), [
    historyList, historySearch, historyFilter, filteredHistory,
    handleExportHistory, handleClearAllHistory, handleDeleteHistoryRecord, handleOpenDashboardReport,
  ]);

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div
      className="w-[420px] bg-slate-950 text-white min-h-[640px] flex flex-col font-sans border border-slate-800 shadow-2xl"
      role="application"
      aria-label="CounterGuard Brand Protection Extension"
    >
      {/* ── ARIA Live Region for toasts/notifications ── */}
      <div aria-live="polite" aria-atomic="true" className="sr-only" id="cg-live-region">
        {toastMsg}
      </div>

      {/* ── Toast Notification Banner ── */}
      {toastMsg && (
        <div
          role="status"
          className="bg-purple-600 text-white px-3 py-2 text-xs font-semibold flex items-center justify-between shadow-lg animate-slideInDown font-mono"
        >
          <span>{toastMsg}</span>
          <button
            onClick={() => setToastMsg(null)}
            className="text-white/80 hover:text-white font-bold text-sm ml-2"
            aria-label="Dismiss notification"
          >
            ×
          </button>
        </div>
      )}

      {/* ── Offline Banner ── */}
      {isOffline && (
        <div
          role="alert"
          className="cg-offline-banner border px-3 py-1.5 flex items-center gap-2 text-[10px] font-mono text-red-300 animate-slideInDown"
        >
          <OfflineIcon className="h-3 w-3 text-red-400 shrink-0" />
          <span>
            <strong>OFFLINE MODE</strong> — No internet detected. Showing cached data only.
          </span>
        </div>
      )}

      {/* ── Header ── */}
      <header
        className="p-3.5 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between shadow-sm transition-colors"
        role="banner"
      >
        <div className="flex items-center gap-2.5">
          <div
            className="h-8 w-8 rounded-xl bg-purple-100 dark:bg-purple-600/20 border border-purple-200 dark:border-purple-500/40 flex items-center justify-center text-purple-700 dark:text-purple-400 shadow-sm"
            aria-hidden="true"
          >
            <Shield className="h-4 w-4" />
          </div>
          <div>
            <h1 className="text-xs font-bold tracking-tight text-slate-900 dark:text-white flex items-center gap-1.5">
              CounterGuard{" "}
              <span className="text-[9px] bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-300 font-mono border border-purple-200 dark:border-purple-800/80 px-1.5 py-0.5 rounded font-bold">
                SOC v1.0
              </span>
            </h1>
            <p className="text-[9px] text-slate-500 dark:text-slate-400 font-mono">Enterprise Brand Protection Agent</p>
          </div>
        </div>

        <div className="flex items-center gap-1.5" role="toolbar" aria-label="Extension controls">
          <button
            onClick={() => updateSettings({ darkMode: !settings.darkMode })}
            className="cg-btn-icon"
            title={settings.darkMode ? "Switch to Light Mode" : "Switch to Dark Mode"}
            aria-label="Toggle theme mode"
          >
            {settings.darkMode ? <Sun className="h-3.5 w-3.5 text-amber-400" /> : <Moon className="h-3.5 w-3.5 text-slate-600" />}
          </button>
          <button
            onClick={handleAnalyze}
            disabled={analyzing}
            className="cg-btn-icon"
            title="Refresh Inspection (Alt+C)"
            aria-label="Refresh threat inspection"
            aria-busy={analyzing}
          >
            <RefreshCw className={`h-3.5 w-3.5 ${analyzing ? "animate-spin text-purple-600 dark:text-purple-400" : ""}`} />
          </button>
          <button
            onClick={handleOpenSettings}
            className="cg-btn-icon"
            title="Extension Settings"
            aria-label="Open extension settings"
          >
            <Settings className="h-3.5 w-3.5" />
          </button>
        </div>
      </header>

      {/* ── Tab Switcher ── */}
      <div
        className="flex border-b border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-950 text-[10px] font-mono font-bold"
        role="tablist"
        aria-label="Extension navigation tabs"
      >
        <button
          role="tab"
          id="tab-inspect"
          aria-selected={activeTabNav === "INSPECT"}
          aria-controls="tabpanel-inspect"
          onClick={() => setActiveTabNav("INSPECT")}
          className={`flex-1 py-2.5 text-center flex items-center justify-center gap-1.5 transition-colors ${
            activeTabNav === "INSPECT"
              ? "bg-white dark:bg-slate-900 text-purple-700 dark:text-purple-300 border-b-2 border-purple-600 dark:border-purple-500 font-bold"
              : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
          }`}
        >
          <Search className="h-3 w-3" aria-hidden="true" />
          Threat Inspection
        </button>
        <button
          role="tab"
          id="tab-history"
          aria-selected={activeTabNav === "HISTORY"}
          aria-controls="tabpanel-history"
          onClick={() => setActiveTabNav("HISTORY")}
          className={`flex-1 py-2.5 text-center flex items-center justify-center gap-1.5 transition-colors ${
            activeTabNav === "HISTORY"
              ? "bg-white dark:bg-slate-900 text-purple-700 dark:text-purple-300 border-b-2 border-purple-600 dark:border-purple-500 font-bold"
              : "text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-slate-200"
          }`}
        >
          <HistoryIcon className="h-3 w-3" aria-hidden="true" />
          History
          <span className="text-[9px] bg-purple-100 dark:bg-purple-950 text-purple-700 dark:text-purple-400 border border-purple-200 dark:border-purple-800/60 px-1.5 py-0.5 rounded-full font-bold">
            {historyList.length}
          </span>
        </button>
      </div>

      {/* ── Backend Status Bar ── */}
      <div
        className="px-4 py-1.5 bg-slate-50 dark:bg-slate-900/60 border-b border-slate-200 dark:border-slate-800/80 flex items-center justify-between text-[10px] font-mono"
        role="status"
        aria-label={`Backend status: ${backendStatus === "ONLINE" ? "online" : "offline"}`}
      >
        <span className="text-slate-500 dark:text-slate-400 flex items-center gap-1">
          <Activity className="h-3 w-3 text-purple-600 dark:text-purple-400" aria-hidden="true" />
          Backend Engine:
        </span>
        <div className="flex items-center gap-1.5">
          {backendStatus === "ONLINE" ? (
            <>
              <Wifi className="h-3 w-3 text-emerald-600 dark:text-emerald-400" aria-hidden="true" />
              <span className="text-emerald-600 dark:text-emerald-400 font-bold">FASTAPI ONLINE (Port 8000)</span>
            </>
          ) : (
            <>
              <WifiOff className="h-3 w-3 text-red-600 dark:text-red-400" aria-hidden="true" />
              <span className="text-red-600 dark:text-red-400 font-bold">BACKEND OFFLINE (Local Mode)</span>
            </>
          )}
        </div>
      </div>

      {/* ── Main Content (Lazy-loaded tab panels) ── */}
      {activeTabNav === "INSPECT" ? (
        <main
          id="tabpanel-inspect"
          role="tabpanel"
          aria-labelledby="tab-inspect"
          className="flex-1 overflow-y-auto max-h-[500px]"
        >
          <ErrorBoundary fallbackLabel="Threat Inspection Error">
            <Suspense fallback={<TabSkeleton />}>
              <InspectTab {...inspectTabProps} />
            </Suspense>
          </ErrorBoundary>
        </main>
      ) : (
        <main
          id="tabpanel-history"
          role="tabpanel"
          aria-labelledby="tab-history"
          className="flex-1 overflow-y-auto max-h-[500px]"
        >
          <ErrorBoundary fallbackLabel="Investigation History Error">
            <Suspense fallback={<TabSkeleton isHistory />}>
              <HistoryTab {...historyTabProps} />
            </Suspense>
          </ErrorBoundary>
        </main>
      )}

      {/* ── Footer ── */}
      <footer
        className="p-2.5 bg-slate-900 border-t border-slate-800 flex items-center justify-between text-[10px]"
        role="contentinfo"
      >
        <button
          onClick={() => handleOpenDashboardReport()}
          className="flex items-center gap-1 text-purple-400 hover:text-purple-300 font-semibold transition-colors font-mono"
          aria-label="Open CounterGuard Command Center dashboard"
        >
          Open Command Center <ChevronRight className="h-3 w-3" aria-hidden="true" />
        </button>
        <span className="text-slate-500 font-mono text-[9px]" aria-label="Extension version: Manifest V3 SOC">
          Manifest V3 SOC
        </span>
      </footer>
    </div>
  );
}

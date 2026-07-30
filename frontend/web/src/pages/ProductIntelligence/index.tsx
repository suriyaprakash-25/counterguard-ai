/**
 * ProductIntelligence/index.tsx — Enterprise SOC Platform Command Center
 * Assembles all 18 Enterprise SOC phases into an integrated control room workspace.
 */
import { useState, useCallback, useMemo, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Layers, Scale, List, LayoutGrid, Sparkles, FileText, Activity } from 'lucide-react';

import {
  useProductDiscovery,
  useSupportedMarketplaces,
  useLaunchInvestigations,
  useBatchStatus,
  useGenerateProductReport,
} from '../../hooks/useDiscovery';
import type { ListingCandidate, ProductIntelligenceReport } from '../../types/discovery';
import { candidateToLaunchItem } from '../../types/discovery';

import { ProductSearchBar } from './components/ProductSearchBar';
import { CommandCenterHeader } from './components/CommandCenterHeader';
import { MarketplaceHealthWidget } from './components/MarketplaceHealthWidget';
import { MarketplaceResultsTable } from './components/MarketplaceResultsTable';
import { ListingComparisonView } from './components/ListingComparisonView';
import { InvestigationLauncher } from './components/InvestigationLauncher';
import { ProductIntelligenceReportView } from './components/ProductIntelligenceReportView';
import { CandidateDetailsDrawer } from './components/CandidateDetailsDrawer';
import { StickyComparisonToolbar } from './components/StickyComparisonToolbar';
import { IntelligenceCommandSidebar } from './components/IntelligenceCommandSidebar';

// SOC Enterprise Subsystems (Phases 1, 2, 3, 5, 7, 9, 10)
import { LiveDiscoveryPipeline } from './components/LiveDiscoveryPipeline';
import { LiveInvestigationPipeline } from './components/LiveInvestigationPipeline';
import { LiveActivityFeed, FeedEvent } from './components/LiveActivityFeed';
import { SavedSearchesWidget } from './components/SavedSearchesWidget';
import { ExportCenter } from './components/ExportCenter';
import { SOCAnalyticsWidgets } from './components/SOCAnalyticsWidgets';
import { HistoricalMemoryPanel } from './components/HistoricalMemoryPanel';
import { ThreatScoreBreakdown } from './components/ThreatScoreBreakdown';
import { ThreatIntelligenceReportViewer } from './components/ThreatIntelligenceReportViewer';
import { RecommendationPanel } from './components/RecommendationPanel';
import { NotificationToastContainer, ToastMessage } from '../../components/common/NotificationToastContainer';

type ViewMode = 'table' | 'groups';

export default function ProductIntelligence() {
  const navigate = useNavigate();

  // ── Search & Filter State ──────────────────────────────────────────────────
  const [query, setQuery] = useState('');
  const [submittedQuery, setSubmittedQuery] = useState('');
  const [activeMarketplaces, setActiveMarketplaces] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<ViewMode>('table');

  // ── Enterprise Toast & Telemetry Feed State ───────────────────────────────
  const [toasts, setToasts] = useState<ToastMessage[]>([]);
  const [activityEvents, setActivityEvents] = useState<FeedEvent[]>([]);

  const addToast = (type: ToastMessage['type'], title: string, description?: string) => {
    const newToast: ToastMessage = {
      id: `toast-${Date.now()}-${Math.random()}`,
      type,
      title,
      description,
      timestamp: new Date().toLocaleTimeString(),
    };
    setToasts((prev) => [newToast, ...prev].slice(0, 4));
  };

  const addActivityEvent = (type: FeedEvent['type'], title: string, detail?: string) => {
    const newEvt: FeedEvent = {
      id: `evt-${Date.now()}-${Math.random()}`,
      timestamp: new Date().toLocaleTimeString(),
      type,
      title,
      detail,
    };
    setActivityEvents((prev) => [newEvt, ...prev].slice(0, 15));
  };

  // ── Discovery Hooks ────────────────────────────────────────────────────────
  const {
    mutate: searchProducts,
    data: searchResult,
    isPending: isSearching,
    isError: isSearchError,
    reset: resetSearch,
  } = useProductDiscovery();

  const { data: marketplacesData } = useSupportedMarketplaces();
  const supportedMarketplaces = marketplacesData?.supported_marketplaces ?? [];

  // ── Candidate Selection & Drawer State ─────────────────────────────────────
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [comparedIds, setComparedIds] = useState<Set<string>>(new Set());
  const [inspectedCandidate, setInspectedCandidate] = useState<ListingCandidate | null>(null);

  // ── Batch Launch Hooks ─────────────────────────────────────────────────────
  const { mutate: launchBatch, data: launchResult, isPending: isLaunching, reset: resetLaunch } = useLaunchInvestigations();
  const [activeBatchId, setActiveBatchId] = useState<string | null>(null);
  const { data: batchStatus } = useBatchStatus(activeBatchId);

  // ── Derived Data ──────────────────────────────────────────────────────────
  const candidates = searchResult?.candidates ?? [];
  const listingGroups = searchResult?.listing_groups ?? [];
  const hasResults = candidates.length > 0;

  const selectedCandidates = useMemo(() => candidates.filter((c) => selectedIds.has(c.id)), [candidates, selectedIds]);
  const comparedCandidates = useMemo(() => candidates.filter((c) => comparedIds.has(c.id)), [candidates, comparedIds]);

  const groupPriceAvg: number | null = useMemo(() => {
    if (!listingGroups.length) return null;
    return listingGroups[0]?.price_range?.avg ?? null;
  }, [listingGroups]);

  // ── Report State ───────────────────────────────────────────────────────────
  const { mutate: generateReport, isPending: isGeneratingReport } = useGenerateProductReport();
  const [activeReport, setActiveReport] = useState<ProductIntelligenceReport | null>(null);

  // ── Handlers ──────────────────────────────────────────────────────────────
  const handleSearchWithQuery = useCallback(
    (qString: string) => {
      if (!qString.trim() || isSearching) return;
      setSubmittedQuery(qString.trim());
      setSelectedIds(new Set());
      setComparedIds(new Set());
      setActiveBatchId(null);
      resetLaunch();

      addActivityEvent('info', `Discovery search initiated: "${qString.trim()}"`, 'Scanning 6 supported marketplace adapters');

      searchProducts(
        {
          query: qString.trim(),
          marketplaces: activeMarketplaces.size > 0 ? Array.from(activeMarketplaces) : undefined,
          limit_per_marketplace: 5,
        },
        {
          onSuccess: (data) => {
            addToast('success', 'Discovery Completed', `Discovered ${data.candidates.length} candidates across ${data.marketplaces_searched.length} platforms.`);
            addActivityEvent('success', `Discovery search completed`, `Discovered ${data.candidates.length} candidate listings in ${data.metadata.duration_ms}ms.`);
          },
          onError: () => {
            addToast('error', 'Discovery Failed', 'Check network connectivity or backend server API.');
          },
        }
      );
    },
    [isSearching, activeMarketplaces, searchProducts, resetLaunch]
  );

  const handleSearch = () => handleSearchWithQuery(query);

  const handleToggleSelect = useCallback((id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else if (next.size < 10) next.add(id);
      return next;
    });
  }, []);

  const handleSelectAll = useCallback(() => {
    if (candidates.every((c) => selectedIds.has(c.id))) {
      setSelectedIds(new Set());
    } else {
      setSelectedIds(new Set(candidates.map((c) => c.id)));
    }
  }, [candidates, selectedIds]);

  const handleToggleCompare = useCallback((candidate: ListingCandidate) => {
    setComparedIds((prev) => {
      const next = new Set(prev);
      if (next.has(candidate.id)) {
        next.delete(candidate.id);
      } else if (next.size < 4) {
        next.add(candidate.id);
      }
      return next;
    });
  }, []);

  const handleLaunchBatch = useCallback(() => {
    if (selectedCandidates.length === 0) return;
    launchBatch(
      {
        candidates: selectedCandidates.map(candidateToLaunchItem),
        investigation_type: 'Counterfeit Detection',
        planner_strategy: 'Balanced Investigation',
        priority: 'high',
      },
      {
        onSuccess: (data) => {
          setActiveBatchId(data.batch_id);
          setSelectedIds(new Set());
          addToast('success', 'Swarm Investigation Launched', `Dispatched parallel swarm batch ${data.batch_id} (${data.total_launched} cases).`);
          addActivityEvent('warning', `Parallel swarm batch ${data.batch_id} launched`, `Analyzing ${data.total_launched} target listings.`);
        },
      }
    );
  }, [selectedCandidates, launchBatch]);

  const handleLaunchSingle = useCallback(
    (candidate: ListingCandidate) => {
      launchBatch(
        {
          candidates: [candidateToLaunchItem(candidate)],
          investigation_type: 'Counterfeit Detection',
          planner_strategy: 'Balanced Investigation',
          priority: 'high',
        },
        {
          onSuccess: (data) => {
            setActiveBatchId(data.batch_id);
            addToast('success', 'Single Investigation Launched', `Swarm analyzing ${candidate.title} on ${candidate.marketplace}.`);
          },
        }
      );
    },
    [launchBatch]
  );

  const handleToggleMarketplace = useCallback((mp: string) => {
    setActiveMarketplaces((prev) => {
      const next = new Set(prev);
      if (next.has(mp)) next.delete(mp); else next.add(mp);
      return next;
    });
  }, []);

  const handleGenerateReport = useCallback(() => {
    const invIds = launchResult?.investigation_ids ?? Array.from(selectedIds);
    const targetIds = invIds.length > 0 ? invIds : candidates.slice(0, 3).map((c) => c.id);
    if (targetIds.length === 0) return;

    generateReport(
      {
        investigation_ids: targetIds,
        product_name: submittedQuery || 'CMF Buds 2a',
      },
      {
        onSuccess: (report) => {
          setActiveReport(report);
          addToast('success', 'Executive Report Synthesized', `Generated report for ${report.product_name} (${report.overall_risk_level} Risk).`);
          addActivityEvent('critical', `Product Intelligence Report generated`, `Product risk: ${report.overall_product_risk}/100 (${report.overall_risk_level}).`);
        },
      }
    );
  }, [launchResult, selectedIds, candidates, submittedQuery, generateReport]);

  return (
    <div className="space-y-6 pb-24 text-slate-900 dark:text-slate-100">
      {/* Toast Notifications */}
      <NotificationToastContainer toasts={toasts} onDismiss={(id) => setToasts((prev) => prev.filter((t) => t.id !== id))} />

      {/* Product Intelligence Report Modal */}
      {activeReport && (
        <ProductIntelligenceReportView
          report={activeReport}
          onClose={() => setActiveReport(null)}
          onNavigateToCase={(invId) => {
            setActiveReport(null);
            navigate(`/investigations/${invId}`);
          }}
        />
      )}

      {/* Candidate Lineage & Details Drawer */}
      <CandidateDetailsDrawer
        candidate={inspectedCandidate}
        onClose={() => setInspectedCandidate(null)}
        onLaunchSingle={handleLaunchSingle}
      />

      {/* Page Header Title */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-2xl font-bold flex items-center gap-3">
            <div className="h-9 w-9 rounded-xl bg-violet-100 dark:bg-violet-900/40 border border-violet-200 dark:border-violet-700 flex items-center justify-center">
              <Sparkles className="h-5 w-5 text-violet-600 dark:text-violet-400" />
            </div>
            Enterprise SOC Product Intelligence Command Center
          </h1>
          <p className="text-slate-600 dark:text-slate-400 text-sm mt-1">
            Real-time multi-marketplace discovery, live swarm telemetry, threat ranking & legal export center
          </p>
        </div>

        {/* Action Header */}
        <div className="flex items-center gap-2">
          {hasResults && (
            <button
              id="generate-product-report-btn"
              onClick={handleGenerateReport}
              disabled={isGeneratingReport}
              className="flex items-center gap-2 px-4 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 active:bg-violet-800 text-white text-xs font-semibold shadow-sm transition-all shrink-0"
            >
              <FileText className="h-4 w-4" />
              {isGeneratingReport ? 'Synthesizing…' : 'Generate Executive Report'}
            </button>
          )}

          {/* View mode toggle */}
          {hasResults && (
            <div className="flex items-center gap-1 bg-slate-100 dark:bg-slate-800 rounded-xl p-1 border border-slate-200 dark:border-slate-700">
              <button
                onClick={() => setViewMode('table')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  viewMode === 'table'
                    ? 'bg-white dark:bg-slate-700 text-violet-700 dark:text-violet-300 shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <List className="h-3.5 w-3.5" /> All Listings
              </button>
              <button
                onClick={() => setViewMode('groups')}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  viewMode === 'groups'
                    ? 'bg-white dark:bg-slate-700 text-violet-700 dark:text-violet-300 shadow-sm'
                    : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'
                }`}
              >
                <LayoutGrid className="h-3.5 w-3.5" /> Groups
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Phase 7 & 8 — Saved Searches & Pinned Products Widget */}
      <SavedSearchesWidget onSelectQuery={(q) => { setQuery(q); handleSearchWithQuery(q); }} />

      {/* PHASE 2 — Enterprise Command Center Header Bar */}
      {searchResult && (
        <CommandCenterHeader
          searchResult={searchResult}
          report={activeReport}
          batchStatus={batchStatus ?? null}
        />
      )}

      {/* Search Bar Container */}
      <div className="rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-5 shadow-sm">
        <ProductSearchBar
          query={query}
          onQueryChange={setQuery}
          onSearch={handleSearch}
          isSearching={isSearching}
          supportedMarketplaces={supportedMarketplaces}
          activeMarketplaces={activeMarketplaces}
          onToggleMarketplace={handleToggleMarketplace}
          onClearMarketplaces={() => setActiveMarketplaces(new Set())}
        />
      </div>

      {/* PHASE 1 — Live Discovery Execution Pipeline */}
      <LiveDiscoveryPipeline isSearching={isSearching} />

      {/* PHASE 2 — Live Swarm Investigation Pipeline */}
      {batchStatus && <LiveInvestigationPipeline batchStatus={batchStatus} />}

      {/* PHASE 3 — Real-Time Telemetry Activity Feed */}
      {activityEvents.length > 0 && <LiveActivityFeed events={activityEvents} />}

      {/* AI Prescriptive Next-Action Recommendations */}
      {hasResults && <RecommendationPanel query={submittedQuery || query} />}

      {/* Executive Threat Intelligence Report Viewer & Presentation Center */}
      {hasResults && <ThreatIntelligenceReportViewer query={submittedQuery || query} />}

      {/* PHASE 9 — Enterprise Export Center */}
      {hasResults && <ExportCenter candidates={candidates} report={activeReport} query={submittedQuery} />}

      {/* ChromaDB Organizational Memory Panel */}
      {hasResults && <HistoricalMemoryPanel query={submittedQuery || query} />}

      {/* Hierarchical Intelligence Threat Score Matrix (8 Levels) */}
      {hasResults && <ThreatScoreBreakdown />}

      {/* PHASE 10 — SOC Analytics Widgets */}
      {hasResults && <SOCAnalyticsWidgets searchResult={searchResult} />}

      {/* PHASE 3 — Marketplace Health Widget */}
      {searchResult && (
        <MarketplaceHealthWidget
          healthScores={searchResult.metadata?.marketplace_health_scores}
        />
      )}

      {/* Error State */}
      {isSearchError && (
        <div className="rounded-xl border border-red-200 bg-red-50 dark:bg-red-900/20 px-5 py-4 flex items-center gap-3">
          <span className="text-red-700 dark:text-red-300 text-sm font-medium">Search failed. Please check backend connection and retry.</span>
          <button onClick={handleSearch} className="text-xs text-red-800 dark:text-red-200 font-semibold underline ml-auto shrink-0">
            Retry Search
          </button>
        </div>
      )}

      {/* Main Workspace Layout (Table + Sticky Command Sidebar) */}
      {hasResults ? (
        <div className="flex flex-col lg:flex-row gap-6 items-start">
          {/* Main Panel */}
          <div className="flex-1 space-y-6 w-full">
            {/* Investigation Launcher Bar */}
            {(selectedIds.size > 0 || activeBatchId || isLaunching) && (
              <InvestigationLauncher
                selectedCount={selectedIds.size}
                isLaunching={isLaunching}
                batchStatus={batchStatus ?? null}
                onLaunch={handleLaunchBatch}
                onViewReport={handleGenerateReport}
              />
            )}

            {/* Side-by-Side Comparison View */}
            {comparedCandidates.length > 0 && (
              <ListingComparisonView
                candidates={comparedCandidates}
                onRemove={(id) => handleToggleCompare(candidates.find((c) => c.id === id)!)}
                onClearAll={() => setComparedIds(new Set())}
              />
            )}

            {/* Table View */}
            {viewMode === 'table' && (
              <MarketplaceResultsTable
                candidates={candidates}
                selectedIds={selectedIds}
                onToggleSelect={handleToggleSelect}
                onSelectAll={handleSelectAll}
                onClearSelection={() => setSelectedIds(new Set())}
                comparisonSet={comparedIds}
                onToggleCompare={handleToggleCompare}
                onViewDetails={(c) => setInspectedCandidate(c)}
                onLaunchSingle={handleLaunchSingle}
                groupPriceAvg={groupPriceAvg}
              />
            )}

            {/* Groups View */}
            {viewMode === 'groups' && (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {listingGroups.map((group) => {
                  const isCritical = group.investigation_priority === 'critical';
                  const isHigh = group.investigation_priority === 'high';
                  const borderColor = isCritical ? 'border-red-300' : isHigh ? 'border-amber-300' : 'border-slate-200 dark:border-slate-800';
                  const accentBar = isCritical ? 'bg-red-500' : isHigh ? 'bg-amber-500' : 'bg-blue-500';
                  const score = group.priority_score?.total_priority_score ?? 0;

                  return (
                    <div
                      key={group.group_id}
                      className={`bg-white dark:bg-slate-900 rounded-xl border ${borderColor} overflow-hidden shadow-sm hover:shadow-md transition-all flex flex-col justify-between`}
                    >
                      <div>
                        <div className={`h-1.5 w-full ${accentBar}`} />
                        <div className="p-4 space-y-3">
                          <div className="flex items-start justify-between gap-2">
                            <h4 className="text-sm font-bold text-slate-900 dark:text-white line-clamp-2" title={group.canonical_title}>
                              {group.canonical_title}
                            </h4>
                            <span className="shrink-0 text-xs font-bold text-slate-700 dark:text-slate-200 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-2 py-0.5 rounded-full">
                              {Math.round(score)}/100
                            </span>
                          </div>
                          <div className="flex flex-wrap gap-1.5">
                            {group.unique_marketplaces.map((mp) => (
                              <span key={mp} className="text-[10px] font-semibold px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                                {mp}
                              </span>
                            ))}
                          </div>
                          <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400 pt-1 border-t border-slate-100 dark:border-slate-800">
                            <span>{group.listing_count} listing(s)</span>
                            {group.price_range.min !== undefined && (
                              <span className="font-bold text-indigo-600 dark:text-indigo-400">
                                ₹{group.price_range.min?.toLocaleString('en-IN', { maximumFractionDigits: 0 })} – ₹{group.price_range.max?.toLocaleString('en-IN', { maximumFractionDigits: 0 })}
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {group.representative && (
                        <div className="p-4 pt-0">
                          <button
                            onClick={() => handleToggleSelect(group.representative!.id)}
                            className="w-full flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-semibold bg-violet-50 dark:bg-slate-800 hover:bg-violet-100 border border-violet-200 dark:border-slate-700 text-violet-700 dark:text-violet-300 transition-colors"
                          >
                            <Layers className="h-3.5 w-3.5" /> Select Representative Listing
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* PHASE 10 — Sticky Command Center Sidebar */}
          <IntelligenceCommandSidebar
            searchResult={searchResult}
            report={activeReport}
            batchStatus={batchStatus ?? null}
            onGenerateReport={handleGenerateReport}
          />
        </div>
      ) : null}

      {/* PHASE 8 — Sticky Docked Toolbar */}
      <StickyComparisonToolbar
        selectedCandidates={selectedCandidates}
        comparisonCandidates={comparedCandidates}
        onOpenCompare={() => setViewMode('table')}
        onClearCompare={() => setComparedIds(new Set())}
        onLaunchBatch={handleLaunchBatch}
      />

      {/* Empty / Idle State */}
      {!isSearching && !hasResults && !isSearchError && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-12 text-center shadow-sm flex flex-col items-center justify-center my-8">
          <div className="h-16 w-16 rounded-2xl bg-violet-100 dark:bg-violet-900/40 border border-violet-200 dark:border-violet-700 flex items-center justify-center mb-4">
            <Sparkles className="h-8 w-8 text-violet-600 dark:text-violet-400" />
          </div>
          <h2 className="text-xl font-bold text-slate-900 dark:text-white mb-2">Enterprise Product Intelligence Command Center</h2>
          <p className="text-slate-600 dark:text-slate-400 text-sm max-w-md mb-8">
            Search for any product to launch real-time multi-marketplace discovery, monitor swarm telemetry, export legal evidence reports, and enforce brand protection.
          </p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-left max-w-xl w-full">
            <div className="p-4 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
              <div className="h-7 w-7 rounded-lg bg-violet-600 text-white font-bold text-xs flex items-center justify-center">1</div>
              <div className="text-xs font-bold text-slate-900 dark:text-white">Live Discovery</div>
              <div className="text-[11px] text-slate-600 dark:text-slate-400">Search "Nothing Charger" or "Sony WH-1000XM5"</div>
            </div>
            <div className="p-4 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
              <div className="h-7 w-7 rounded-lg bg-violet-600 text-white font-bold text-xs flex items-center justify-center">2</div>
              <div className="text-xs font-bold text-slate-900 dark:text-white">Swarm Telemetry & Provenance</div>
              <div className="text-[11px] text-slate-600 dark:text-slate-400">Inspect multi-stage confidence and visual lineage timelines</div>
            </div>
            <div className="p-4 bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 rounded-xl space-y-2">
              <div className="h-7 w-7 rounded-lg bg-violet-600 text-white font-bold text-xs flex items-center justify-center">3</div>
              <div className="text-xs font-bold text-slate-900 dark:text-white">Export & Enforce</div>
              <div className="text-[11px] text-slate-600 dark:text-slate-400">Export CSV, JSON, and PDF legal report bundles</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

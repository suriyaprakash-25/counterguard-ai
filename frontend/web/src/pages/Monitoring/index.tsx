/**
 * Monitoring/index.tsx — Phase 4: Enterprise Command Center
 * Continuous Monitoring Dashboard with:
 * - Live Marketplace Intelligence Panel (403/429/latency health cards)
 * - Watchlist Creation Modal
 * - Evidence Archive Inspector
 * - Real-time change detection feed
 */
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { PageHeader } from '../../components/common/PageHeader';
import { Button } from '../../components/common/Button';
import { LoadingSkeleton } from '../../components/common/LoadingSkeleton';
import {
  Play, Pause, RefreshCw, Clock, Activity, AlertTriangle, ShieldCheck,
  CheckCircle2, Zap, Layers, Plus, Database, Globe, XCircle, TrendingUp,
  Download, Eye, ChevronDown, ChevronUp, FileText, X, Shield, Wifi, Network, Code, Cpu
} from 'lucide-react';
import { apiClient, endpoints } from '../../shared/api';
import { ListingLineageDrawer } from '../../components/common/ListingLineageDrawer';

/* ─── Types ─────────────────────────────────────────────────────────────── */

export interface MonitoringJob {
  job_id: string;
  name: string;
  frequency: string;
  status: 'ACTIVE' | 'PAUSED' | 'RUNNING' | 'FAILED';
  last_run?: string;
  next_run?: string;
  total_scans: number;
  discovered_listings: number;
  investigations_triggered: number;
}

export interface ChangeEvent {
  event_id: string;
  change_type: string;
  marketplace: string;
  product_name: string;
  details: string;
  timestamp: string;
}

export interface MonitoringStatusResponse {
  active_jobs: number;
  paused_jobs: number;
  running_jobs: number;
  completed_scans: number;
  total_discovered_listings: number;
  total_auto_investigations: number;
  jobs: MonitoringJob[];
  recent_events: ChangeEvent[];
}

export interface ProviderHealth {
  marketplace: string;
  status: 'HEALTHY' | 'DEGRADED' | 'BLOCKED' | 'RATE_LIMITED';
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  blocked_403_count: number;
  rate_limit_429_count: number;
  captcha_count: number;
  average_latency_ms: number;
  success_rate_pct: number;
  last_successful_at?: string;
  last_failure_at?: string;
  last_error_message?: string;
}

export interface ArchiveEntry {
  archive_id: string;
  marketplace: string;
  source_url: string;
  http_status: number;
  response_hash: string;
  parser_version: string;
  retrieval_timestamp: string;
  compressed_size_bytes: number;
}

/* ─── Marketplace Health Card ───────────────────────────────────────────── */

const statusConfig: Record<string, { color: string; bg: string; dot: string; icon: React.ReactNode }> = {
  HEALTHY:      { color: 'text-emerald-700 dark:text-emerald-300', bg: 'bg-emerald-50 dark:bg-emerald-950/60 border-emerald-200 dark:border-emerald-800', dot: 'bg-emerald-500', icon: <CheckCircle2 className="h-3.5 w-3.5" /> },
  DEGRADED:     { color: 'text-amber-700 dark:text-amber-300',     bg: 'bg-amber-50 dark:bg-amber-950/60 border-amber-200 dark:border-amber-800',       dot: 'bg-amber-500',   icon: <AlertTriangle className="h-3.5 w-3.5" /> },
  BLOCKED:      { color: 'text-red-700 dark:text-red-300',         bg: 'bg-red-50 dark:bg-red-950/60 border-red-200 dark:border-red-800',               dot: 'bg-red-500',     icon: <XCircle className="h-3.5 w-3.5" /> },
  RATE_LIMITED: { color: 'text-orange-700 dark:text-orange-300',   bg: 'bg-orange-50 dark:bg-orange-950/60 border-orange-200 dark:border-orange-800',   dot: 'bg-orange-500',  icon: <Clock className="h-3.5 w-3.5" /> },
};

function MarketplaceCard({ p }: { p: ProviderHealth }) {
  const cfg = statusConfig[p.status] ?? statusConfig.HEALTHY;
  return (
    <div className={`rounded-xl border p-4 space-y-3 ${cfg.bg}`}>
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Globe className="h-4 w-4 text-slate-500" />
          <span className="text-sm font-bold text-slate-900 dark:text-white">{p.marketplace}</span>
        </div>
        <span className={`flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full ${cfg.color} bg-white/50 dark:bg-black/20`}>
          {cfg.icon}
          {p.status}
        </span>
      </div>

      <div className="space-y-1.5">
        {/* Success rate bar */}
        <div className="flex justify-between text-[10px] text-slate-500 font-mono">
          <span>Success Rate</span>
          <span className="font-bold text-slate-700 dark:text-slate-300">{p.success_rate_pct.toFixed(1)}%</span>
        </div>
        <div className="h-1.5 rounded-full bg-slate-200 dark:bg-slate-700 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all ${p.success_rate_pct >= 90 ? 'bg-emerald-500' : p.success_rate_pct >= 70 ? 'bg-amber-500' : 'bg-red-500'}`}
            style={{ width: `${Math.min(p.success_rate_pct, 100)}%` }}
          />
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 text-center text-[10px]">
        <div className="bg-white/60 dark:bg-black/20 rounded-lg p-1.5">
          <div className="font-bold text-slate-800 dark:text-slate-200 font-mono">{p.total_requests}</div>
          <div className="text-slate-500">Requests</div>
        </div>
        <div className="bg-white/60 dark:bg-black/20 rounded-lg p-1.5">
          <div className="font-bold text-slate-800 dark:text-slate-200 font-mono">{p.average_latency_ms.toFixed(0)}ms</div>
          <div className="text-slate-500">Avg Latency</div>
        </div>
        <div className={`bg-white/60 dark:bg-black/20 rounded-lg p-1.5 ${p.blocked_403_count > 0 ? 'text-red-600 dark:text-red-400' : ''}`}>
          <div className="font-bold font-mono">{p.blocked_403_count}</div>
          <div className="text-slate-500">403 Blocks</div>
        </div>
      </div>

      {p.last_successful_at && (
        <div className="text-[10px] text-slate-400 font-mono truncate">
          Last OK: {new Date(p.last_successful_at).toLocaleTimeString()}
        </div>
      )}
    </div>
  );
}

/* ─── Watchlist Create Modal ────────────────────────────────────────────── */

const CATEGORIES = ['BRAND', 'PRODUCT', 'SELLER', 'PHONE', 'EMAIL', 'GST', 'FRAUD_RING', 'MARKETPLACE'];

function CreateWatchlistModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [form, setForm] = useState({ name: '', category: 'PRODUCT', value: '' });
  const [error, setError] = useState('');

  const createMutation = useMutation({
    mutationFn: async () => {
      await apiClient.post(endpoints.watchlists.create, {
        name: form.name,
        category: form.category,
        value: form.value,
      });
    },
    onSuccess: () => { onCreated(); onClose(); },
    onError: (e: any) => setError(e?.response?.data?.detail || 'Failed to create watchlist.'),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="w-full max-w-md bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-700 p-6 space-y-5">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-base font-bold text-slate-900 dark:text-white flex items-center gap-2">
              <Shield className="h-4 w-4 text-violet-500" />
              Create Watchlist Target
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">Add a new target to continuous autonomous monitoring.</p>
          </div>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 dark:hover:text-slate-300">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="space-y-3">
          <div>
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">Display Name *</label>
            <input
              className="w-full text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-violet-500/40"
              placeholder="e.g. Nike Air Force 1 - Brand Protection"
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
            />
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">Category *</label>
            <select
              className="w-full text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-violet-500/40"
              value={form.category}
              onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
            >
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
          </div>

          <div>
            <label className="text-xs font-semibold text-slate-600 dark:text-slate-400 block mb-1">Search Query / Identifier *</label>
            <input
              className="w-full text-sm bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg px-3 py-2 text-slate-900 dark:text-white outline-none focus:ring-2 focus:ring-violet-500/40"
              placeholder="e.g. Nike Air Force 1 counterfeit"
              value={form.value}
              onChange={e => setForm(f => ({ ...f, value: e.target.value }))}
            />
          </div>
        </div>

        {error && (
          <div className="text-xs text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg p-2">
            {error}
          </div>
        )}

        <div className="flex gap-3 pt-1">
          <Button variant="outline" size="sm" onClick={onClose} className="flex-1">Cancel</Button>
          <Button
            size="sm"
            className="flex-1"
            disabled={!form.name || !form.value || createMutation.isPending}
            onClick={() => createMutation.mutate()}
          >
            {createMutation.isPending ? 'Creating...' : 'Create Watchlist'}
          </Button>
        </div>
      </div>
    </div>
  );
}

/* ─── Parser Inspector Panel (Feature 9) ────────────────────────────────── */

interface ParserInspectorData {
  marketplace: string;
  parser_name: string;
  parser_version: string;
  http_status: number;
  html_size_bytes: number;
  dom_nodes: number;
  selectors_executed: number;
  selectors_failed: number;
  cards_found: number;
  cards_parsed: number;
  cards_rejected: number;
  duration_ms: number;
  parser_success_pct: number;
  confidence_score: number;
  confidence_explanation: string;
  rejected_reasons: { position: number; reason: string; raw_snippet?: string }[];
  last_execution_at: string;
}

function ParserInspectorPanel() {
  const [open, setOpen] = useState(false);

  const { data, isLoading } = useQuery<{ parsers: ParserInspectorData[] }>({
    queryKey: ['providers', 'parserInspector'],
    queryFn: async () => {
      const resp = await apiClient.get(endpoints.providers.parserInspector);
      return resp.data;
    },
    refetchInterval: 30_000,
    staleTime: 25_000,
  });

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
      <button
        className="w-full flex items-center justify-between p-5 text-left hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
        onClick={() => setOpen(v => !v)}
      >
        <div className="flex items-center gap-3">
          <Code className="h-5 w-5 text-indigo-500" />
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
              Enterprise Parser Inspector & Diagnostics
              <span className="text-[10px] bg-indigo-100 dark:bg-indigo-950 text-indigo-700 dark:text-indigo-300 font-mono px-2 py-0.5 rounded-full">
                Auto-Refresh 30s
              </span>
            </h3>
            <p className="text-[10px] text-slate-500 mt-0.5">
              Live selector extraction statistics, DOM node counts, rejection diagnostics & confidence scoring
            </p>
          </div>
        </div>
        {open ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
      </button>

      {open && (
        <div className="border-t border-slate-100 dark:border-slate-800 p-5 space-y-4">
          {isLoading ? (
            <LoadingSkeleton className="h-32 w-full rounded-xl" />
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {(data?.parsers || []).map((p) => (
                <div
                  key={p.marketplace}
                  className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/80 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-sm font-bold text-slate-900 dark:text-white">{p.marketplace}</h4>
                      <span className="text-[10px] font-mono text-slate-400">{p.parser_version}</span>
                    </div>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${
                      p.http_status === 200 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300'
                    }`}>
                      HTTP {p.http_status}
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-2 text-[11px] text-slate-600 dark:text-slate-300 font-mono bg-white dark:bg-slate-900/80 p-2.5 rounded-lg border border-slate-200/80 dark:border-slate-800">
                    <div>
                      <span className="text-slate-400 block text-[9px]">DOM Nodes</span>
                      <strong>{p.dom_nodes.toLocaleString()}</strong>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[9px]">HTML Size</span>
                      <strong>{(p.html_size_bytes / 1024).toFixed(0)} KB</strong>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[9px]">Selectors (Exec/Fail)</span>
                      <strong>{p.selectors_executed} / {p.selectors_failed}</strong>
                    </div>
                    <div>
                      <span className="text-slate-400 block text-[9px]">Cards (Found/Parsed)</span>
                      <strong>{p.cards_found} / {p.cards_parsed}</strong>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <div className="flex justify-between text-[11px]">
                      <span className="text-slate-500 font-medium">Parser Confidence Score:</span>
                      <span className="font-bold text-emerald-600 dark:text-emerald-400">{p.confidence_score}%</span>
                    </div>
                    <div className="h-1.5 w-full bg-slate-200 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500 rounded-full transition-all"
                        style={{ width: `${p.confidence_score}%` }}
                      />
                    </div>
                  </div>

                  {p.rejected_reasons && p.rejected_reasons.length > 0 && (
                    <div className="p-2 rounded bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 text-[10px] text-amber-700 dark:text-amber-300">
                      <strong>Rejected Diagnostics:</strong> {p.rejected_reasons.map(r => r.reason).join(', ')}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

/* ─── Evidence Archive Inspector ────────────────────────────────────────── */

function ArchiveInspector() {
  const [open, setOpen] = useState(false);

  const { data, isLoading } = useQuery<{ archives: ArchiveEntry[]; count: number }>({
    queryKey: ['archive', 'list'],
    queryFn: async () => {
      const resp = await apiClient.get(endpoints.providers.archive + '?limit=20');
      return resp.data;
    },
    enabled: open,
    staleTime: 30_000,
  });

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
      <button
        className="w-full flex items-center justify-between p-5 text-left hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
        onClick={() => setOpen(v => !v)}
      >
        <div className="flex items-center gap-3">
          <Database className="h-5 w-5 text-violet-500" />
          <div>
            <h3 className="text-sm font-bold text-slate-900 dark:text-white">Raw Evidence Archive Inspector</h3>
            <p className="text-[10px] text-slate-500 mt-0.5">Browse SHA-256 cryptographic evidence records with provenance metadata</p>
          </div>
        </div>
        {open ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
      </button>

      {open && (
        <div className="border-t border-slate-100 dark:border-slate-800 p-5 space-y-3">
          {isLoading ? (
            <LoadingSkeleton className="h-24 w-full rounded-xl" />
          ) : !data?.archives?.length ? (
            <div className="text-center py-6 text-slate-500 text-xs space-y-1">
              <Database className="h-8 w-8 mx-auto text-slate-300" />
              <p>No archived evidence yet. Evidence is captured during scheduled monitoring cycles.</p>
            </div>
          ) : (
            <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
              {data.archives.map(a => (
                <div key={a.archive_id} className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-800 text-xs">
                  <div className="flex items-center justify-between mb-1.5">
                    <span className="font-bold text-slate-800 dark:text-slate-200">{a.marketplace}</span>
                    <span className={`px-1.5 py-0.5 rounded text-[9px] font-bold ${a.http_status === 200 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300' : 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300'}`}>
                      HTTP {a.http_status}
                    </span>
                  </div>
                  <div className="text-slate-500 font-mono text-[9px] mb-1 truncate">{a.response_hash}</div>
                  <div className="flex justify-between text-[9px] text-slate-400">
                    <span>{a.parser_version}</span>
                    <span>{(a.compressed_size_bytes / 1024).toFixed(1)} KB compressed</span>
                    <span>{new Date(a.retrieval_timestamp).toLocaleTimeString()}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
          <div className="text-[10px] text-slate-400 font-mono">
            {data?.count ?? 0} archive record(s) found
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── Main Dashboard Component ──────────────────────────────────────────── */

export default function MonitoringDashboard() {
  const queryClient = useQueryClient();
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showHealthPanel, setShowHealthPanel] = useState(true);

  const { data, isLoading, refetch } = useQuery<MonitoringStatusResponse>({
    queryKey: ['monitoring', 'jobs'],
    queryFn: async () => {
      const resp = await apiClient.get(`${endpoints.monitoring.jobs}`);
      return resp.data;
    },
  });

  const { data: providerData, isLoading: isHealthLoading } = useQuery<{ providers: ProviderHealth[] }>({
    queryKey: ['providers', 'health'],
    queryFn: async () => {
      const resp = await apiClient.get(endpoints.providers.health);
      return resp.data;
    },
    refetchInterval: 30_000,
    staleTime: 25_000,
  });

  const triggerRun = useMutation({
    mutationFn: async (job_id: string) => {
      await apiClient.post(`${endpoints.monitoring.run}?job_id=${job_id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['monitoring'] }),
  });

  const togglePause = useMutation({
    mutationFn: async ({ job_id, isPaused }: { job_id: string; isPaused: boolean }) => {
      const endpoint = isPaused ? endpoints.monitoring.resume : endpoints.monitoring.pause;
      await apiClient.post(`${endpoint}?job_id=${job_id}`);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['monitoring'] }),
  });

  const handleExportCSV = () => {
    window.open(endpoints.export.investigations + '?format=csv', '_blank');
  };

  const handleExportHealth = () => {
    window.open(endpoints.export.providerHealth, '_blank');
  };

  const handleCreated = () => {
    queryClient.invalidateQueries({ queryKey: ['monitoring'] });
    queryClient.invalidateQueries({ queryKey: ['watchlists'] });
  };

  if (isLoading) {
    return (
      <div className="space-y-6 pb-16">
        <PageHeader title="Proactive Continuous Monitoring Platform" description="Loading monitoring telemetry..." />
        <LoadingSkeleton className="h-40 w-full rounded-2xl" />
        <LoadingSkeleton className="h-96 w-full rounded-2xl" />
      </div>
    );
  }

  const jobs = data?.jobs || [];
  const events = data?.recent_events || [];
  const providers = providerData?.providers || [];
  const healthyProviders = providers.filter(p => p.status === 'HEALTHY').length;
  const blockedProviders = providers.filter(p => p.status === 'BLOCKED' || p.status === 'DEGRADED').length;

  return (
    <div className="space-y-6 pb-16 text-slate-900 dark:text-slate-100">
      {showCreateModal && (
        <CreateWatchlistModal onClose={() => setShowCreateModal(false)} onCreated={handleCreated} />
      )}

      <PageHeader
        title="Continuous Monitoring Command Center"
        description="Autonomous multi-marketplace surveillance, marketplace intelligence telemetry, and enterprise evidence archive."
      >
        <div className="flex gap-2 flex-wrap">
          <Button variant="outline" size="sm" onClick={handleExportHealth}>
            <Download className="mr-2 h-4 w-4" /> Health CSV
          </Button>
          <Button variant="outline" size="sm" onClick={handleExportCSV}>
            <FileText className="mr-2 h-4 w-4" /> Export Investigations
          </Button>
          <Button variant="outline" size="sm" onClick={() => refetch()}>
            <RefreshCw className="mr-2 h-4 w-4" /> Refresh
          </Button>
          <Button size="sm" onClick={() => setShowCreateModal(true)}>
            <Plus className="mr-2 h-4 w-4" /> New Watchlist
          </Button>
        </div>
      </PageHeader>

      {/* ── Metric Cards ──────────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold">
            <span>Active Watchlists</span>
            <Activity className="h-4 w-4 text-emerald-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">{data?.active_jobs ?? 0} Jobs</div>
          <div className="text-[10px] text-slate-400 font-mono">15m / 30m / 1h Intervals</div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold">
            <span>Completed Scans</span>
            <ShieldCheck className="h-4 w-4 text-violet-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">{data?.completed_scans ?? 0} Scans</div>
          <div className="text-[10px] text-slate-400">Across 6 Marketplaces</div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold">
            <span>Marketplace Availability</span>
            <Wifi className={`h-4 w-4 ${blockedProviders > 0 ? 'text-amber-500' : 'text-emerald-500'}`} />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">{healthyProviders}/{providers.length || 6} Live</div>
          <div className={`text-[10px] font-mono ${blockedProviders > 0 ? 'text-amber-500' : 'text-emerald-500'}`}>
            {blockedProviders > 0 ? `${blockedProviders} Blocked by Anti-Bot` : 'All Marketplaces Healthy'}
          </div>
        </div>

        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl p-4 shadow-sm space-y-1">
          <div className="flex items-center justify-between text-xs text-slate-500 font-semibold">
            <span>Auto Swarm Cases</span>
            <CheckCircle2 className="h-4 w-4 text-blue-500" />
          </div>
          <div className="text-2xl font-bold text-slate-900 dark:text-white">{data?.total_auto_investigations ?? 0} Swarms</div>
          <div className="text-[10px] text-slate-400">Auto-Launched Investigations</div>
        </div>
      </div>

      {/* ── Marketplace Intelligence Panel ───────────────────────────────── */}
      <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl overflow-hidden shadow-sm">
        <button
          className="w-full flex items-center justify-between p-5 text-left hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors"
          onClick={() => setShowHealthPanel(v => !v)}
        >
          <div className="flex items-center gap-3">
            <Globe className="h-5 w-5 text-blue-500" />
            <div>
              <h3 className="text-sm font-bold text-slate-900 dark:text-white">
                Marketplace Intelligence Panel
                {providers.length > 0 && (
                  <span className={`ml-2 text-[10px] font-bold px-2 py-0.5 rounded-full ${
                    blockedProviders === 0
                      ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                      : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                  }`}>
                    {healthyProviders}/{providers.length} HEALTHY
                  </span>
                )}
              </h3>
              <p className="text-[10px] text-slate-500 mt-0.5">Live HTTP success rates, latency, 403/429 block tracking per marketplace</p>
            </div>
          </div>
          {showHealthPanel ? <ChevronUp className="h-4 w-4 text-slate-400" /> : <ChevronDown className="h-4 w-4 text-slate-400" />}
        </button>

        {showHealthPanel && (
          <div className="border-t border-slate-100 dark:border-slate-800 p-5">
            {isHealthLoading ? (
              <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {[...Array(6)].map((_, i) => <LoadingSkeleton key={i} className="h-40 rounded-xl" />)}
              </div>
            ) : providers.length === 0 ? (
              <div className="text-center py-6 text-xs text-slate-500 space-y-1">
                <Globe className="h-8 w-8 mx-auto text-slate-300" />
                <p>Provider health data will appear after the first monitoring cycle completes.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
                {providers.map(p => <MarketplaceCard key={p.marketplace} p={p} />)}
              </div>
            )}
            <div className="mt-3 flex justify-end">
              <button
                onClick={handleExportHealth}
                className="flex items-center gap-1.5 text-[10px] font-semibold text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
              >
                <Download className="h-3 w-3" /> Export Health Report (CSV)
              </button>
            </div>
          </div>
        )}
      </div>

      {/* ── Monitoring Jobs Grid ─────────────────────────────────────────── */}
      {jobs.length === 0 ? (
        <div className="p-8 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 text-center space-y-3">
          <Layers className="h-12 w-12 text-slate-400 mx-auto" />
          <h3 className="text-base font-bold text-slate-900 dark:text-white">No Continuous Monitoring Jobs Active</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            Configure your first automated surveillance job to monitor marketplaces on 15m, 30m, or 24h cron schedules.
          </p>
          <Button size="sm" onClick={() => setShowCreateModal(true)}>
            <Plus className="h-4 w-4 mr-1.5" /> Create First Watchlist
          </Button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Continuous Monitoring Job Schedules</h3>
            <button
              onClick={() => setShowCreateModal(true)}
              className="flex items-center gap-1.5 text-[10px] font-bold text-violet-600 dark:text-violet-400 hover:text-violet-700 transition-colors"
            >
              <Plus className="h-3 w-3" /> Add Watchlist
            </button>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {jobs.map((job) => (
              <div
                key={job.job_id}
                className="p-5 rounded-2xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 shadow-sm space-y-4 flex flex-col justify-between"
              >
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${
                      job.status === 'ACTIVE' || job.status === 'RUNNING'
                        ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300'
                        : 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300'
                    }`}>
                      {job.status}
                    </span>
                    <span className="text-[10px] font-mono text-slate-400">{job.frequency} Cron</span>
                  </div>

                  <h4 className="text-sm font-bold text-slate-900 dark:text-white">{job.name}</h4>

                  <div className="text-xs text-slate-500 space-y-1">
                    <div className="flex justify-between">
                      <span>Total Scans:</span>
                      <span className="font-mono font-semibold text-slate-700 dark:text-slate-300">{job.total_scans}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Discovered:</span>
                      <span className="font-mono font-semibold text-slate-700 dark:text-slate-300">{job.discovered_listings}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Auto Swarms:</span>
                      <span className="font-mono font-semibold text-slate-700 dark:text-slate-300">{job.investigations_triggered}</span>
                    </div>
                    {job.next_run && (
                      <div className="flex justify-between">
                        <span>Next Run:</span>
                        <span className="font-mono font-semibold text-blue-600 dark:text-blue-400 text-[10px]">
                          {new Date(job.next_run).toLocaleTimeString()}
                        </span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="pt-3 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => togglePause.mutate({ job_id: job.job_id, isPaused: job.status === 'PAUSED' })}
                  >
                    {job.status === 'PAUSED' ? <Play className="h-3.5 w-3.5 mr-1" /> : <Pause className="h-3.5 w-3.5 mr-1" />}
                    {job.status === 'PAUSED' ? 'Resume' : 'Pause'}
                  </Button>

                  <Button size="sm" onClick={() => triggerRun.mutate(job.job_id)} disabled={triggerRun.isPending}>
                    <Play className="h-3.5 w-3.5 mr-1" /> Run Scan Now
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Parser Inspector Panel ────────────────────────────────────────── */}
      <ParserInspectorPanel />

      {/* ── Evidence Archive Inspector ────────────────────────────────────── */}
      <ArchiveInspector />

      {/* ── Change Detection Real-Time Feed ──────────────────────────────── */}
      {events.length > 0 && (
        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-3">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">Real-Time Telemetry & Change Detection Log</h3>
          <div className="space-y-2">
            {events.map((evt) => (
              <div
                key={evt.event_id}
                className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-xs flex items-center justify-between gap-3"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <Activity className="h-4 w-4 text-violet-500 shrink-0" />
                  <div className="truncate">
                    <span className="font-bold text-slate-900 dark:text-white">{evt.product_name}</span>
                    <span className="text-slate-500 ml-2">({evt.marketplace}) — {evt.details}</span>
                  </div>
                </div>
                <span className="text-[10px] font-mono text-slate-400 shrink-0">{new Date(evt.timestamp).toLocaleTimeString()}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

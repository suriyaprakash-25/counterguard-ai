/**
 * IntelligenceLifecycleDashboard.tsx — Phase 3: Intelligence Lifecycle Dashboard Component
 * Visualizes the 8-stage autonomous closed-loop feedback pipeline, evolution metrics (knowledge, threat, entity, risk), and live execution telemetry.
 */
import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { RefreshCw, CheckCircle2, Cpu, Database, Network, ShieldAlert, Sparkles, FileText, Bell, Layers, ArrowRight } from 'lucide-react';
import { apiClient, endpoints } from '../../../shared/api';

export interface PipelineStage {
  stage_number: number;
  stage_name: string;
  status: string;
  details: string;
  duration_ms: number;
}

export interface TelemetryData {
  execution_id: string;
  case_id: string;
  product_name: string;
  status: string;
  total_duration_ms: number;
  stages: PipelineStage[];
  knowledge_nodes_added: number;
  vector_precedents_created: number;
  syndicates_updated: number;
  new_threat_score: number;
  recommendations_count: number;
  report_id: string;
  alerts_triggered: number;
}

export function IntelligenceLifecycleDashboard() {
  const queryClient = useQueryClient();

  const { data, isLoading } = useQuery<TelemetryData>({
    queryKey: ['closedLoopTelemetry'],
    queryFn: async () => {
      const resp = await apiClient.get(`${endpoints.closedLoop.telemetry}?case_id=INV-8901`);
      return resp.data;
    },
  });

  const triggerMutation = useMutation({
    mutationFn: async () => {
      const resp = await apiClient.post(`${endpoints.closedLoop.trigger}`, {
        case_id: 'INV-8901',
        product_name: 'CMF Buds 2a',
      });
      return resp.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['closedLoopTelemetry'] });
    },
  });

  if (isLoading || !data) return null;

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-5 mb-6 text-slate-900 dark:text-slate-100">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-100 dark:border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <RefreshCw className="h-5 w-5 text-violet-600 dark:text-violet-400" />
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
              Autonomous Closed-Loop Intelligence Lifecycle Dashboard
            </h3>
            <p className="text-[11px] text-slate-500">Self-evolving feedback loop propagating completed case intelligence across 8 stages</p>
          </div>
        </div>

        <button
          onClick={() => triggerMutation.mutate()}
          disabled={triggerMutation.isPending}
          className="px-3.5 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm shrink-0 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${triggerMutation.isPending ? 'animate-spin' : ''}`} />
          {triggerMutation.isPending ? 'Running Pipeline...' : 'Trigger Closed-Loop Cycle'}
        </button>
      </div>

      {/* Evolution Tracking Metrics Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-[10px] uppercase font-bold tracking-wider">
            <span>Knowledge Evolution</span>
            <Network className="h-3.5 w-3.5 text-blue-500" />
          </div>
          <div className="text-lg font-black text-slate-900 dark:text-white">+{data.knowledge_nodes_added} Graph Nodes</div>
          <div className="text-[10px] text-slate-500">Neo4j graph topology expanded</div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-[10px] uppercase font-bold tracking-wider">
            <span>Threat Evolution</span>
            <ShieldAlert className="h-3.5 w-3.5 text-red-500" />
          </div>
          <div className="text-lg font-black text-red-600 dark:text-red-400">{data.new_threat_score} CRITICAL</div>
          <div className="text-[10px] text-slate-500">Hierarchical score updated</div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-[10px] uppercase font-bold tracking-wider">
            <span>Entity Evolution</span>
            <Database className="h-3.5 w-3.5 text-violet-500" />
          </div>
          <div className="text-lg font-black text-slate-900 dark:text-white">+{data.vector_precedents_created} Precedents</div>
          <div className="text-[10px] text-slate-500">ChromaDB memory enriched</div>
        </div>

        <div className="p-3.5 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
          <div className="flex items-center justify-between text-slate-500 text-[10px] uppercase font-bold tracking-wider">
            <span>Risk Evolution</span>
            <Sparkles className="h-3.5 w-3.5 text-emerald-500" />
          </div>
          <div className="text-lg font-black text-slate-900 dark:text-white">{data.recommendations_count} Recs Dispatched</div>
          <div className="text-[10px] text-slate-500">Report {data.report_id} generated</div>
        </div>
      </div>

      {/* 8-Stage Pipeline Stepper Visualizer */}
      <div className="space-y-2">
        <div className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
          8-Stage Closed-Loop Pipeline Runtime ({data.total_duration_ms}ms)
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-2.5">
          {data.stages.map((st) => (
            <div
              key={st.stage_number}
              className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-violet-600 dark:text-violet-400 text-[10px]">
                  STAGE {st.stage_number}
                </span>
                <span className="px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300 font-mono text-[9px] font-bold flex items-center gap-1">
                  <CheckCircle2 className="h-2.5 w-2.5" /> {st.duration_ms}ms
                </span>
              </div>
              <div className="font-bold text-slate-900 dark:text-white text-xs">{st.stage_name}</div>
              <p className="text-[10px] text-slate-500 line-clamp-2">{st.details}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

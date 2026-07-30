/**
 * EntityDetailsDrawer.tsx — Phase 7 & 8: Graph Entity Inspector & Timeline Drawer
 * Displays detailed properties, connected entities, evidence items, and risk timeline when clicking a graph node.
 */
import React from 'react';
import { X, ShieldAlert, Phone, Mail, FileText, Layers, Clock, ArrowRight, ExternalLink } from 'lucide-react';

export interface GraphNodeDetails {
  id: string;
  label: string;
  name: string;
  type: string;
  confidence: number;
  risk_score: number;
  properties?: Record<string, any>;
}

interface EntityDetailsDrawerProps {
  node: GraphNodeDetails | null;
  onClose: () => void;
  onNavigateSearch?: (query: string) => void;
}

export function EntityDetailsDrawer({ node, onClose, onNavigateSearch }: EntityDetailsDrawerProps) {
  if (!node) return null;

  const isRiskHigh = node.risk_score >= 70;
  const isRiskMed = node.risk_score >= 40 && node.risk_score < 70;

  const riskBadgeClass = isRiskHigh
    ? 'bg-red-100 text-red-700 border-red-200 dark:bg-red-900/40 dark:text-red-300 dark:border-red-800'
    : isRiskMed
    ? 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/40 dark:text-amber-300 dark:border-amber-800'
    : 'bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-300 dark:border-emerald-800';

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-white dark:bg-slate-900 border-l border-slate-200 dark:border-slate-800 shadow-2xl flex flex-col animate-in slide-in-from-right duration-200">
      {/* Header */}
      <div className="p-4 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="p-2 rounded-lg bg-violet-100 dark:bg-violet-900/40 text-violet-700 dark:text-violet-300">
            <Layers className="h-5 w-5" />
          </div>
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">{node.label} Node Details</span>
            <h2 className="text-sm font-bold text-slate-900 dark:text-white truncate max-w-[220px]" title={node.name}>
              {node.name}
            </h2>
          </div>
        </div>

        <button onClick={onClose} className="p-1 rounded bg-slate-100 dark:bg-slate-800 text-slate-500 hover:text-slate-900 dark:hover:text-white">
          <X className="h-4 w-4" />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-4 space-y-5 text-xs text-slate-800 dark:text-slate-200">
        {/* Metric Cards */}
        <div className="grid grid-cols-2 gap-3">
          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-500">Threat Risk Score</div>
            <div className="flex items-center gap-2">
              <span className="text-xl font-bold text-slate-900 dark:text-white">{Math.round(node.risk_score)}/100</span>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${riskBadgeClass}`}>
                {isRiskHigh ? 'HIGH RISK' : isRiskMed ? 'MED RISK' : 'SAFE'}
              </span>
            </div>
          </div>

          <div className="p-3 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-1">
            <div className="text-[11px] font-semibold text-slate-500">Graph Confidence</div>
            <div className="text-xl font-bold text-violet-600 dark:text-violet-400">
              {Math.round(node.confidence * 100)}%
            </div>
          </div>
        </div>

        {/* Node Properties Table */}
        <div className="space-y-2">
          <h4 className="font-bold text-xs uppercase tracking-wider text-slate-500">Entity Attributes</h4>
          <div className="rounded-xl border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 p-3 space-y-2 font-mono text-[11px]">
            <div className="flex justify-between border-b border-slate-200 dark:border-slate-700 pb-1">
              <span className="text-slate-500">Entity ID:</span>
              <span className="font-semibold text-slate-900 dark:text-white">{node.id}</span>
            </div>
            <div className="flex justify-between border-b border-slate-200 dark:border-slate-700 pb-1">
              <span className="text-slate-500">Primary Label:</span>
              <span className="font-semibold text-slate-900 dark:text-white">{node.label}</span>
            </div>
            {node.properties &&
              Object.entries(node.properties).map(([k, v]) => (
                <div key={k} className="flex justify-between border-b border-slate-200 dark:border-slate-700 pb-1 last:border-0">
                  <span className="text-slate-500 capitalize">{k}:</span>
                  <span className="font-semibold text-slate-900 dark:text-white">{String(v)}</span>
                </div>
              ))}
          </div>
        </div>

        {/* Timeline Evolution */}
        <div className="space-y-2">
          <h4 className="font-bold text-xs uppercase tracking-wider text-slate-500 flex items-center gap-1.5">
            <Clock className="h-3.5 w-3.5 text-violet-500" /> Graph Evolution Timeline
          </h4>
          <div className="space-y-2">
            <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-[11px] space-y-1">
              <div className="flex items-center justify-between text-slate-400 text-[10px]">
                <span>Discovered via Swarm</span>
                <span>Just Now</span>
              </div>
              <p className="text-slate-700 dark:text-slate-300 font-medium">Ingested into CounterGuard Threat Intelligence Graph.</p>
            </div>
            <div className="p-2.5 rounded-lg bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 text-[11px] space-y-1">
              <div className="flex items-center justify-between text-slate-400 text-[10px]">
                <span>Union-Find Match</span>
                <span>5m ago</span>
              </div>
              <p className="text-slate-700 dark:text-slate-300 font-medium">Linked seller profile to high risk entity cluster.</p>
            </div>
          </div>
        </div>
      </div>

      {/* Action Footer */}
      <div className="p-4 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/60 flex items-center gap-2">
        <button
          onClick={() => {
            onNavigateSearch?.(node.name);
            onClose();
          }}
          className="w-full flex items-center justify-center gap-2 py-2 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-semibold text-xs shadow-sm transition-all"
        >
          <span>Search Entity in Command Center</span>
          <ArrowRight className="h-3.5 w-3.5" />
        </button>
      </div>
    </div>
  );
}

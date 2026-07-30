/**
 * ThreatScoreBreakdown.tsx — Hierarchical Intelligence Threat Score Breakdown Component
 * Renders 8-level entity threat scores, weighted factor contributions, and step-by-step explainability logs.
 */
import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { ShieldAlert, BarChart3, Layers, CheckCircle2, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { apiClient, endpoints } from '../../../shared/api';

export interface FactorContribution {
  factor_name: string;
  weight_pct: number;
  raw_score: number;
  weighted_score: number;
  description: string;
}

export interface EntityThreatScore {
  entity_id: string;
  entity_type: string;
  entity_name: string;
  threat_score: number;
  threat_level: string;
  confidence: number;
  factor_contributions: FactorContribution[];
  reasoning: string[];
}

export interface HierarchicalScoreResponse {
  overall_organization_risk: number;
  hierarchy_scores: Record<string, EntityThreatScore>;
}

export function ThreatScoreBreakdown() {
  const [expandedLevel, setExpandedLevel] = useState<string | null>('Listing');

  const { data, isLoading } = useQuery<HierarchicalScoreResponse>({
    queryKey: ['scoring', 'hierarchical'],
    queryFn: async () => {
      const resp = await apiClient.get(`${endpoints.scoring.hierarchical}`);
      return resp.data;
    },
  });

  if (isLoading || !data) return null;

  const levels = Object.keys(data.hierarchy_scores);

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4 mb-6">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-5 w-5 text-violet-600 dark:text-violet-400" />
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
              Hierarchical Intelligence Threat Score Matrix (8 Entity Levels)
            </h3>
            <p className="text-[11px] text-slate-500">Deterministic, explainable threat scoring model</p>
          </div>
        </div>
        <span className="text-xs font-bold text-red-600 dark:text-red-400 px-3 py-1 bg-red-50 dark:bg-red-950 rounded-full border border-red-200 dark:border-red-800">
          Org Threat Index: {data.overall_organization_risk}/100
        </span>
      </div>

      {/* Grid of 8 Hierarchy Levels */}
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-8 gap-2">
        {levels.map((lvl) => {
          const item = data.hierarchy_scores[lvl];
          const isSelected = expandedLevel === lvl;
          const isCrit = item.threat_level === 'CRITICAL';
          const isHigh = item.threat_level === 'HIGH';

          return (
            <button
              key={lvl}
              onClick={() => setExpandedLevel(isSelected ? null : lvl)}
              className={`p-3 rounded-xl border text-left transition-all flex flex-col justify-between ${
                isSelected
                  ? 'bg-violet-50 dark:bg-slate-800 border-violet-500 shadow-sm'
                  : 'bg-slate-50 dark:bg-slate-800/40 border-slate-200 dark:border-slate-800 hover:border-slate-300'
              }`}
            >
              <div className="text-[10px] font-bold uppercase text-slate-500">{lvl}</div>
              <div className="text-base font-bold text-slate-900 dark:text-white my-1">{Math.round(item.threat_score)}/100</div>
              <span
                className={`text-[9px] font-bold px-1.5 py-0.5 rounded text-center ${
                  isCrit ? 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300' : isHigh ? 'bg-amber-100 text-amber-700' : 'bg-emerald-100 text-emerald-700'
                }`}
              >
                {item.threat_level}
              </span>
            </button>
          );
        })}
      </div>

      {/* Expanded Factor Breakdown & Explainability Logs */}
      {expandedLevel && data.hierarchy_scores[expandedLevel] && (
        <div className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-4 animate-in fade-in duration-150">
          <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-700 pb-2">
            <h4 className="text-xs font-bold text-slate-900 dark:text-white uppercase tracking-wider">
              {expandedLevel} Level Score Breakdown: {data.hierarchy_scores[expandedLevel].entity_name}
            </h4>
            <span className="text-xs font-mono text-slate-500">Confidence: {Math.round(data.hierarchy_scores[expandedLevel].confidence * 100)}%</span>
          </div>

          {/* Factor Contribution Progress Bars */}
          <div className="space-y-2">
            <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Weighted Factor Contributions</div>
            {data.hierarchy_scores[expandedLevel].factor_contributions.map((fc) => (
              <div key={fc.factor_name} className="space-y-1 text-xs">
                <div className="flex justify-between text-slate-700 dark:text-slate-300 font-medium">
                  <span>{fc.factor_name} ({fc.weight_pct}% weight)</span>
                  <span className="font-mono text-violet-600 dark:text-violet-400">+{fc.weighted_score} pts</span>
                </div>
                <div className="w-full bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-violet-600 h-full rounded-full" style={{ width: `${fc.raw_score}%` }} />
                </div>
                <div className="text-[10px] text-slate-400">{fc.description}</div>
              </div>
            ))}
          </div>

          {/* Explainable Reasoning Checklist */}
          <div className="space-y-2 pt-2 border-t border-slate-200 dark:border-slate-700">
            <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider">Explainability Reasoning Log</div>
            <div className="space-y-1.5">
              {data.hierarchy_scores[expandedLevel].reasoning.map((r, i) => (
                <div key={i} className="flex items-start gap-2 text-xs text-slate-700 dark:text-slate-300">
                  <CheckCircle2 className="h-3.5 w-3.5 text-emerald-500 shrink-0 mt-0.5" />
                  <span>{r}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

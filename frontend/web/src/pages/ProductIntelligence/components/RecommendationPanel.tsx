/**
 * RecommendationPanel.tsx — Phase 3: AI Prescriptive Recommendation Panel Component
 * Displays actionable prescriptive recommendation cards, explainability logs, and one-click case creation / enforcement triggers.
 */
import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Sparkles, ShieldCheck, AlertTriangle, ArrowRight, CheckCircle2, Gavel, Scale, FolderPlus, Info } from 'lucide-react';
import { apiClient, endpoints } from '../../../shared/api';

export interface PrescriptiveRecommendation {
  recommendation_id: string;
  action_type: string;
  title: string;
  confidence: number;
  urgency: string;
  reasoning: string[];
  supporting_evidence: string[];
  supporting_graph_entities: string[];
  historical_precedents: string[];
}

export interface PrescriptiveResponse {
  target_product: string;
  overall_confidence: number;
  recommendations: PrescriptiveRecommendation[];
}

export function RecommendationPanel({ query = 'CMF Buds 2a' }: { query?: string }) {
  const queryClient = useQueryClient();
  const [executedIds, setExecutedIds] = useState<Record<string, string>>({});

  const { data, isLoading } = useQuery<PrescriptiveResponse>({
    queryKey: ['recommendations', query],
    queryFn: async () => {
      const resp = await apiClient.get(`${endpoints.recommendations.prescriptive}?target_query=${encodeURIComponent(query)}`);
      return resp.data;
    },
  });

  const executeMutation = useMutation({
    mutationFn: async ({ recId, action }: { recId: string; action: string }) => {
      const resp = await apiClient.post(`${endpoints.recommendations.execute}`, {
        recommendation_id: recId,
        action_type: action,
      });
      return resp.data;
    },
    onSuccess: (data, vars) => {
      setExecutedIds((prev) => ({ ...prev, [vars.recId]: data.case_id || 'DISPATCHED' }));
    },
  });

  if (isLoading || !data) return null;

  const getActionBadge = (action: string) => {
    switch (action) {
      case 'INVESTIGATE_IMMEDIATELY':
        return { label: 'Investigate Immediately', bg: 'bg-red-100 text-red-700 dark:bg-red-950 dark:text-red-300' };
      case 'ISSUE_TAKEDOWN':
        return { label: 'Marketplace Takedown', bg: 'bg-violet-100 text-violet-700 dark:bg-violet-950 dark:text-violet-300' };
      case 'ESCALATE_LEGAL':
        return { label: 'Escalate to Legal', bg: 'bg-amber-100 text-amber-700 dark:bg-amber-950 dark:text-amber-300' };
      case 'MERGE_CASE':
        return { label: 'Merge Case', bg: 'bg-blue-100 text-blue-700 dark:bg-blue-950 dark:text-blue-300' };
      default:
        return { label: action, bg: 'bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300' };
    }
  };

  return (
    <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-5 shadow-sm space-y-4 mb-6">
      <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="h-5 w-5 text-violet-600 dark:text-violet-400" />
          <div>
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-900 dark:text-white">
              AI Prescriptive Next-Action Recommendations
            </h3>
            <p className="text-[11px] text-slate-500">Deterministic, explainable action recommendations & one-click execution</p>
          </div>
        </div>
        <span className="text-xs font-bold text-violet-600 dark:text-violet-400 px-3 py-1 bg-violet-50 dark:bg-violet-950 rounded-full border border-violet-200 dark:border-violet-800">
          AI Confidence: {data.overall_confidence}%
        </span>
      </div>

      {/* Action Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.recommendations.map((rec) => {
          const badge = getActionBadge(rec.action_type);
          const isExecuted = !!executedIds[rec.recommendation_id];

          return (
            <div
              key={rec.recommendation_id}
              className="p-4 rounded-xl bg-slate-50 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-800 space-y-3 text-xs flex flex-col justify-between"
            >
              <div className="space-y-2">
                <div className="flex items-start justify-between gap-2">
                  <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold ${badge.bg}`}>
                    {badge.label}
                  </span>
                  <span className="text-[10px] font-mono font-bold text-slate-500">{rec.confidence}% Match</span>
                </div>

                <div className="font-bold text-slate-900 dark:text-white text-sm">{rec.title}</div>

                {/* Explainable Reasoning */}
                <div className="space-y-1 pt-1 border-t border-slate-200 dark:border-slate-700">
                  <div className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Deterministic Reasoning</div>
                  {rec.reasoning.map((r, i) => (
                    <div key={i} className="flex items-start gap-1.5 text-[11px] text-slate-600 dark:text-slate-300">
                      <CheckCircle2 className="h-3 w-3 text-emerald-500 shrink-0 mt-0.5" />
                      <span>{r}</span>
                    </div>
                  ))}
                </div>

                {/* Graph & Precedent Badges */}
                <div className="flex flex-wrap items-center gap-1.5 pt-1">
                  {rec.supporting_graph_entities.map((g, i) => (
                    <span key={i} className="px-2 py-0.5 rounded text-[9px] font-mono bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300">
                      {g}
                    </span>
                  ))}
                </div>
              </div>

              {/* One-Click Execution Button */}
              <div className="pt-2 border-t border-slate-200 dark:border-slate-700 flex justify-end">
                {isExecuted ? (
                  <span className="px-3 py-1.5 rounded-lg bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-300 text-xs font-bold flex items-center gap-1">
                    <CheckCircle2 className="h-3.5 w-3.5" /> Action Executed ({executedIds[rec.recommendation_id]})
                  </span>
                ) : (
                  <button
                    onClick={() => executeMutation.mutate({ recId: rec.recommendation_id, action: rec.action_type })}
                    className="px-3 py-1.5 rounded-lg bg-violet-600 hover:bg-violet-700 text-white text-xs font-semibold flex items-center gap-1.5 transition-all shadow-sm"
                  >
                    Execute Action <ArrowRight className="h-3.5 w-3.5" />
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
